"""Pick ~200 XFinBench test calculation items as seeds for controllable rewriting.

Usage: python3 -I scripts/select_xfinbench.py RAW_DIR OUT_DIR
RAW_DIR holds test_set.csv from https://huggingface.co/datasets/Zhihan/XFinBench (MIT).
"""
import csv
import collections
import json
import random
import re
import sys

QUOTA = {  # capability label -> target count (sums to 200)
    'TR': 50, 'NM': 45, 'SP': 30, 'SP; TR': 20, 'NM; SP': 15,
    'NM; TR': 15, 'FF': 15, 'TU': 10,
}
REF = re.compile(r'\b(previous|preceding|above|earlier|part \(|problem \d|question \d|refer to|the following table|exhibit|figure|table \d|example \d)\b', re.I)
LATEX = re.compile(r'\\begin|\\textbf|tabular|\\hline|\\\\')
NUM = re.compile(r'(?<![A-Za-z_])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?|\.\d+)\s*(percent|%|million|billion|thousand)?', re.I)
SCALE = {'million': 1e6, 'billion': 1e9, 'thousand': 1e3}


def numbers(q):
    out = []
    for m in NUM.finditer(q):
        v = float(m.group(1).replace(',', ''))
        unit = (m.group(2) or '').lower()
        out.append(v)
        if unit in SCALE:
            out.append(v * SCALE[unit])
        if unit in ('percent', '%'):
            out.append(v / 100)
    return out


def topic(q):
    t = q.lower()
    if re.search(r'option|futures|forward|swap|strike|volatility|binomial|black-scholes|hedg|delta|gamma', t):
        return 'derivatives'
    if re.search(r'federal reserve|\bfed\b|money supply|reserve requirement|monetary base|deposits?\b|central bank|money multiplier|discount loan', t):
        return 'money_banking'
    return 'corporate_finance'


def main(raw_dir, out_dir):
    rows = list(csv.DictReader(open(f'{raw_dir}/test_set.csv', encoding='utf-8-sig')))
    reasons = collections.Counter()
    pool = []
    for r in rows:
        q = r['question'].strip()
        if r['task'] != 'calcu':
            reasons['not calculation task'] += 1; continue
        if r['figure'].strip() or LATEX.search(q):
            reasons['figure or table'] += 1; continue
        if not 120 <= len(q) <= 700:
            reasons['too short or too long'] += 1; continue
        if '(Unit' not in q:
            reasons['no unit hint'] += 1; continue
        if REF.search(q):
            reasons['refers to other text'] += 1; continue
        try:
            gt = float(r['ground_truth'])
        except ValueError:
            reasons['non-numeric answer'] += 1; continue
        nums = numbers(q.split('(Unit')[0])
        if len(set(nums)) < 2:
            reasons['fewer than 2 parameters'] += 1; continue
        if any(abs(gt - v) <= 0.005 * max(abs(gt), 1e-9) for v in nums):
            reasons['answer equals a given number'] += 1; continue
        pool.append(dict(r, id=r['id'], question=q, gt=gt, n_params=len(set(nums)), topic=topic(q)))
    # one item per shared textbook context (XFinBench splits one exercise into several items)
    random.seed(20261121)
    random.shuffle(pool)
    seen, dedup = set(), []
    for r in pool:
        key = re.sub(r'\W+', ' ', r['question'][:90].lower())
        if key in seen:
            reasons['same exercise as a kept item'] += 1; continue
        seen.add(key); dedup.append(r)
    by_cap = collections.defaultdict(list)
    for r in dedup:
        by_cap[r['fin_capability']].append(r)
    picked = []
    for cap, k in QUOTA.items():
        picked += by_cap[cap][:k]
    short = 200 - len(picked)  # top up from the largest groups if a quota could not be met
    rest = [r for cap in ('TR', 'NM') for r in by_cap[cap][QUOTA[cap]:]]
    picked += rest[:max(short, 0)]
    picked.sort(key=lambda r: int(r['id'].split('_')[1]))
    with open(f'{out_dir}/seeds_200.jsonl', 'w') as f:
        for r in picked:
            f.write(json.dumps({k: r[k] for k in ('id', 'question', 'ground_truth', 'fin_capability',
                                                  'gold_fin_term_id', 'topic', 'n_params')}, ensure_ascii=False) + '\n')
    with open(f'{out_dir}/seeds_200.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'fin_capability', 'topic', 'question', 'ground_truth'])
        for r in picked:
            w.writerow([r['id'], r['fin_capability'], r['topic'], r['question'], r['ground_truth']])
    stats = {
        'test_rows': len(rows), 'eligible_before_dedup': len(pool), 'eligible_after_dedup': len(dedup),
        'excluded': dict(reasons), 'available_by_capability': {c: len(v) for c, v in by_cap.items()},
        'picked': len(picked),
        'picked_by_capability': dict(collections.Counter(r['fin_capability'] for r in picked)),
        'picked_by_topic': dict(collections.Counter(r['topic'] for r in picked)),
    }
    json.dump(stats, open(f'{out_dir}/selection_stats.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(stats, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
