import csv, sys, re, statistics
csv.field_size_limit(10**9)
rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig', newline='')))
gl = [len(r['ground_truth_answer']) for r in rows]
print("GT len min/median/max:", min(gl), statistics.median(gl), max(gl))
# questions lacking an explicit company name
names = ['apple','p&g','procter','nike','discover','dfs','nvidia','halliburton','goldman','jpmorgan','honeywell','exxon','coca','tesla','nee','nextera']
noent = [r['QID'] for r in rows if not any(n in r['Question'].lower() for n in names)]
print("no company in question:", len(noent), noent)
for q in sys.argv[2:]:
    r = next(x for x in rows if x['QID']==q)
    print(f"\n===== {q}: {r['Question'].strip()}\n[filing ctx] {r['context_markdown_with_headers'].split(chr(10),1)[0]}\n--- GT ---\n{r['ground_truth_answer'][:900]}")
