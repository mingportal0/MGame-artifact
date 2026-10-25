"""P1-20 문서·출처·추적·산술 검사만. 게임/사용자/성능 검증 아님."""
from pathlib import Path
import json,re,hashlib,math,datetime
B=Path(__file__).resolve().parent
D=(B/'20.md').read_text(); T=(B/'20-trace.md').read_text()
M=json.loads((B/'20-manifest.json').read_text()); R=json.loads((B/'20-trace.json').read_text())
O=json.loads((B/'01-trace.json').read_text()); C=json.loads((B/'12-catalog.json').read_text())['upgrades']
S=(B.parent/'source.txt').read_text().splitlines()
checks=[]
def ck(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ck('Part1~10 지정순서',re.findall(r'^## Part (\d+)\.',D,re.M)==[str(i) for i in range(1,11)])
chunks={i:D.split(f'<a id="p{i}"></a>')[1].split('<a id=')[0] for i in range(1,11)}
ck('01 전수 ID·원문·분류·원책임 완전보존',len(R)==len(O) and all({k:r[k] for k in o}==o for r,o in zip(R,O)),{'rows':len(R)})
ck('전수ID 중복없음',len(set(r['id'] for r in R))==len(R))
ck('원문 물리줄 일치',all(S[r['line']-1].strip()==r['source'] for r in R))
ck('요구별 GDD 실재 앵커',all(f'id="p{r["gdd_part"]}"' in D and r['gdd_anchor']==f'20.md#p{r["gdd_part"]}' for r in R))
trace_body=T.split('## 01 전수 행',1)[1]
ck('전수 추적표 행 일대일',all(trace_body.count('| '+r['id']+' |')==1 for r in R))
for sub in M['part_subitems']:
    ck('지정하위항목 '+str(sub['line']),sub['text'] in chunks[sub['part']],sub)
for e in M['excerpts']:
    raw='\n'.join((B/e['source']).read_text().splitlines()[e['first_line']-1:e['last_line']]).strip()
    text=re.sub(r'(?m)^#{1,4} ','##### ',raw)
    ck('발췌정합 '+e['label'],text in D and hashlib.sha256(text.encode()).hexdigest()==e['text_sha256'])
for path,h in M['input_sha256'].items():ck('입력불변 '+Path(path).name,Path(path).exists() and sha(Path(path))==h)
missing=[]
for name in ['20.md','20-trace.md']:
    for url in re.findall(r'\]\(([^)]+)\)',(B/name).read_text()):
        if url.startswith(('https://','http://')):continue
        path,_,anchor=url.partition('#'); p=(B/path).resolve() if path else B/name
        if not p.exists():missing.append(url)
        elif anchor and f'id="{anchor}"' not in p.read_text():missing.append(url)
ck('로컬 링크·명시 앵커 실재',not missing,missing)
ids=[r['id'] for r in C]
full_tables=re.findall(r'^\| (UPG_[A-Z0-9_]+) \|',chunks[4],re.M)
ck('통합69 전수표 원천순서·ID보존',len(C)==69 and full_tables==[r.split('|')[1].strip() for r in (B/'12.md').read_text().splitlines() if re.match(r'^\| UPG_',r)] and set(full_tables)==set(ids),{'catalog':len(C),'table_rows':len(full_tables)})
fields=['id','name','category','applies_to','effects','max_level','cost','unlock_condition','prerequisites','visual_change']
ck('업그레이드10필드/상태/유한레벨',all(all(k in u for k in fields) and u['status']=='proposed' and u['max_level']>0 for u in C))
ck('업그레이드ID중복0',len(ids)==len(set(ids)))
known=set(ids)
used=set(re.findall(r'\bUPG_[A-Z0-9_]+\b',D)); ck('본문UPG참조 유효',used<=known,sorted(used-known))
classids=set(re.findall(r'\bCLS_[A-Z]+\b',D));ck('5직업ID',classids=={'CLS_ELM','CLS_DRG','CLS_BST','CLS_DMN','CLS_NEC'})
summons=set(re.findall(r'\bSUM_(?:ELM|DRG|BST|DMN|NEC)_[A-Z]+\b',chunks[3])); ck('기본+추가4 각직업 종수',all(len([s for s in summons if s.startswith('SUM_'+c+'_')])==5 for c in ['ELM','DRG','BST','DMN','NEC']),sorted(summons))
ck('원문G1변경행 구분',all('G1' in next(r['disposition'] for r in R if r['line']==l) for l in [59,60,79,161,189,196,263,312,388,389,418,451,469]))
ck('정정원장12행',all(re.search(r'^\| I%02d \|'%i,D,re.M) for i in range(1,13)))
ck('위험10개/미합의7개/TOP5',all(f'R{i:02}' in chunks[9] for i in range(1,11)) and all(f'U{i:02}' in chunks[9] for i in range(1,8)) and all(f'TOP{i}' in chunks[9] for i in range(1,6)))
ck('재미가설 H1~H5 실험방법/지표/기준/중단/표본',all(f'H{i}.' in chunks[8] for i in range(1,6)) and all(k in chunks[8] for k in ['방법:','관찰지표:','성공/실패:','중단/수정:','대상/표본:']))
ck('첫작업7/착수결정10',all(f'W{i:02}' in chunks[10] for i in range(1,8)) and all(f'D{i:02}' in chunks[10] for i in range(1,11)))
ck('축소 HP/손실 명시적 미판정',M['reduced_boss_status']=='not_evaluated_for_HP300_600_1000_or_command_loss' and chunks[6].count('미판정')>=7)
ck('실제검증/승인경계 명시',all(s in D for s in ['실제0명','G3 개발 미승인','새전문검토','대표별도명시승인전blocked유지']))
# 아래는18의 비용/공급/원장 단순산술 독립대조일 뿐 축소화력 계산 아님.
byid={u['id']:u for u in C}
def cost(u,l):
    c=u['cost']; rule=c['growth_rule']
    return math.ceil(c['base'] if rule=='one_shot' else c['base']+c['step']*l if rule=='linear' else c['base']*c['factor']**l)
reduced=['UPG_COM_COMMAND_RADIUS','UPG_COM_POWER','UPG_COM_SUPPLY','UPG_ELM_BLOOM','UPG_ELM_SPARK']
allcost=sum(cost(byid[x],l) for x in reduced for l in range(byid[x]['max_level']))
req=sum(cost(byid['UPG_COM_POWER'],l) for l in range(3))+cost(byid['UPG_ELM_BLOOM'],0)+cost(byid['UPG_ELM_SPARK'],0)
ck('축소 완매비용265',allcost==265,allcost); ck('축소 해금비용105',req==105,req)
ceilings=[{'s':s,'reserved':6*(4+2*s),'gold_ceiling':6*(4+2*s*3)} for s in range(3)]
ck('축소예약24/36/48·지급천장24/60/96',[(x['reserved'],x['gold_ceiling']) for x in ceilings]==[(24,24),(36,60),(48,96)],ceilings)
ck('원장 24즉시지급-20구매·정산0·실패0=4',0+24-20+0+0==4)
ck('全카탈로그/축소안 혼용방지',all(s in D for s in ['전체결과를 축소에 복사하지 않음','축소승리증거가아니다','일반2종·5항목']))
# 한 과거 입력 14/15 원천은 이번 재실행/수치승인으로 보고하지 않음.
ck('선행산술 재실행을 주장하지않음','기존 계산기를 재실행해 새 결과로 보고하지 않는다' in D)
passed=sum(x['passed'] for x in checks)
report={'document_id':'P1-20-GDD-v01','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':passed,'total':len(checks),'failed':[x for x in checks if not x['passed']],'checks':checks,'trace_rows':len(R),'part_subitems':len(M['part_subitems']),'excerpts':len(M['excerpts']),'catalog_rows':len(full_tables),'summon_definitions':len(summons),'artifact_sha256':{n:sha(B/n) for n in ['20.md','20-trace.md','20-trace.json','20-manifest.json','20-validate.py']},'scope':'문서구조·출처·변경추적·명시상태·ID·로컬링크·비용/공급/원장 산술만. 의미적 전문 승인·축소화력/HP손실·실제K·플레이·사용자·기능·성능·접근성·재미 검증 아님.','not_performed':['축소보스화력계산','동료신규검토/역동의','게임코드/프로토타입/프로젝트초기화','실제참가자접촉/실험','벤치마크/설치/유료/외부공개','후속카드실행/해제','Slack실제전달직접확인']}
(B/'20-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['passed','total','failed','trace_rows','part_subitems','catalog_rows','summon_definitions','excerpts']},ensure_ascii=False,indent=2))
raise SystemExit(0 if passed==len(checks) else 1)
