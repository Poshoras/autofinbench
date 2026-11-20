import csv, sys, collections
csv.field_size_limit(10**9)
p = sys.argv[1]
with open(p, encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
print("rows:", len(rows))
print("cols:", list(rows[0].keys()))
print("question_type:", collections.Counter(r['question_type'] for r in rows))
print("unique accession:", len(set(r['accession_number'] for r in rows)))
print("items:", collections.Counter(r['item'].split('.')[0].strip() for r in rows).most_common(10))
lens = [len(r['context_markdown_with_headers']) for r in rows]
print("ctx md len min/median/max:", min(lens), sorted(lens)[len(lens)//2], max(lens))
# company/fiscal year from context first line
fy = collections.Counter()
for r in rows:
    first = r['context_markdown_with_headers'].split('\n',1)[0]
    fy[first.split(', page')[0][:90]] += 1
print("filings (by context header):")
for k,v in fy.most_common(60): print(f"  {v:3d}  {k}")
print("\n=== all QIDs + questions ===")
for r in rows:
    print(r['QID'], '|', r['Question'].replace('\n',' ')[:160])
