"""P1-16 document-only checks; not game code or UX execution."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parent
text = (root / '16.md').read_text()
catalog = json.loads((root / '12-catalog.json').read_text())
records = {r['id']: r for r in catalog['upgrades']}
checks = []
def check(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})

for prefix, count in [('UI', 10), ('V', 19), ('TR', 12)]:
    ids = re.findall(r'^\| (' + prefix + r'\d{2}) \|', text, re.M)
    expected = [f'{prefix}{i:02}' for i in range(1, count + 1)]
    check(prefix + ' unique ordered rows', ids == expected)
for screen in ['W01', 'W02', 'W02-C', 'W03', 'W03-S', 'W04', 'W05']:
    check('wireframe ' + screen, bool(re.search(r'^### ' + re.escape(screen) + r' ', text, re.M)))
for section in range(1, 11):
    check('section ' + str(section), bool(re.search(r'^## ' + str(section) + r'\.', text, re.M)))
for prefix, count in [('J', 4), ('S', 5)]:
    ids = re.findall(r'^- (' + prefix + r'\d{2}):', text, re.M)
    check(prefix + ' question rows', ids == [f'{prefix}{i:02}' for i in range(1, count + 1)])
responses = re.findall(r'^\| (A(?:05|12|13)-\d) /', text, re.M)
check('Mia upstream responses', len(responses) == 10 and len(set(responses)) == 10)
links = re.findall(r'\]\(([^)]+)\)', text)
check('all local source links exist', all((root / link.split('#')[0]).exists() for link in links))
refs = set(re.findall(r'\bUPG_[A-Z_]+\b', text))
check('exact referenced upgrade IDs exist', len(refs) == 6 and refs <= records.keys())
check('BLOOM assumed base price 20', records['UPG_ELM_BLOOM']['cost']['base'] == 20)
check('SPARK assumed base price 25', records['UPG_ELM_SPARK']['cost']['base'] == 25)
ledger = [0, 0 + 24, 24 - 20, 4 + 0, 4 + 0, 4 + 0]
check('example ledger ending 4', ledger == [0, 24, 4, 4, 4, 4])
gold = {str(g): [int(g * (1 + .25 * l)) for l in (0, 1)] for g in (1, 3, 6)}
check('assumed floor rewards L0 L1', gold == {'1': [1, 1], '3': [3, 3], '6': [6, 7]})
check('affordability example', 25 - 24 == 1 and 24 - 20 == 4)
check('no CJK mixed-script typo', re.search(r'[\u4e00-\u9fff]', text) is None)
for label in ['텍스트 와이어프레임', '실제 사용자', 'G3', '응답은 아직 없음', 'R_cmd', 'R_reach', 'R_fx', '미수집/손실/수집률원장은없다']:
    check('required boundary text ' + label, label in text)
report = {
    'document_id': 'P1-16-UX-v01',
    'scope': '문서 구조/로컬 링크/명시 ID/가격 예시/가정 산술만 자동 검사. 의미 검토는 Mia 수기 워크스루. 게임 실행/렌더/실제 사용자/성능 검증 아님.',
    'checks': checks,
    'passed': sum(c['passed'] for c in checks),
    'total': len(checks),
    'manual_cases': 19,
    'ui_rows': 10,
    'change_rows': 12,
    'upstream_response_rows': len(responses),
    'peer_review_status': {'James': '질문 게시, 응답 대기', 'Sam': '질문 게시, 응답 대기'},
    'arithmetic': {'ledger': ledger, 'L0_L1_gold_by_base': gold, 'shortfall': 25 - 24},
    'sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ['16.md', '05.md', '12.md', '12-catalog.json', '13.md']},
    'not_performed': ['게임 코드/프로토타입/프로젝트 초기화', 'UI 렌더링/클릭 기능 테스트', '사용자 접촉/플레이테스트', '성능/접근성 실측', 'James/Sam 동의 확인', 'Slack 전달 확인'],
}
(root / '16-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'total': report['total'], 'failed': [c['name'] for c in checks if not c['passed']], 'ledger': ledger, 'floor_examples': gold}, ensure_ascii=False))
raise SystemExit(0 if report['passed'] == report['total'] else 1)
