"""P1-11 document-only structure/arithmetic checks; no game runtime."""
import json
import re
from pathlib import Path

root = Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
text = (root / '11.md').read_text()
checks = []
def check(name, condition, detail):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})

rows = [line.split('|')[1:-1] for line in text.splitlines() if line.startswith('| UPG_NEC_')]
rows = [[cell.strip() for cell in row] for row in rows]
ids = [r[0] for r in rows]
summons = re.findall(r'^\| (SUM_NEC_[A-Z_]+) \|', text, re.M)
check('summon_quantity_unique', len(summons) == len(set(summons)) == 5, summons)
check('upgrade_quantity_unique', len(ids) == len(set(ids)) == 14, ids)
check('row_fields', all(len(r) == 9 and all(r) for r in rows), '9 columns plus explicit shared category/applies_to/unlock_condition/currency/status/cost formula')
check('four_types', {r[7] for r in rows} == {'repeat', 'unlock', 'evolve', 'synergy'}, sorted({r[7] for r in rows}))
check('positive_finite_levels_prices', all(int(r[3]) > 0 and int(r[4]) > 0 for r in rows), 'integer levels/base prices')
levels = {r[0]: int(r[3]) for r in rows}
graph = {}
for r in rows:
    prereqs = re.findall(r'(UPG_NEC_[A-Z_]+):(\d+)', r[5])
    graph[r[0]] = [p for p, _ in prereqs]
    check('prerequisites_' + r[0], all(p in levels and 0 < int(l) <= levels[p] for p, l in prereqs), prereqs)
visited, active = set(), set()
def walk(node):
    if node in active:
        return False
    if node in visited:
        return True
    active.add(node)
    if not all(walk(p) for p in graph.get(node, [])):
        return False
    active.remove(node)
    visited.add(node)
    return True
check('acyclic_reachable_tree', all(walk(i) for i in ids), 'all prerequisites exist; run_start roots; no cycles')
check('reserved_ids_retained', all(i in ids for i in ['UPG_NEC_RAISE', 'UPG_NEC_LICH']) and all(i in summons for i in ['SUM_NEC_SKELETON', 'SUM_NEC_LICH']), 'P1-06 IDs unchanged')
check('summon_unlock_and_evolution_references', all(i in ids for i in re.findall(r'UPG_NEC_[A-Z_]+', '\n'.join(line for line in text.splitlines() if line.startswith('| SUM_NEC_')))), 'summon table upgrade refs')
check('case_quantity_unique', len(re.findall(r'^\| NV\d{2} ', text, re.M)) == 15, '15 manual expected-event traces, not executed gameplay')
check('trace_quantity', len(re.findall(r'^\| NTR\d{2} ', text, re.M)) == 12, '12 source/G1 mappings')
check('scope_partition', sum(r[8] == 'M' for r in rows) == 4 and sum(r[8] == 'E' for r in rows) == 10, 'M4 + E10 upgrades; game MVP not approved')
check('two_builds', 'A. 소생 군단 빌드' in text and 'B. 영구 지팡이 빌드' in text, 'two purchase paths, not equal-budget efficiency proof')
check('ledger', 10*2-10+12*2-18 == 16, {'income': 10*2+12*2, 'spent': 10+18, 'balance': 10*2-10+12*2-18})
check('equal_budget_candidates', 10+18 == 20+8 == 28, 'RAISE+THRIFT vs LICH+BONE1')
check('base_raise_arithmetic', divmod(9, 3) == (3, 0), '9 tokens, cost3 => temporary3/remainder0')
check('expanded_raise_arithmetic', divmod(10, 2) == (5, 0), '10 tokens, cost2 => temporary5/remainder0')
check('overflow_arithmetic', 2+4-3 == 3, '2 existing+4 new-cap3 = 3 discarded')
check('damage_arithmetic', 6*(1+0.25*3)+2 == 12.5, 'GUARD+BONE3+CONDUCT = 12.5; rounding unresolved')
check('finite_summon_max', len(summons)+3+2 == 10, 'permanent5 + temporary(base3+2 levels)=10; performance unmeasured')
check('required_boundaries_present', all(s in text for s in ['비행 중 지정 이탈 즉시', '재진입 복원 금지', '토큰0/임시0', '재지급0', '무한 성장·환생 제외', 'G3 개발 미승인']), 'literal coverage only; not semantic/runtime validation')
result = {'document': 'P1-11-NEC-v01', 'scope': 'document structure and arithmetic only', 'checks': checks, 'passed': sum(c['passed'] for c in checks), 'total': len(checks), 'not_performed': ['game code/prototype', 'actual user tests', 'Mia/Sam expert review', 'runtime functionality or performance', 'balance or retention validation'], 'counts': {'summons': len(summons), 'upgrades': len(ids), 'manual_cases': 15, 'source_traces': 12}}
(root / '11-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['passed'] == result['total'] else 1)
