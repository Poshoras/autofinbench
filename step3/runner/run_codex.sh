#!/bin/bash
# usage: run_codex.sh QID REV
Q=$1; REV=$2; WS=~/didigou/autofinbench/codex_ws; OUT=~/didigou/autofinbench/step3_runs
PROMPT="You are the solver in a finance agent benchmark. Read step3/README.md, then the question step3/questions/$Q.md (revision $REV) and the files in step3/env/$Q/. Use ONLY the files in step3/env/$Q/ as your information source: no internet, no other directories, no prior knowledge of actual reported figures. You may run Python/shell commands to analyse the files. When done, output ONLY the final answer in Markdown: first line 'Question: $Q, Revision: $REV', then essential reasoning, then end with exactly one fenced json block in the schema the question requires."
timeout 1200 codex exec -C "$WS" -s read-only --skip-git-repo-check --json -o "$OUT/$Q.r$REV.last.md" "$PROMPT" > "$OUT/$Q.r$REV.events.jsonl" 2> "$OUT/$Q.r$REV.stderr"
echo "$Q exit=$?"
