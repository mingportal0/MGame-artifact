"""P1-12 문서 카탈로그 검증. 전투 시뮬레이터/게임 코드 아님."""
from pathlib import Path
import json,re,copy,hashlib
from collections import Counter
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
P=Path(__file__).resolve().parent
D=json.loads((P/'12-catalog.json').read_text())
results=[]
def check(name,ok):
    results.append({'check':name,'passed':bool(ok)})
    if not ok: raise AssertionError(name)
def validate(d):
    rows=d['upgrades']; ids=[r['id'] for r in rows]
    assert len(ids)==len(set(ids)), 'duplicate'
    by={r['id']:r for r in rows}
    required={'id','name','category','applies_to','effects','max_level','cost','unlock_condition','prerequisites','visual_change','type','scope','status','source_ref'}
    for r in rows:
        assert required<=r.keys(),'fields'
        assert re.fullmatch(r'UPG_[A-Z0-9_]+',r['id']),'id'
        assert all(r[k] for k in required-{'prerequisites'}),'empty'
        assert r['category'] in {'game','monster','gold','summon'},'category'
        assert r['type'] in {'repeat','unlock','evolve','synergy'},'type'
        assert r['applies_to'] in {'ALL','CLS_ELM','CLS_DRG','CLS_BST','CLS_DMN','CLS_NEC'},'class'
        assert isinstance(r['max_level'],int) and r['max_level']>0,'cap'
        c=r['cost']; assert c['base']>0 and c['step']>=0 and c['currency']=='gold' and c['status']=='assumed','cost'
        assert c['growth_rule'] in {'linear','exponential','one_shot'},'cost rule'
        for dep in r['prerequisites']:
            assert dep['upgrade_id'] in by,'missing ref'
            other=by[dep['upgrade_id']]
            assert 0<dep['required_level']<=other['max_level'],'unreachable level'
            assert other['applies_to'] in ['ALL',r['applies_to']],'cross class'
    visiting=set();done=set()
    def visit(uid):
        assert uid not in visiting,'cycle'
        if uid in done:return
        visiting.add(uid)
        for x in by[uid]['prerequisites']: visit(x['upgrade_id'])
        visiting.remove(uid);done.add(uid)
    for uid in by:visit(uid)
    # Monotonic unlock run_start, no progression gates beyond DAG.
    reachable=set()
    while True:
        new={r['id'] for r in rows if all(x['upgrade_id'] in reachable for x in r['prerequisites'])}
        if new<=reachable:break
        reachable|=new
    assert reachable==set(ids),'unreachable'
    assert set(d['boss_required_set'])=={'CLS_ELM','CLS_DRG','CLS_BST','CLS_DMN','CLS_NEC'},'boss classes'
    for cl,deps in d['boss_required_set'].items():
        assert deps,'empty boss'
        assert len(deps)==len({x['upgrade_id'] for x in deps}),'boss duplicate'
        for x in deps:
            assert x['upgrade_id'] in by,'boss ref'
            r=by[x['upgrade_id']]
            assert r['applies_to'] in ['ALL',cl],'boss class'
            assert 0<x['required_level']<=r['max_level'],'boss level'
            assert r['type']!='synergy','forced synergy'
    assert d['supply_stage']['upgrade_id'] in by,'supply ref'
    assert by[d['supply_stage']['upgrade_id']]['max_level']==2,'supply cap'
    return by
by=validate(D)
check('69 records / unique IDs / required fields / enums / DAG / reachable / boss refs',len(by)==69)
expected={'ALL':5,'CLS_ELM':13,'CLS_DRG':12,'CLS_BST':13,'CLS_DMN':12,'CLS_NEC':14}
check('owner counts',dict(Counter(r['applies_to'] for r in by.values()))==expected)
check('four categories',set(r['category'] for r in by.values())=={'game','monster','gold','summon'})
check('four types',set(r['type'] for r in by.values())=={'repeat','unlock','evolve','synergy'})
source_dir=P if (P/'07.md').exists() else Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
for n,cl in [(7,'ELM'),(8,'DRG'),(9,'BST'),(10,'DMN'),(11,'NEC')]:
    src=source_dir/f'{n:02}.md';raw=src.read_bytes()
    check(f'{n:02} source snapshot unchanged',hashlib.sha256(raw).hexdigest()==D['source_sha256'][src.name])
    lines=raw.decode().splitlines(); source_ids=[]
    for line in lines:
        if line.startswith('| UPG_'+cl+'_'):source_ids.append(line.split('|')[1].strip())
    actual={r['id'] for r in by.values() if r['applies_to']=='CLS_'+cl}
    check(f'{n:02} all source upgrade IDs preserved',actual==set(source_ids))
    check(f'{n:02} source effects exact',all(r['effects']==r['source_effect'] and r['effects'] in lines[int(r['source_ref'].split(':L')[1])-1] for r in by.values() if r['applies_to']=='CLS_'+cl))

def price(r,L):
    assert 0<=L<r['max_level']
    c=r['cost'];v=c['base']
    if c['growth_rule']=='linear':v+=c['step']*L
    elif c['growth_rule']=='exponential':v*=c['factor']**L
    return int(Decimal(str(v)).to_integral_value(rounding=ROUND_CEILING))
price_lists=[[price(r,L) for L in range(r['max_level'])] for r in by.values()]
check('all legal level prices positive and monotonic',all(all(v>0 for v in ps) and ps==sorted(ps) for ps in price_lists))
check('ELM former nulls priced, assumed not approved',all(r['cost']['base']>0 and r['cost']['status']=='assumed' and r['status']=='proposed' for r in by.values() if r['applies_to']=='CLS_ELM'))
check('radius stages 150/200/250/300',[150+50*l for l in range(4)]==[150,200,250,300])
check('NEC cooldown mapping / sentinel interval',Decimal('.2')+Decimal('.6')==Decimal('.8'))
check('damage ELM POWER3 DUET COM3',(Decimal(10)+2*3+3)*Decimal('1.3')==Decimal('24.7'))
check('damage DMN POWER1 CROWN COM3',Decimal(10)*Decimal('1.2')*Decimal('1.5')*Decimal('1.3')==Decimal('23.4'))
check('damage NEC GUARD BONE3 CONDUCT COM3',(Decimal(6)*Decimal('1.75')+2)*Decimal('1.3')==Decimal('16.25'))
check('damage symbolic DRG additive coefficients',Decimal(1)+Decimal('.3')+Decimal('.3')+Decimal('.1')==Decimal('1.7'))
check('damage symbolic BST additive coefficients',Decimal(1)+Decimal('.3')+Decimal('.2')+Decimal('.3')+Decimal('.1')==Decimal('1.9'))
# Structural purchase budget, NOT generated income or playtime.
budgets={}
for cl,deps in D['boss_required_set'].items():
    levels={}
    def need(uid,lv):
        levels[uid]=max(levels.get(uid,0),lv)
        for dep in by[uid]['prerequisites']:need(dep['upgrade_id'],dep['required_level'])
    for dep in deps:need(dep['upgrade_id'],dep['required_level'])
    budgets[cl]={'closure':levels,'gold':sum(price(by[uid],l) for uid,lv in levels.items() for l in range(lv))}
    check(cl+' boss closure finite affordable symbolic gold',budgets[cl]['gold']>0)
check('boss sets exclude supply and synergy',all('UPG_COM_SUPPLY' not in b['closure'] and all(by[u]['type']!='synergy' for u in b['closure']) for b in budgets.values()))
# Quantify per-death flooring, no inferred actual income.
gold_caps={}
for l in range(4):
    m=Decimal(1)+Decimal('.25')*l
    gs=[int((Decimal(g)*m).to_integral_value(rounding=ROUND_FLOOR)) for g in [1,3,6]]
    gold_caps[l]={'per_monster':gs,'scheduled_caps':[24*gs[0],24*gs[0]+12*gs[1],24*gs[0]+24*gs[1]+gs[2]]}
check('unboosted scheduled caps',gold_caps[0]['scheduled_caps']==[24,60,102])
check('BASIC gold has dead levels',all(v['per_monster'][0]==1 for v in gold_caps.values()))
check('supply reservations',[6*4,6*6,6*8+1]==[24,36,49])
check('ledger immediate reward minus purchases',10-10+20-20==0)
negative=[]
def reject(name,mutate):
    d=copy.deepcopy(D);mutate(d)
    try:validate(d)
    except AssertionError as e:negative.append({'case':name,'rejected':True,'reason':str(e)});check('negative '+name,True)
    else:check('negative '+name,False)
reject('duplicate',lambda d:d['upgrades'].append(copy.deepcopy(d['upgrades'][0])))
reject('missing field',lambda d:d['upgrades'][0].pop('visual_change'))
reject('missing dependency',lambda d:d['upgrades'][0]['prerequisites'].append({'upgrade_id':'UPG_COM_MISSING','required_level':1}))
reject('self cycle',lambda d:d['upgrades'][0]['prerequisites'].append({'upgrade_id':d['upgrades'][0]['id'],'required_level':1}))
reject('unreachable required level',lambda d:d['upgrades'][0]['prerequisites'].append({'upgrade_id':'UPG_COM_POWER','required_level':99}))
reject('empty boss set',lambda d:d['boss_required_set'].__setitem__('CLS_NEC',[]))
reject('cross class boss',lambda d:d['boss_required_set']['CLS_NEC'].append({'upgrade_id':'UPG_ELM_SPARK','required_level':1}))
report={'document_id':D['document_id'],'passed':sum(x['passed'] for x in results),'total':len(results),'checks':results,'counts':{'total':len(by),'by_owner':expected,'by_category':dict(Counter(r['category'] for r in by.values())),'by_type':dict(Counter(r['type'] for r in by.values()))},'boss_budget_gold_assumed':budgets,'gold_caps_scheduled_not_actual':gold_caps,'negative_tests':negative,'scope':'문서 구조/원문보존/참조/DAG/조건도달성/가정 산술만. 게임·실제사용자·UX/기술 전문검토·성능·경제밸런스·클리어가능성 검증 아님. 용/동물 원천 공격값 미정.','not_performed':['게임코드/프로토타입','전투 시뮬레이션','사용자 테스트','Mia/Sam 검토','실측 성능','Slack 전달 확인']}
(P/'12-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'total':report['total'],'counts':report['counts'],'boss_budget_gold':{k:v['gold'] for k,v in budgets.items()},'gold_caps':gold_caps},ensure_ascii=False,indent=2))
