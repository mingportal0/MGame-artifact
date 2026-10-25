"""P1-19 document-only structural audit; not a game/test simulator."""
from pathlib import Path
import hashlib
import json
import re

base = Path(__file__).resolve().parent
text = (base / '19.md').read_text(encoding='utf-8')
source_path = base.parent / 'source.txt'
source = source_path.read_text(encoding='utf-8').splitlines()
checks = []
def check(name, ok, detail):
    checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

sections = re.findall(r'^### R(\d{2}) ([^\n]+)\n(.*?)(?=^### R|^## 3\.)', text, re.M | re.S)
check('ten_unique_risks', [x[0] for x in sections] == [f'{n:02d}' for n in range(1,11)], [x[0] for x in sections])
fields = ['원문', '원인', '플레이 영향', '가능성', '심각도', '예방', '구현비용', '권고책', '책임자', '근거', '검증·종결조건', '잔여위험']
for i, title, body in sections:
    line = 466 + int(i)
    original = source[line-1].removeprefix('- ').strip()
    check('R'+i+'_source_title', title == original, {'line':line, 'title':title, 'source':original})
    check('R'+i+'_all_fields', all('- '+f+':' in body for f in fields), fields)
    check('R'+i+'_source_line', f'source L{line}' in body, line)
    check('R'+i+'_specialist_citation', bool(re.search(r'(James|Mia|Sam)\d{2}', body)), 'named existing document citation')
    check('R'+i+'_downstream_action', '20' in body and ('21' in body or '22' in body), '20 and review route')

top = re.findall(r'^\| TOP(\d) \|', text, re.M)
check('top5_exact', top == ['1','2','3','4','5'], top)
for name, pattern, expected in [('unresolved7',r'^\| U(\d{2}) ',7),('change12',r'^\| C(\d{2}) ',12),('decisions5',r'^\| D(\d{2}) ',5)]:
    found=re.findall(pattern,text,re.M)
    check(name,len(found)==expected and len(set(found))==expected, found)
links = re.findall(r'\]\(([^)]+)\)', text)
for link in sorted(set(links)):
    if not re.match(r'https?://',link):
        # The validation record is written at the end of this audit.
        check('local_link:'+link, link=='19-validation.json' or (base/link.split('#')[0]).exists(), link)
check('G1_boundary', all(s in text for s in ['D01 범위','G3 개발 미승인','참가자 접촉','HP300도 현재 적정성 보류','고정틱과 엄격 연속이탈은 동의어 아님']), 'approval and non-measurement disclaimers')
check('required_critical_review', all(s in text for s in ['강점','가장 중요한 약점','유사성 판단의 경계','고난도 요소']), 'source Part9 topics')
check('reduced_not_full_damage', 'ELM478.4/1080.3/1271.4를 축소 전력으로 복사 금지' in text, 'full/reduced distinction')
index_path = base.parents[2] / 'README.md'
index_text = index_path.read_text(encoding='utf-8')
index_links = re.findall(r'\]\(([^)]+)\)', index_text)
check('index_links_exist', all((index_path.parent / link.split('#')[0]).exists() for link in index_links if not re.match(r'https?://', link)), index_links)
check('index_15_to_19', all(f'artifacts/{n}.md' in index_text for n in range(15,20)), '15-19 document index present')
inputs = [index_path, source_path, base/'02.md', base/'15.md', base/'16.md', base/'17.md', base/'18.md', base.parents[2]/'decisions/2026-10-25_phase1-g1_approved_v01.md']
fingerprints={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs+[base/'19.md',Path(__file__).resolve()]}
result={'document_id':'P1-19-RISK-v01','scope':'Document structure, exact source risk headings, field presence, links and fingerprints only; no semantic expert approval, arithmetic balance recalculation, game, UX, performance or user tests.', 'risk_count':len(sections),'risk_field_count':len(fields),'top5_count':len(top),'passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,'sha256':fingerprints,'unresolved':['reduced MVP damage and natural economy unverified','U01-U07 peer followup pending','art effort and representative quality undefined','MVP/GDD/G3 and participant contact unapproved'],'not_performed':['game code/prototype/project initialization','reduced combat arithmetic','peer assent collection','user/performance/accessibility tests','paid work/publication/contact','Slack delivery verification']}
output=base/'19-validation.json'
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':result['passed'],'total':result['total'],'risk_count':len(sections),'top5_count':len(top),'record':str(output),'failed':[c for c in checks if not c['passed']]},ensure_ascii=False,indent=2))
raise SystemExit(0 if result['passed']==result['total'] else 1)
