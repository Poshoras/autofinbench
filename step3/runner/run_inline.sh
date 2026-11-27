#!/bin/bash
# usage: run_inline.sh QID REV  -> codex answers with env files inlined (no tools; host sandbox unavailable)
Q=$1; REV=$2; K=${3:+.k$3}; WS=~/didigou/autofinbench/codex_ws; OUT=~/didigou/autofinbench/step3_runs
P="$OUT/$Q.r$REV$K.prompt.txt"
{
echo "You are the solver in a finance agent benchmark. You have NO tools in this run: every file of the environment is included below. Use ONLY these files as your information source (no prior knowledge of actual reported figures). Work carefully; do arithmetic step by step."
echo "Output ONLY the final answer in Markdown: first line 'Question: $Q, Revision: $REV', then essential reasoning, then end with exactly one fenced json block in the schema the question requires."
echo; echo "===== FILE: step3/README.md ====="; cat $WS/step3/README.md
echo; echo "===== FILE: step3/questions/$Q.md ====="; cat $WS/step3/questions/$Q.md
for f in $WS/step3/env/$Q/*; do echo; echo "===== FILE: step3/env/$Q/$(basename $f) ====="; cat "$f"; done
} > "$P"
timeout 1500 codex exec -C "$WS" -s read-only -c approval_policy='"never"' --skip-git-repo-check --json -o "$OUT/$Q.r$REV$K.last.md" - < "$P" > "$OUT/$Q.r$REV$K.events.jsonl" 2> "$OUT/$Q.r$REV$K.stderr"
echo "$Q exit=$? $(date +%H:%M)"
