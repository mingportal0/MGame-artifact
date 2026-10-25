"""Document checks only; no game code or prototype."""
import json
import re
from pathlib import Path
p = Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts/07.md')
s = p.read_text()
rows = [line.split('|')[1:-1] for line in s.splitlines() if line.startswith('| UPG_ELM_')]
u = {r[0].strip(): r for r in rows}
summons = re.findall(r'^\| (SUM_ELM_\w+) /', s, re.M)
checks = {
    'five_unique_summons': len(summons) == len(set(summons)) == 5,
    'at_least_ten_exclusive_upgrades': len(rows) >= 10,
    'unique_upgrade_ids': len(rows) == len(u),
    'all_table_fields_present': all(len(r) == 8 and all(c.strip() for c in r) for r in rows),
    'common_required_fields': all(x in s for x in ['category=summon', 'applies_to=CLS_ELM', 'unlock_condition=run_start', 'currency:gold', 'growth_rule:null', 'rounding:null']),
    'four_upgrade_types': {r[2].strip() for r in rows} == {'repeat', 'unlock', 'evolve', 'synergy'},
}
pr = {k: re.findall(r'(UPG_ELM_\w+):(\d+)', r[5]) for k, r in u.items()}
checks['valid_prerequisites'] = all(a in u and 0 < int(b) <= int(u[a][4]) for v in pr.values() for a, b in v)
seen = set()
while True:
    nxt = {k for k, v in pr.items() if all(a in seen for a, b in v)} - seen
    if not nxt:
        break
    seen |= nxt
checks['all_reachable_no_cycle'] = len(seen) == len(u)
builds = {}
for name in ['A', 'B']:
    text = s.split('### 빌드 ' + name + ':')[1].split('### ')[0]
    line = next(x for x in text.splitlines() if x.startswith('구매 경로'))
    path = re.findall(r'UPG_ELM_\w+', line)
    levels = {}
    errors = []
    for k in path:
        if k not in u:
            errors.append(k)
            continue
        if not all(levels.get(a, 0) >= int(b) for a, b in pr[k]):
            errors.append('prerequisite:' + k)
        levels[k] = levels.get(k, 0) + 1
        if levels[k] > int(u[k][4]):
            errors.append('cap:' + k)
    builds[name] = {'path': path, 'levels': levels, 'errors': errors}
    checks['build_' + name + '_legal'] = not errors
checks['reserved_ids_preserved'] = all(x in s for x in ['SUM_ELM_EMBER', 'SUM_ELM_SPARK', 'UPG_ELM_BLOOM', 'UPG_ELM_SPARK'])
checks['evolution_upgrade_references'] = all('UPG_ELM_' + x in u for x in ['BLOOM', 'SPARK_ARC', 'TIDE_WAVE', 'STONE_MONOLITH', 'PRISM_CROWN'])
checks['ten_trace_rows'] = len(re.findall(r'^\| R\d\d ', s, re.M)) == 10
checks['eight_boundary_cases'] = len(re.findall(r'^\| E\d\d ', s, re.M)) == 8
arithmetic = {'ember_A_damage': 10 + 2 * 3 + 3, 'ember_A_radius': 60 + 10 * 2, 'spark_B_cd': round(1.4 - 0.1 * 2, 2), 'spark_B_interval': round(0.2 + 1.4 - 0.1 * 2, 2), 'bloom_three': 10 * 3, 'spark_four': 7 * 4, 'gold': 3 + 4}
checks['example_arithmetic'] = arithmetic == {'ember_A_damage': 19, 'ember_A_radius': 80, 'spark_B_cd': 1.2, 'spark_B_interval': 1.4, 'bloom_three': 30, 'spark_four': 28, 'gold': 7}
report = {'scope': '문서 구조·참조·선행 DAG·빌드 경로·예시 산술만', 'counts': {'summons': len(summons), 'exclusive_upgrades': len(rows), 'builds': len(builds)}, 'checks': checks, 'passed': sum(checks.values()), 'total': len(checks), 'builds': builds, 'arithmetic': arithmetic, 'not_performed': ['게임 실행/기능 테스트', '실제 사용자 테스트', 'Mia/Sam 전문 검토', '경제/가격/소요시간 검증', '성능 실측', 'Slack 전달 확인']}
print(json.dumps(report, ensure_ascii=False, indent=2))
Path('07-validation-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
if not all(checks.values()):
    raise SystemExit(1)
