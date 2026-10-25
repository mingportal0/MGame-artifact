"""문서 구조/참조 검사 전용. 게임 구현·플레이 시뮬레이션 아님."""
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

root = Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
p = root / '06.md'
s = p.read_text()
checks = []
def check(name, passed, detail):
    checks.append({'name': name, 'passed': bool(passed), 'detail': detail})

classes = re.findall(r'^\| (?:정령소환사|용조련사|동물조련사|악마소환사|네크로멘서) / (CLS_\w+) \|', s, re.M)
summon_section = s.split('### 5.1 소환수 ID 예약표')[1].split('### 5.2')[0]
summons = [line.split('|')[1:-1] for line in summon_section.splitlines() if re.match(r'^\| SUM_', line)]
upgrade_section = s.split('### 5.2 업그레이드 참조 예시')[1].split('## 6.')[0]
upgrades = [line.split('|')[1:-1] for line in upgrade_section.splitlines() if re.match(r'^\| UPG_', line)]
summon_ids = [row[0].strip() for row in summons]
upgrade_ids = [row[0].strip().split(' / ')[0] for row in upgrades]
ids = classes + summon_ids + upgrade_ids
check('five_class_comparison', len(classes) == 5 and len(set(classes)) == 5, classes)
check('comparison_columns', all(len(line.split('|')[1:-1]) == 7 for line in s.splitlines() if re.match(r'^\| (?:정령소환사|용조련사|동물조련사|악마소환사|네크로멘서) / CLS_', line)), '콘셉트/기제/선택/장점/단점/비용 열 검사')
check('id_unique_format', len(ids) == len(set(ids)) and all(re.fullmatch(r'[A-Z][A-Z0-9_]+', x) for x in ids), {'total': len(ids)})
counts = {c: sum(row[1].strip() == c for row in summons) for c in classes}
check('representative_summons_per_class', all(v == 2 for v in counts.values()), counts)
check('starter_one_per_class', all(sum(row[1].strip() == c and 'starter 1' in row[2] for row in summons) == 1 for c in classes), '초기 1종·1마리, 나머지는 후보')
check('summon_unlock_links', all(all(u in upgrade_ids for u in re.findall(r'UPG_[A-Z0-9_]+', '|'.join(row))) for row in summons), '소환수 예시가 가리킨 업그레이드 존재')
check('upgrade_columns', all(len(row) == 7 for row in upgrades), {'upgrade_examples': len(upgrades)})
check('upgrade_targets_resolve', all(all(x in summon_ids for x in re.findall(r'SUM_[A-Z0-9_]+', row[2])) for row in upgrades), '효과 대상 소환수 참조')
check('upgrade_class_scope', all(row[1].strip().split(' / ')[1] in classes + ['ALL'] for row in upgrades), '적용 직업 참조')
check('finite_levels', all(re.fullmatch(r'\d+(?:\(가정\))?', row[3].strip()) and int(re.match(r'\d+', row[3].strip()).group()) > 0 for row in upgrades), '반복·단발 모두 유한 최대 레벨')
edges = {u: re.findall(r'(UPG_[A-Z0-9_]+):\d+', row[4]) for u, row in zip(upgrade_ids, upgrades)}
def visit(u, trail):
    if u in trail or u not in edges:
        return False
    return all(visit(v, trail + [u]) for v in edges[u])
check('prerequisites_resolve_acyclic', all(visit(u, []) for u in edges), edges)
check('scope_explicit', all(row[-1].strip() in ['mvp_candidate', 'expansion_candidate'] for row in summons + upgrades), '전 행 MVP/확장 구분')
fields = ['id / name', 'category', 'applies_to', 'effects', 'max_level', 'cost', 'unlock_condition', 'prerequisites', 'visual_change', 'type']
schema = s.split('### 4.4 Upgrade')[1].split('### 4.5')[0]
check('upgrade_required_fields_and_type', all(f in schema for f in fields), fields)
check('g1_rules_documented', all(x in s for x in ['골드 드랍 시 즉시 자동 수집', '30초 고정', '재도전 보스 HP 초기화', '무한 성장·환생 제외', '범위 밖 자동 공격', '공격 지정 반경(command_radius)']), 'G1 제약 존재 검사; 의미 정합성은 별도 자체 검토')
check('no_obsolete_example_upgrades', not any(re.search(r'COLLECT|GOLD_RADIUS|TURN_TIME|AUTO_COLLECT|PRESTIGE', x) for x in upgrade_ids), upgrade_ids)
check('test_and_approval_limits_explicit', all(x in s for x in ['실제 사용자 테스트 미수행', 'G3 개발 미승인', 'Mia 검토 질문(대기)', 'Sam 검토 질문(대기)', '### 7.2 가장 싼 검증 계획 — 미수행']), '검증/승인 한계 명시 여부; 사실 여부를 자동 입증하는 검사는 아님')
check('change_trace_present', '## 8. 원문 대비 변경·요구 추적표' in s and 'L139~147' in s, '원문 수량과 이번 대표 예시 범위 차이 명시')
links = re.findall(r'\]\(([^)]+)\)', s)
missing = [x for x in links if not x.startswith(('http:', 'https:')) and x != '06-validation.json' and not (root / x).exists()]
check('local_source_links', not missing, {'links': links, 'missing': missing})
report = {'document': str(p), 'checked_at': datetime.now(ZoneInfo('Asia/Seoul')).isoformat(), 'kind': 'document_structure_and_reference_only', 'checks': checks, 'passed': sum(x['passed'] for x in checks), 'total': len(checks), 'all_passed': all(x['passed'] for x in checks), 'not_performed': ['실제 플레이테스트', 'Mia UX 검토', 'Sam 기술 검토', '성능 실측', '직업 경제 밸런스 검증', '대표 세부 사양 승인']}
out = root / '06-validation.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report['all_passed'] else 1)
