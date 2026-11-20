"""Print a compact view of step0/runs/*.json (for reviewing the agent trajectories)."""
import json, glob, os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'step0', 'runs')
for p in sorted(glob.glob(os.path.join(root, '*.json'))):
    t = json.load(open(p, encoding='utf-8'))
    if len(sys.argv) > 1 and t['qid'] not in sys.argv[1:]: continue
    print(f"\n================ {t['qid']}  [{t['final_status']}]")
    ev = t['step1_learn_pattern']['evidence_in_seed_context']
    print('  ① located in seed context:', ', '.join(f"{k}->{('p'+v[0]['page']+' '+v[0]['row_label'][:28]) if v else 'NOT FOUND'}" for k, v in ev.items()))
    for r in t['step2_backtest']['inputs']:
        extra = f"  ⇒ seed value matches {r['diagnosis_seed_value_matches_concept']}" if 'diagnosis_seed_value_matches_concept' in r else ''
        print(f"  ② input {r['key']:<16} seed={r['seed_stated']} xbrl={r['xbrl']} [{r['status']}]{extra}")
    for r in t['step2_backtest']['answers']:
        if r.get('seed_answer') is None:
            print(f"  ② metric {r['metric']:<22} (no seed answer) filing={r['recomputed_from_filing']}")
        else:
            print(f"  ② metric {r['metric']:<22} seed={r['seed_answer']:<8} from_seed_inputs={r['recomputed_from_seed_inputs'] if r['recomputed_from_seed_inputs'] is None else round(r['recomputed_from_seed_inputs'],4)} arith_ok={r['arithmetic_ok']} filing_ok={r['filing_ok']} corrected={r['corrected_seed_answer']}")
    pl = t['step3_plan']
    print(f"  ③ decision={pl['decision']}  target={pl.get('target_filing',{}).get('form')} {pl.get('target_filing',{}).get('period')} filed {pl.get('target_filing',{}).get('filed')}")
    if 'availability' in pl: print('    availability:', pl['availability'])
    if 'step4_compute' in t:
        print('  ④', {k: (round(v['value'], 4) if v['value'] is not None else v['missing']) for k, v in t['step4_compute']['metrics'].items()})
        print('  ⑤ answer:', t['step5_question']['answer'])
        r6 = t['step6_review']
        print('  ⑥ text check:', ', '.join(f"{c['key']}={c['value_as_text']}{'✓' if c['found_in_filing_text'] else '✗'}" for c in r6['text_verification']), '| leak:', r6['answer_leak_in_question'], '| auto_pass:', r6['automatic_checks_pass'])
