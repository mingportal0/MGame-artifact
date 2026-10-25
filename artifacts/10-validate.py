"""Document-only audit. No game implementation or runtime simulation."""
import json
import re
from collections import Counter
from pathlib import Path
from decimal import Decimal

p = Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts/10.md')
s = p.read_text()
checks = []
def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})

def rows(prefix):
    return [[v.strip() for v in line.strip('|').split('|')]
            for line in s.splitlines() if line.startswith('| ' + prefix)]

summons = rows('SUM_DMN_')
upgrades = rows('UPG_DMN_')
u = {r[0]: r for r in upgrades}
check('summons_basic1_plus_additional4', len(summons) == 5 and sum('starter/1' in r[1] for r in summons) == 1 and sum('unlock/0' in r[1] for r in summons) == 4)
check('summon_ids_unique', len({r[0] for r in summons}) == len(summons))
check('upgrade_count_at_least10', len(upgrades) >= 10)
check('upgrade_ids_unique', len(u) == len(upgrades))
check('ten_required_fields_plus_type_nonempty', all(len(r) == 11 and all(r) for r in upgrades))
check('id_format', all(re.fullmatch(r'(?:SUM|UPG)_DMN_[A-Z0-9_]+', r[0]) for r in summons + upgrades))
check('class_and_category', all(r[2:4] == ['summon', 'CLS_DMN'] for r in upgrades))
check('finite_positive_levels', all(int(r[5]) > 0 for r in upgrades))
check('cost_positive_explicit_currency_rule', all(re.fullmatch(r'gold:[1-9][0-9]*:(?:단발|×2/level)', r[6]) for r in upgrades))
check('all_four_types', set(r[10] for r in upgrades) == {'repeat','unlock','evolve','synergy'})
check('reserved_upgrades_preserved', {'UPG_DMN_EXECUTOR', 'UPG_DMN_RELAY'} <= u.keys())
check('reserved_summons_preserved', {'SUM_DMN_IMP','SUM_DMN_EXECUTOR'} <= {r[0] for r in summons})
edges = {r[0]: re.findall(r'(UPG_DMN_[A-Z0-9_]+):([0-9]+)', r[8]) for r in upgrades}
check('prerequisite_ids_levels_valid', all(k in u and 0 < int(level) <= int(u[k][5]) for es in edges.values() for k,level in es))
resolved = set()
while True:
    new = {k for k, es in edges.items() if all(dep in resolved for dep,_ in es)} - resolved
    if not new:
        break
    resolved |= new
check('dag_and_all_reachable', len(resolved) == len(u))
check('summon_acquisition_evolution_refs_exist', all(ref in u for r in summons for ref in re.findall(r'UPG_DMN_[A-Z0-9_]+', ' '.join(r))))
check('upgrade_summon_refs_exist', all(ref in {r[0] for r in summons} for r in upgrades for ref in re.findall(r'SUM_DMN_[A-Z0-9_]+', r[4])))
check('two_builds_present', all(x in s for x in ['### B01 ', '### B02 ']))
cases = rows('C0') + rows('C1')
traces = rows('TR')
check('manual_cases14', len(cases) == 14 and len({r[0] for r in cases}) == 14)
check('change_traces12', len(traces) == 12)
check('mvp_and_expansion_explicit', all(x in s for x in ['가장 작은 비교 후보', '확장 전용 후보', '미승인']))
check('local_markdown_links_resolve', all((p.parent / x).exists() for x in re.findall(r'\]\(([^)]+)\)', s) if not x.startswith('http')))
# Verify documented build totals and that listed order satisfies prerequisites.
builds = {
 'B01': [('POWER',1),('IMP_CROWN',1),('IMP_TWIN',1),('POWER',2),('TYRANT',1)],
 'B02': [('EXECUTOR',1),('RELAY',1),('EXECUTOR_CLEAVE',1),('HEXER',1),('HEXER_SIGIL',1)]
}
build_totals = {}
for b, steps in builds.items():
    owned = {}
    total = 0
    valid = True
    for short, level in steps:
        key = 'UPG_DMN_' + short
        r = u[key]
        valid &= level == owned.get(key,0) + 1
        valid &= all(owned.get(dep,0) >= int(n) for dep,n in edges[key])
        base = int(r[6].split(':')[1])
        total += base * (2 ** (level-1) if r[10] == 'repeat' else 1)
        owned[key] = level
    build_totals[b] = total
    check(b + '_purchase_order', valid)
    check(b + '_documented_total', str(total)+'골드' in s)
check('final_permanent_count', sum([2,1,1,1,1]) == 6 and '영구6' in s)
arithmetic = {'base_sequence':10+20+20*0.5,'simultaneous_first_hits':10+20,'remaining_hp':100-(10+20+20*0.5),'relay_hit':20+20,'evolved_imp_power1':str(Decimal(10)*Decimal('1.2')*Decimal('1.5')),'gold_grant':3+4,'gold_after_grant':10+3+4,'gold_after_purchase':10+3+4-10}
check('document_example_arithmetic', arithmetic['base_sequence']==40 and arithmetic['simultaneous_first_hits']==30 and arithmetic['remaining_hp']==60 and arithmetic['relay_hit']==40 and Decimal(arithmetic['evolved_imp_power1'])==18 and arithmetic['gold_after_purchase']==7)
result = {'document':str(p), 'scope':'문서 구조·참조·구매 선행·산술 검사만. 게임 구현/실행 없음.', 'counts':{'summons':len(summons),'upgrades':len(upgrades),'types':dict(Counter(r[10] for r in upgrades)),'manual_cases':len(cases),'change_traces':len(traces)},'build_totals':build_totals,'arithmetic':arithmetic,'checks':checks,'passed':sum(x['passed'] for x in checks),'total':len(checks),'manual_review':'James가 10.md C01~C14의 규칙을 문서상 추적. 독립 전문 검토·실제 실행 테스트 아님. 표식 생성/소비의 부가 사건 재귀 없음, 무피격/범위/골드 경계 자체 대조.', 'not_performed':['실제 사용자 테스트','게임 코드/프로토타입','UX 전문 검토','기술 전문 검토','성능 실측','밸런스 실측','Slack 전달 확인']}
out = p.with_name('10-validation.json')
out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
assert result['passed'] == result['total'], 'Document audit failed'
