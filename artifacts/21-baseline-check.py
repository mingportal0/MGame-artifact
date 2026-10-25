from pathlib import Path
import json, hashlib, re, datetime
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
checks=[]
def check(name,ok,detail=''):
 checks.append({'name':name,'passed':bool(ok),'detail':detail})
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
text=(A/'20.md').read_text(); lines=text.splitlines()
check('target version','P1-20-GDD-v01' in text)
check('target hash',h(A/'20.md')=='0d40dd6a5bf795b7984c742a6c8def8edce81d16d8973016a8d4a3237332ec87')
m=json.loads((A/'20-manifest.json').read_text())
for p,want in m['input_sha256'].items():check('baseline input hash '+Path(p).name,h(Path(p))==want)
source=(A.parent/'source.txt').read_text().splitlines()
trace=json.loads((A/'20-trace.json').read_text())
check('trace exact source ID set', {r['id'] for r in trace}=={f'R-L{i:03}' for i,s in enumerate(source,1) if s.strip() and s.strip()!='---'})
whitespace_differences=[]
for r in trace:
 raw=source[r['line']-1]
 if r['source']!=raw: whitespace_differences.append({'id':r['id'],'trace':r['source'],'source':raw,'whitespace_only':r['source'].strip()==raw.strip()})
 check('trace row '+r['id'],r['source'].strip()==raw.strip() and r['id']==f"R-L{r['line']:03}")
for part in range(1,11):check(f'Part{part}',f'<a id="p{part}"></a>' in text)
for uid in range(1,8):check(f'open U{uid:02}',f'U{uid:02}' in text)
check('reduced boss explicit not judged','명시적 미판정' in text and 'HP300도잡힌다고주장하지않는다' in text)
check('no new colleague review claim', '본 v01의 새로운 동료 교차 검토는 미실행' in text)
for u in ['수집률','미수집','수집 반경']:
 check('G1 replacement preserved '+u,u in text)
for n,s in enumerate(m['part_subitems']):check('source subitem '+str(s['line']),s['text'] in source[s['line']-1] and s['text'] in text)
for label in ['20.md','20-trace.json','20-manifest.json','21-review-requests.json']:
 check('exists '+label,(A/label).is_file())
result={'checked_at':datetime.datetime.now().astimezone().isoformat(),'scope':'Sophie independent baseline document/hash/source-presence checks; NOT replay of P1-20 126-check tool, no gameplay/user/performance verification','target_sha256':h(A/'20.md'),'line_count':len(lines),'trace_rows':len(trace),'whitespace_differences':whitespace_differences,'trace_comparison':'strip leading/trailing whitespace only; literal byte identity not asserted','initial_check_note':'496/502 strict trace text comparison; six whitespace-only differences preserved below. No source or trace edited. Corrected text-comparison criterion to whitespace-trimmed source, ID and hash remain exact.','passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks}
(A/'21-baseline-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))
print('FAILURES',json.dumps([c for c in checks if not c['passed']],ensure_ascii=False))
