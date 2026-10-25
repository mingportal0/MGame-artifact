from pathlib import Path
import json,re,hashlib,shutil
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts'); W=Path(__file__).parent
old=(A/'20.md').read_text(); text=(W/'22-main.md').read_text()
for i in [3,4]:
 start=old.index('### 통합 요약',old.index(f'## Part {i}.'))
 end=old.index(f'<a id="p{i+1}"></a>')
 fragment=old[start:end]
 # All retained headings are source detail, subordinate to new scope/contract.
 fragment='\n### 확장 상세 부록 — 20 v01 재수록, 축소 실행 바인딩 금지\n\n'+fragment
 fragment=re.sub(r'^#{2,5} ',lambda m:'#'+m.group(0),fragment,flags=re.M)
 text=text.replace('{{PART'+str(i)+'_DETAIL}}',fragment)
balance=json.loads((A/'22-balance.json').read_text()); rows=balance['results']
md=['| 상태/지연a/합성손실q | T미만 총피해 | HP300 | HP600 | HP1000 |','|---|---:|---|---|---|']
for state in ['A_unlock','A_max','B_bloom_unlock','B_spark_unlock']:
 for a,q in [('0','0'),('2','0'),('2','0.10'),('2','0.25'),('5','0.25')]:
  r=[r for r in rows if r['state']==state and r['delay_s']==a and r['q']==q]
  md.append('|'+state+'/'+a+'/'+q+'|'+str(r[0]['total_damage'])+'|'+'|'.join('조건부가능 t='+str(v['clear_t_s']) if v['conditional_clear'] else '조건내실패' for v in r)+'|')
text=text.replace('{{BALANCE_TABLE}}','\n'.join(md))
text=text.replace('HP300도취소/지연이커지면실패할수있다.','특히 B의 BLOOM단독 해금은 a=2/q=0에서도 총299로 HP300에1피해 모자란다. a=0에서도 손실을주면막힐수있다. 이것은권고B/HP300을동시에그대로채택할수없다는계산반례이며치명잔여다. SPARK추가구매경로는있지만대표성장선택이곧승리라는보장으로표현금지. HP300도취소/지연이커지면실패할수있다.')
(A/'22.md').write_text(text)
# preserve all original requirement IDs/text, add explicit new destinations.
trace=json.loads((A/'20-trace.json').read_text())
for r in trace:
 r['baseline_anchor']=r['gdd_anchor'];r['gdd_anchor']=r['gdd_anchor'].replace('20.md#','22.md#')
 r['unresolved']='22 Part9 U01~U07/I07 and Part10 D01~D06; independent reviewer results in22-resolutions; no final approval'
(A/'22-trace.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
(A/'22-trace.md').write_text('# P1-22 원문 전수 추적\n\n20의 ID/원문/책임/출처를 보존하고 현재22 Part에 연결. 서술 포함은 구현/승인/검증 완료가 아니다. G1 대체 기준은22 §0 및 각 Part 우선.\n\n| ID | 원문행 | 현재위치 | 처리·기준 |\n|---|---:|---|---|\n'+'\n'.join(f"|{r['id']}|{r.get('line','')}|[{r['gdd_anchor']}]({r['gdd_anchor']})|{r['disposition']}|" for r in trace)+'\n')
for name in ['22-calculate.py']:
 shutil.copy2(W/name,A/name)
print(json.dumps({'document_sha256':hashlib.sha256((A/'22.md').read_bytes()).hexdigest(),'lines':len(text.splitlines()),'trace_rows':len(trace),'trace_kind_counts':{k:sum(r['id'].startswith(k) for r in trace) for k in ['R-','P']}},ensure_ascii=False))
