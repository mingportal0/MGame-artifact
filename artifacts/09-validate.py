"""P1-09 Markdown structure/reference/arithmetic checks only; not game code."""
import json
import re
from pathlib import Path

base = Path(__file__).resolve().parent
text = (base / '09.md').read_text()
checks = []
def check(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})

def rows(prefix):
    return [[v.strip() for v in line.strip().strip('|').split('|')]
            for line in text.splitlines() if line.startswith('| ' + prefix)]

summons = rows('SUM_BST_')
upgrades = rows('UPG_BST_')
sids = [r[0] for r in summons]
uids = [r[0] for r in upgrades]
check('basic1_plus_additional4', len(summons) == 5 and sum('starter' in r[1] for r in summons) == 1 and sum('unlock' in r[1] for r in summons) == 4)
check('upgrade_minimum10', len(upgrades) >= 10)
check('unique_ids', len(set(sids + uids)) == len(sids + uids))
check('id_format', all(re.fullmatch(r'[A-Z0-9_]+', x) for x in sids + uids))
check('summon_attack_evolution_fields', all(len(r) == 6 and all(r) and 'BASE' in r[3] for r in summons))
check('upgrade_10fields_plus_type', all(len(r) == 11 and all(r) for r in upgrades))
check('category_class_type', all(r[2] == 'summon' and r[3] == 'CLS_BST' and r[10] in {'repeat', 'unlock', 'evolve', 'synergy'} for r in upgrades))
check('four_types', {r[10] for r in upgrades} == {'repeat', 'unlock', 'evolve', 'synergy'})
check('positive_finite_levels_cost', all(int(r[5]) > 0 and int(r[6].split('/')[0]) > 0 for r in upgrades))
records = {r[0]: r for r in upgrades}
deps = {r[0]: re.findall(r'(UPG_BST_[A-Z_]+):(\d+)', r[8]) for r in upgrades}
check('prerequisite_refs_levels', all(d in records and 0 < int(level) <= int(records[d][5]) for items in deps.values() for d, level in items))
reachable = set()
while True:
    nxt = {u for u, items in deps.items() if all(d in reachable for d, _ in items)}
    if nxt <= reachable:
        break
    reachable |= nxt
check('no_cycles_all_reachable', len(reachable) == len(upgrades))
check('summon_unlock_refs', all(all(u in records for u in re.findall(r'UPG_BST_[A-Z_]+', r[1])) for r in summons))
check('evolution_refs', all(all(u in records for u in re.findall(r'UPG_BST_[A-Z_]+', r[3])) for r in summons))
check('all_bst_upgrade_references_defined', set(re.findall(r'UPG_BST_[A-Z_]+', text)) == set(uids))
check('reserved_06_ids_preserved', {'SUM_BST_WOLF', 'SUM_BST_HAWK'} <= set(sids) and {'UPG_BST_PACK', 'UPG_BST_HAWK'} <= set(uids))
check('builds2', len(re.findall(r'^### B-BST-', text, re.M)) == 2)
check('manual_cases10', len(rows('C0')) + len(rows('C10')) == 10)
check('trace11', len(rows('TR-BST-')) == 11)
check('g1_boundaries', all(s in text for s in ['즉시 기본 자동 수집', '30초 고정', '시간 증가 보류', '재도전 보스 HP 초기화', '무한 성장·환생 제외', '즉시 무효', '재진입해도 복원하지 않는다']))
check('mvp_expansion_approval_labels', all(s in text for s in ['expansion_candidate', 'MVP', 'G3', '미해결', '실제 사용자 테스트']))
links = re.findall(r'\]\(([^)]+)\)', text)
source_links = [s for s in links if s not in {'09-validation.json', '09-validate.py'}]
check('local_source_links_exist', all((base / p).exists() for p in source_links))

ledger = rows('일반전') + rows('상점') + rows('보스 실패')
check('ledger_arithmetic', all(int(r[1]) + int(r[2]) - int(r[3]) == int(r[4]) for r in ledger))
ordered_ledger = [r for r in [[v.strip() for v in line.strip().strip('|').split('|')] for line in text.splitlines() if line.startswith('| ')] if len(r) == 6 and r[0] in {'일반전1','상점1','일반전2','상점2','보스 실패·재도전'}]
check('ledger_continuity', len(ordered_ledger) == 5 and all(int(a[4]) == int(b[1]) for a,b in zip(ordered_ledger, ordered_ledger[1:])))

def cost(uid, level=0):
    return int(records[uid][6].split('/')[0]) * (1 + level)
pack_path = [('UPG_BST_PACK',0),('UPG_BST_PACK',1),('UPG_BST_WOLF_LEADER',0),('UPG_BST_FANG',0),('UPG_BST_CROWN',0)]
mix_path = [('UPG_BST_HAWK',0),('UPG_BST_BOAR',0),('UPG_BST_HAWK_TWIN',0),('UPG_BST_BOAR_TUSK',0),('UPG_BST_SKY_GROUND',0)]
check('crown_no_other_species_required', deps['UPG_BST_CROWN'] == [('UPG_BST_WOLF_LEADER','1')] and deps['UPG_BST_WOLF_LEADER'] == [])
max_count = sum([3,2,2,1,1])
check('finite_roster_cap9', max_count == 9 and 'permanent_cap=9, temporary_cap=0' in text)
result = {
    'document': 'P1-09-BST-v01',
    'scope': '문서 구조·ID·참조·선행 도달성·산술만, 게임/사용자/UX/성능 검증 아님',
    'counts': {'summons': len(summons), 'upgrades': len(upgrades), 'builds': 2, 'manual_document_cases': 10, 'change_traces': 11},
    'arithmetic': {'permanent_cap': max_count, 'pack_build_total_gold_assumed': sum(cost(u,l) for u,l in pack_path), 'mixed_build_total_gold_assumed': sum(cost(u,l) for u,l in mix_path), 'pack_build_units':3, 'mixed_build_units':sum([1,2,2]), 'ledger_income':sum(int(r[2]) for r in ordered_ledger), 'ledger_spend':sum(int(r[3]) for r in ordered_ledger), 'ledger_final':int(ordered_ledger[-1][4])},
    'passed': sum(c['passed'] for c in checks), 'total': len(checks), 'checks': checks,
    'not_performed': ['게임 코드/프로토타입', '실제 사용자 테스트', 'Mia UX 검토', 'Sam 기술 검토', '성능 실측', '빌드 균형 실측', 'Slack 전달 확인']
}
(base / '09-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
