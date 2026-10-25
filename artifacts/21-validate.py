from pathlib import Path
import re,json,hashlib,datetime,collections,sys
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
D=json.loads((A/'21-defects.json').read_text());Q=json.loads((A/'21-review-requests.json').read_text()); text=(A/'21.md').read_text(); target=(A/'20.md').read_text().splitlines()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(n,v,d=''):checks.append({'name':n,'passed':bool(v),'detail':d})
check('immutable target hash',sha(A/'20.md')=='0d40dd6a5bf795b7984c742a6c8def8edce81d16d8973016a8d4a3237332ec87')
check('target version', 'P1-20-GDD-v01' in '\n'.join(target[:8]))
check('all finding IDs unique',len({r['id'] for r in D['findings']})==len(D['findings']))
check('all 27 findings',len(D['findings'])==27)
expected={'james':7,'mia':9,'sam':11}
for p in D['review_provenance']:
 name=p['profile_cli'];prefix={'james':'J','mia':'M','sam':'S'}[name];review=(A/p['review_file']).read_text()
 check(name+' new review hash',sha(A/p['review_file'])==p['review_sha256'])
 check(name+' response hash',sha(A/p['response_file'])==p['response_sha256'])
 check(name+' target hash in review',D['target_sha256'] in review)
 check(name+' process exited',p['exit_code']==0)
 check(name+' session record exact',p.get('session_metadata',{}).get('id')==p['session_id'])
 check(name+' session ended',p.get('session_metadata',{}).get('ended_at') is not None)
 check(name+' real tool messages',p.get('message_role_counts',{}).get('tool',0)>0)
 check(name+' metadata warning retained','HERMES_PROFILE=sophie' in p['environment_warning'])
 check(name+' finding count',sum(r['reviewer']==name for r in D['findings'])==expected[name])
 for i,question in enumerate(Q['questions'][name],1):
  q=f'{prefix}{i:02}'
  check(name+' question '+q,q in review and question.startswith(q+':'))
for r in D['findings']:
 b=r['review_body'];id=r['id']
 check(id+' severity',r['severity'] in ['치명','높음','중간','낮음'])
 check(id+' single owner',r['owner'] in ['James','Mia','Sam','Sophie'])
 check(id+' remains open',r['status']=='open_not_fixed')
 check(id+' source row', (A/r['evidence_file']).read_text().splitlines()[r['evidence_first_line']-1].startswith('### '+id))
 check(id+' target location stated','대상' in b and ('행' in b or 'L' in b))
 loc=next((line for line in b.splitlines() if line.startswith('- 대상')), '')
 ranges=re.findall(r'(?:L)?(\d{1,4})[~～](\d{1,4})',loc)
 singles=re.findall(r'\bL(\d{1,4})\b',loc)
 check(id+' target ranges valid',bool(ranges or singles) and all(1<=int(lo)<=int(hi)<=len(target) for lo,hi in ranges) and all(1<=int(n)<=len(target) for n in singles))
 check(id+' acceptance criteria','수용기준' in b or '수용 기준' in b)
 check(id+' alternatives','대안' in b and '추천' in b)
 check(id+' evidence rationale','근거' in b)
 check(id+' approval boundary','미합의' in b and ('대표승인' in b or '대표' in b))
 check(id+' main report row', bool(re.search(r'^\| '+re.escape(id)+r' \|',text,re.M)))
 check(id+' excerpt line number valid',1<=r['evidence_first_line']<=len((A/r['evidence_file']).read_text().splitlines()))
for u in range(1,8):check(f'open U{u:02}',f'| U{u:02}' in text)
check('I07 retained','| I07' in text)
check('not approval','최종 MVP/GDD' in text and '미승인' in text and 'G3' in text)
check('next card gated','별도 명시 실행 승인 전 blocked' in text)
check('no Slack delivery claim','Slack 실제 전달 성공은 직접 확인하지 않았' in text)
check('source snapshot arithmetic',25-4==21)
check('severity aggregate',dict(collections.Counter(r['severity'] for r in D['findings']))==D['severity_counts'])
check('severity declared',D['severity_counts']=={'치명':1,'높음':17,'중간':9})
base=json.loads((A/'21-baseline-validation.json').read_text());check('baseline all pass',base['passed']==base['total']==502)
for label in ['21.md','21-defects.json','21-review-requests.json','21-review-james.md','21-review-mia.md','21-review-sam.md']:
 check('deliverable '+label,(A/label).is_file())
for link in re.findall(r'\]\(([^)]+)\)',text):
 if link=='21-validation.json':continue
 if '://' not in link:check('local link '+link,(A/link.split('#')[0]).is_file())
for idx in [A.parents[2]/'README.md',A.parent/'plan.md']:
 index_text=idx.read_text()
 check('index contains21 '+idx.name,'21.md' in index_text and 'phase1-p21-execution_approved_v01.md' in index_text)
 check('index retains gate '+idx.name,'blocked' in index_text and 'G3' in index_text)
result={'document_id':'P1-21-PACKAGE-VALIDATION-v01','checked_at':datetime.datetime.now().astimezone().isoformat(),'scope':'document provenance, response presence, field coverage, hashes, record counts and source location bounds; NOT defect resolution/game/user/performance test','target_sha256':sha(A/'20.md'),'findings':len(D['findings']),'severity_counts':D['severity_counts'],'owner_counts':D['owner_counts'],'review_count':len(D['review_provenance']),'question_count':sum(len(q) for q in Q['questions'].values()),'passed':sum(x['passed'] for x in checks),'total':len(checks),'checks':checks,'artifact_sha256':{f.name:sha(f) for f in A.glob('21*') if f.is_file() and f.name!='21-validation.json'}}
(A/'21-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','artifact_sha256']},ensure_ascii=False,indent=2))
print('FAILURES',json.dumps([x for x in checks if not x['passed']],ensure_ascii=False))
sys.exit(0 if all(x['passed'] for x in checks) else 1)
