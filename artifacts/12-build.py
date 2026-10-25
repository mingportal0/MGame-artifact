"""문서 표를 통합하는 편집 도구. 게임/전투 실행 코드 아님."""
from pathlib import Path
import re,json,hashlib
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
OUT=Path(__file__).parent
records=[]
sources={}
elm_prices={'BLOOM':20,'SPARK':25,'TIDE':25,'STONE':45,'PRISM':100,'SPARK_ARC':45,'TIDE_WAVE':35,'STONE_MONOLITH':60,'PRISM_CROWN':90,'POWER':10,'TEMPO':20,'SPLASH':20,'DUET':35}
for num,code in [(7,'ELM'),(8,'DRG'),(9,'BST'),(10,'DMN'),(11,'NEC')]:
    p=A/f'{num:02}.md'; text=p.read_text(); sources[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    for line_no,line in enumerate(text.splitlines(),1):
        if not line.startswith('| UPG_'+code+'_'): continue
        c=[x.strip() for x in line.strip().strip('|').split('|')]
        if code=='ELM':
            uid,name,typ,effect,maximum,pre,visual,scope=c
            base=elm_prices[uid.removeprefix('UPG_ELM_')]; step=base; model='linear'; origin='P1-12 신규 가격 가정; 07 null 대체'
        elif code=='DRG':
            uid,name,effect,maximum,costtext,pre,visual,typ,scope=c
            base=int(re.search(r'\d+',costtext).group()); m=re.search(r'step(\d+)',costtext)
            step=int(m.group(1)) if m else 0; model='linear'; origin='08 가격 가정 유지'
        elif code=='BST':
            uid,name,cat,cl,effect,maximum,costtext,unlock,pre,visual,typ=c
            base=int(re.search(r'\d+',costtext).group()); step=base; model='linear'; scope='expansion_candidate'; origin='09 가격 가정 유지'
        elif code=='DMN':
            uid,name,cat,cl,effect,maximum,costtext,unlock,pre,visual,typ=c
            base=int(costtext.split(':')[1]); step=0; model='exponential'; scope='expansion_candidate'; origin='10 가격 가정 유지'
        else:
            uid,name,effect,maximum,costtext,pre,visual,typ,scope=c
            base=int(costtext);step=base;model='linear';origin='11 가격 가정 유지'
        maximum=int(maximum)
        if maximum==1: model='one_shot';step=0
        prereq=[{'upgrade_id':i,'required_level':int(l)} for i,l in re.findall(r'(UPG_[A-Z_]+)\s*:\s*(\d+)',pre)]
        scope='mvp_candidate' if code=='ELM' and uid in ['UPG_ELM_BLOOM','UPG_ELM_SPARK'] else 'expansion_candidate'
        records.append(dict(id=uid,name=name,category='summon',applies_to='CLS_'+code,effects=effect,max_level=maximum,cost=dict(currency='gold',base=base,growth_rule=model,step=step,factor=2 if model=='exponential' else 1,rounding='ceil',status='assumed',provenance=origin),unlock_condition='run_start AND selected_class='+code,prerequisites=prereq,visual_change=visual,type=typ,scope=scope,status='proposed',source_ref=f'{num:02}.md:L{line_no}',source_effect=effect))

def common(uid,name,cat,effect,maxlv,base,step,visual,scope='mvp_candidate'):
    records.append(dict(id=uid,name=name,category=cat,applies_to='ALL',effects=effect,max_level=maxlv,cost=dict(currency='gold',base=base,growth_rule='linear',step=step,factor=1,rounding='ceil',status='assumed',provenance='P1-12 신규 가정'),unlock_condition='run_start',prerequisites=[],visual_change=visual,type='repeat',scope=scope,status='proposed',source_ref='12.md §3; source §5',source_effect=effect))
common('UPG_COM_COMMAND_RADIUS','지휘 범위 확대','game','EFF_COMMAND_GROW: command_radius=150+50×L 전장 단위; L=0~3, 최대300. 공격 사거리/효과 반경/골드 불변',3,15,15,'커서 지정 원 150→200→250→300, 실제 피해 원과 구분')
common('UPG_COM_POWER','소환 공통 화력','summon','EFF_COM_POWER: 모든 출전 소환수(임시 포함)의 공통 피해계수 M_com=1+0.10×L, 최대1.30; 직업 계산 뒤 1회 곱',3,10,10,'피해 정보/적중 숫자 증가, 개체·공격 형태 변화 없음')
common('UPG_COM_SUPPLY','몬스터 공급 확장','monster','EFF_COM_SUPPLY: 공급단계 s=L, L=0~2. 13.md s0/s1/s2 예약표 선택; BASIC 유지, DENSE 추가·s2 SPECIAL 예약. HP/골드 자동배수 없음',2,20,30,'다음 일반전 묵직한 잔영 증가, s2 황금 잔영 예약; 공격 대상으로 보이는 적 증가')
common('UPG_COM_GOLD_YIELD','처치 보상 강화','gold','EFF_COM_GOLD_YIELD: 일반 적 보상 G=floor(g_base×(1+0.25×L)), L=0~3, 최대계수1.75; 사망별 1회, 보스/상자 제외',3,20,20,'보상 정보와 즉시 잔액 변화만 증가, 동전 클릭·수집 원 없음','expansion_candidate')
common('UPG_COM_REACH','공격 도달 강화','summon','EFF_COM_REACH: 모든 출전 소환수 attack_range=기본 사거리+20×L, 최대+40 전장 단위; command_radius/효과 크기 불변',2,25,25,'사거리 정보 증가, 이동 후 정지 위치 변화; 지정 원/폭발 크기는 그대로','expansion_candidate')
# 13의 미정 보스 해금 집합을 명시적 제안으로 연결. 전용 시너지/다종 강제 없음.
boss={
 'CLS_ELM':[('UPG_COM_POWER',3),('UPG_ELM_POWER',3),('UPG_ELM_BLOOM',1)],
 'CLS_DRG':[('UPG_COM_POWER',3),('UPG_DRG_POWER',3),('UPG_DRG_ADULT',1),('UPG_DRG_ANCIENT',1)],
 'CLS_BST':[('UPG_COM_POWER',3),('UPG_BST_PACK',2),('UPG_BST_FANG',3),('UPG_BST_WOLF_LEADER',1),('UPG_BST_CROWN',1)],
 'CLS_DMN':[('UPG_COM_POWER',3),('UPG_DMN_POWER',3),('UPG_DMN_IMP_CROWN',1),('UPG_DMN_IMP_TWIN',1)],
 'CLS_NEC':[('UPG_COM_POWER',3),('UPG_NEC_BONE',3),('UPG_NEC_GUARD',1)]}
data={'document_id':'P1-12-CATALOG-v01','status':'proposed_not_approved','schema_version':'1.1-document','note':'effects는 원문 보존 문서 명세 문자열이며 게임 런타임 payload 아님. 표준 연산 계약은 12.md §4.','source_sha256':sources,'upgrades':records,'boss_required_set':{k:[{'upgrade_id':u,'required_level':l} for u,l in v] for k,v in boss.items()},'supply_stage':{'upgrade_id':'UPG_COM_SUPPLY','mapping':{'0':'13.md:s=0','1':'13.md:s=1','2':'13.md:s=2'},'boss_requirement':False}}
(OUT/'12-catalog.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
lines=['# 부록 A. 통합 업그레이드 전수표','', '자동 펼침 원본: 12-catalog.json. 모든 행 status=proposed, 비용 assumed, 단위 gold. 직업 공통 선언도 각 JSON 레코드에 명시했다. 해금은 run_start(해당 직업 선택), 선행은 AND, 모든 구매는 상점 직접 구매·다음 전투 적용. 효과 수치와 가격 모두 미승인이다.','']
for owner in ['ALL','CLS_ELM','CLS_DRG','CLS_BST','CLS_DMN','CLS_NEC']:
    lines += [f'## {owner}','', '| ID | 이름 | 분류 | 적용직업 | 유형 | 효과 | 최대레벨 | 최초비용·증가식 | 해금 | 선행 | 시각 변화 | 출처 |','|---|---|---|---|---|---|---:|---|---|---|---|---|']
    for r in records:
        if r['applies_to']!=owner:continue
        c=r['cost']; formula=f"{c['base']} (단발)" if c['growth_rule']=='one_shot' else (f"ceil({c['base']}×2^L)" if c['growth_rule']=='exponential' else f"ceil({c['base']}+{c['step']}×L)")
        pre=', '.join(f"{x['upgrade_id']}:{x['required_level']}" for x in r['prerequisites']) or '[]'
        cells=[r['id'],r['name'],r['category'],owner,r['type'],r['effects'],str(r['max_level']),formula,r['unlock_condition'],pre,r['visual_change'],r['source_ref']]
        lines.append('| '+' | '.join(x.replace('|','/') for x in cells)+' |')
    lines.append('')
(OUT/'12-appendix.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'total':len(records),'by_owner':{k:sum(r['applies_to']==k for r in records) for k in ['ALL','CLS_ELM','CLS_DRG','CLS_BST','CLS_DMN','CLS_NEC']}},ensure_ascii=False))
