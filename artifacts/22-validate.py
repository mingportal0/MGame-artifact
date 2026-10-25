"""Document/provenance and independent conditional-arithmetic audit only."""
from pathlib import Path
from fractions import Fraction as F
import json,re,csv,hashlib,collections,sys
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
checks=[]
def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
def load(n):return json.loads((A/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return re.sub(r'\s+','',t)
t=(A/'22.md').read_text();h=sha(A/'22.md');src=(A/'../source.txt').read_text().splitlines()
manifest=load('22-manifest.json')
for n,d in manifest['preserved_baseline'].items():check('preserve '+n,sha(A/n)==d)
for i in range(1,11):check('part '+str(i),len(re.findall(r'^## Part '+str(i)+r'\.',t,re.M))==1 and f'id="p{i}"' in t)
check('review not approved', '상태: review' in t and 'G3 개발 미승인' in t and '대표 승인자·승인일: 없음' in t)
check('no template placeholders','{{' not in t)
for needle in ['즉시 기본 자동 수집','공격 지정 R_cmd','무한 성장·환생 제외','재도전 HP초기화','시간 증가 보류','P1-23은별도실행승인전blocked','총비용미산정']:
 check('scope '+needle,needle in t)
for u in re.findall(r'\]\(([^)]+)\)',t):
 if not u.startswith(('http','#')):check('link '+u,(A/u.split('#')[0]).exists())
old={r['id']:r for r in load('20-trace.json')};trace=load('22-trace.json')
check('trace unique and399',len(trace)==399==len({r['id'] for r in trace}) and set(old)=={r['id'] for r in trace})
for r in trace:
 o=old[r['id']]
 check('trace text/source '+r['id'],r['source']==o['source'] and norm(r['source'])==norm(src[r['line']-1]))
 check('trace scope '+r['id'],r['gdd_anchor']==f"22.md#p{r['gdd_part']}" and r['disposition']==o['disposition'])
subitems=[(i,l[2:].strip()) for i,l in enumerate(src,1) if 495<=i<=563 and l.startswith('- ')]
check('required50',len(subitems)==50)
for i,s in subitems:
 check('subitem '+str(i),any(r['line']==i and norm(s) in norm(r['source']) for r in trace))
original=load('21-defects.json')['findings'];res=load('22-resolutions.json')
check('resolution target',res['target_sha256']==h)
check('27 one-to-one',len(res['findings'])==27 and {r['id'] for r in res['findings']}=={r['id'] for r in original})
for r in res['findings']:
 check('fields '+r['id'],all(r.get(k) for k in ['disposition','reason','location','reverification','remaining','responsible_response']))
 rr=r['responsible_response'];check('response target '+r['id'],bool(rr) and rr.get('target_sha256')==h)
 check('location '+r['id'],all(1<=int(i)<=len(t.splitlines()) for i in re.findall(r'\d+',r['location'].split(' L')[-1])))
for p,n in [('mia',9),('sam',11)]:
 review=load(f'22-review-{p}.json');check('review target '+p,review['target_sha256']==h)
 check('review IDs '+p,len(review['findings'])==n and {r['id'] for r in review['findings']}=={r['id'] for r in original if r['reviewer']==p})
for p in load('22-review-index.json')['reviews']:
 check('actual session '+p['profile'],p['verified_session'] and p['exit_code']==0 and p['session_metadata']['ended_at'] is not None)
 for name,d in p['hashes'].items():check('review hash '+name,sha(A/name)==d)
b=load('22-balance.json');inp=b['inputs'];check('roster source',sha(A/'14-inputs.json')==inp['source_14_sha256'])
check('input hash',hashlib.sha256(json.dumps(inp,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==b['input_hash'])
check('roster subset',inp['roster']==[r for r in load('14-inputs.json')['roster'] if r['id'] in ['SUM_ELM_EMBER','SUM_ELM_SPARK']])
rows=list(csv.DictReader((A/'22-boss-hits.csv').open())); summaries=list(csv.DictReader((A/'22-boss-summary.csv').open()))
# Independent closed-form opportunity counts, not calculator loop replay.
for state,lv in inp['states'].items():
 for delay in inp['delays']:
  for q in inp['loss_fractions']:
   events=[]
   for r in inp['roster']:
    if r['id']=='SUM_ELM_SPARK' and not lv['spark']:continue
    first=F(delay)+F(str(r['windup_s']))+F(300,600);period=F(str(r['windup_s']))+F(str(r['cooldown_s']))
    span=(F(30)-first)/period;N=max(0,-(-span.numerator//span.denominator));keep=(N*(1-F(q))).__floor__()
    damage=F(str(r['base_damage']))*F(13,10)
    subset=[x for x in rows if (x['state'],x['delay_s'],x['q'],x['summon'])==(state,delay,q,r['id'])]
    check(f'count {state}/{delay}/{q}/{r["id"]}',len(subset)==N)
    check(f'hits {state}/{delay}/{q}/{r["id"]}',all(F(x['hit_t_exact'])==first+(int(x['opportunity'])-1)*period and int(x['retained'])==(int(x['opportunity'])<=keep) and F(x['damage_exact'])==(damage if int(x['retained']) else 0) for x in subset))
    events.extend((first+i*period,damage) for i in range(keep))
   events.sort();total=sum((d for _,d in events),F(0))
   for hp in inp['hp_candidates']:
    x=next(x for x in b['results'] if (x['state'],x['delay_s'],x['q'],x['hp'])==(state,delay,q,hp));v=F(0);clear=None
    for tm,d in events:
     v+=d
     if v>=hp:clear=tm;break
    check(f'summary {state}/{delay}/{q}/{hp}',F(x['total_damage_exact'])==total and bool(x['conditional_clear'])==(clear is not None) and (not clear or F(x['clear_t_exact'])==clear))
check('csv summary count',len(summaries)==len(b['results'])==108)
for x in summaries:
 y=next(r for r in b['results'] if (r['state'],r['delay_s'],r['q'],r['hp'])==(x['state'],x['delay_s'],x['q'],int(x['hp'])))
 check('csv summary consistency '+x['state']+'/'+x['delay_s']+'/'+x['q']+'/'+x['hp'],all(str(y[k])==x[k] for k in y))
add=(A/'22-addendum.md').read_text()
check('addendum explicit boundaries',all(s in add for s in ['E01','E02','E03','E04','최종 GDD/MVP','자발 발언','질문을 던져 답을 얻지 않는다','최종 수치 채택 보류']))
check('addendum preserved main fingerprint',h in add)
check('addendum linked from resolution','22-addendum.md' in (A/'22-resolutions.md').read_text())
check('critical counterexample',next(x for x in b['results'] if (x['state'],x['delay_s'],x['q'],x['hp'])==('B_bloom_unlock','2','0',300))['total_damage_exact']=='299')
check('600/1000 impossible in fixture',not any(x['conditional_clear'] for x in b['results'] if x['hp']>=600))
for r in b['recovery']:
 check('cashflow '+r['case']+'/'+str(r['turn']),r['w_after']==r['w_before']+r['grant'] and r['shortfall']==max(0,10-r['w_after']) and r['grant']==r['assumed_killed_basic']+3*r['assumed_killed_dense'] and r['reserved_basic']==24 and r['reserved_dense']==12)
check('shop arithmetic',24-20==4 and 25-24==1 and 25-4==21)
check('A/B costs',10+20+30+20+25==105 and 105+15+30+45+20+50==265 and 60+20==80 and 60+25==85)
report={'document_id':'P1-22-VALIDATION-v01','target_sha256':h,'command':'python /home/mj/.hermes/company/kanban/game-planning-phase1/artifacts/22-validate.py','scope':'Document structure, trace/provenance and independent conditional arithmetic only; no game/user/performance/legal/approval validation','passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,'failed':[c['name'] for c in checks if not c['passed']],'counts':{'trace_rows':len(trace),'required_subitems':len(subitems),'original_findings':len(original),'resolution_statuses':dict(collections.Counter(r['status'] for r in res['findings'])),'hit_rows':len(rows),'summary_rows':len(summaries),'recovery_rows':len(b['recovery'])}}
(A/'22-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2));sys.exit(bool(report['failed']))
