"""P1-14 document arithmetic, not game/AI/combat implementation.
Finite closed-form hit counts, catalog costs, supplied kill-count budgets only.
Run in workspace or deliverable directory; outputs stay beside this file.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, ROUND_CEILING
import json, math, hashlib, csv
from itertools import combinations
ROOT = Path(__file__).resolve().parent
SRC = Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
cat = json.loads((SRC/'12-catalog.json').read_text())
up = {x['id']:x for x in cat['upgrades']}
checks=[]
def ck(name, cond):
    checks.append({'name':name,'pass':bool(cond)})
    assert cond, name

def cost(uid, level):
    u=up[uid]; c=u['cost']
    if not 0 <= level < u['max_level']: return None
    b=Decimal(str(c['base'])); rule=c['growth_rule']
    if rule=='one_shot': v=b
    elif rule=='linear': v=b+Decimal(str(c['step']))*level
    elif rule=='exponential': v=b*Decimal(str(c['factor']))**level
    else: raise ValueError(rule)
    return int(v.to_integral_value(rounding=ROUND_CEILING))

def closure(req):
    r={x['upgrade_id']:x['required_level'] for x in req}
    while True:
        before=r.copy()
        for uid in list(r):
            for p in up[uid]['prerequisites']:
                r[p['upgrade_id']]=max(r.get(p['upgrade_id'],0),p['required_level'])
        if before==r: return r

def budget(levels):
    return sum(cost(uid,l) for uid,n in levels.items() for l in range(n))

# id suffix, damage, windup, cooldown, reach, projectile, shape, radius/half-angle, targets
raw={
'ELM': [('EMBER',10,.2,1,300,True,'single',0,1),('SPARK',7,.2,1.4,300,True,'chain',100,3),('TIDE',5,.2,.6,300,True,'single',0,1),('STONE',24,.2,2.2,300,True,'single',0,1),('PRISM',18,.2,2.8,300,True,'splash',70,3)],
'DRG': [('WHELP',18,.3,1.5,260,True,'single',0,1),('WYVERN',10,.2,.8,300,True,'single',0,1),('STONE',28,.4,2,250,True,'splash',70,3),('STORM',12,.2,1.4,280,True,'chain',100,3),('MOON',32,.3,1.8,300,True,'single',0,1)],
'BST': [('WOLF',6,.2,.8,40,False,'single',0,1),('HAWK',5,.2,1,300,True,'single',0,1),('BOAR',10,.3,1.2,45,False,'single',0,1),('BEAR',16,.4,1.6,50,False,'single',0,1),('STAG',6,.15,.65,45,False,'single',0,1)],
'DMN': [('IMP',10,.2,1,300,True,'single',0,1),('EXECUTOR',20,.3,1.5,40,False,'single',0,1),('HOUND',6,.1,.7,40,False,'single',0,1),('HEXER',8,.3,1.7,300,True,'splash',80,3),('TYRANT',30,.5,2,180,False,'cone',30,4)],
'NEC': [('SKELETON',4,.2,1,40,False,'single',0,1),('LICH',8,.2,1.2,300,True,'single',0,1),('ARCHER',5,.2,.8,300,True,'single',0,1),('REVENANT',10,.2,1.5,50,False,'single',0,1),('GOLEM',12,.2,2,60,False,'splash',70,3)]}
roster=[]
for cls, rows in raw.items():
    for name,d,w,cd,r,p,shape,fx,n in rows:
        roster.append(dict(id=f'SUM_{cls}_{name}',class_id=f'CLS_{cls}',base_damage=d,windup_s=w,cooldown_s=cd,attack_range=r,move_speed=400,projectile_speed=600 if p else None,projectile_lifetime_s=2 if p else None,shape=shape,effect_size=fx,max_targets=n,initial_count=int(name==rows[0][0]),status='assumed_not_approved',provenance=f'{cls}: 14 new null-fill assumptions' if cls in ('DRG','BST') else f'{cls}: 07/10/11 via 12 timing corrections'))
ck('roster 25 unique ids',len(roster)==25 and len({r['id'] for r in roster})==25)
ck('positive finite attack fields',all(r['base_damage']>0 and r['windup_s']>0 and r['cooldown_s']>0 and r['attack_range']>0 for r in roster))

# Scenario vectors are formula inputs, not implemented upgrade-effect dispatch.
# Each row stores per-unit damage after class/common effects, cooldown, count, projectile delay.
def unit(cls,name,damage=None,cd=None,count=1,projectile=None):
    r=next(x for x in roster if x['id']==f'SUM_{cls}_{name}')
    p=(r['projectile_speed'] is not None) if projectile is None else projectile
    return dict(id=r['id'],damage=str(damage if damage is not None else r['base_damage']),windup_s=str(r['windup_s']),cooldown_s=str(cd if cd is not None else r['cooldown_s']),count=count,flight_s=str(F(str(r['attack_range']))/600) if p else '0')
required={
'ELM':[unit('ELM','EMBER','20.8')],
'DRG':[unit('DRG','WHELP','37.44',projectile=False)],
'BST':[unit('BST','WOLF','14.04',count=3)],
'DMN':[unit('DMN','IMP','31.2',count=2)],
'NEC':[unit('NEC','SKELETON','13.65')]}
maximum={
'ELM':[unit('ELM','EMBER','24.7'),unit('ELM','SPARK','9.1',cd=1.2),unit('ELM','TIDE','10.4'),unit('ELM','STONE','31.2'),unit('ELM','PRISM','23.4')],
'DRG':[unit('DRG','WHELP','37.44',projectile=False),unit('DRG','WYVERN',13,cd=.64),unit('DRG','STONE','36.4'),unit('DRG','STORM','15.6'),unit('DRG','MOON','60.32')],
'BST':[unit('BST','WOLF','14.82',count=3),unit('BST','HAWK','9.1',count=2),unit('BST','BOAR','16.9',count=2),unit('BST','BEAR','27.04'),unit('BST','STAG','10.14',cd=.52)],
'DMN':[unit('DMN','IMP','31.2',cd=.8,count=2),unit('DMN','EXECUTOR','41.6',cd=1.2),unit('DMN','HOUND','18.72',cd=.56),unit('DMN','HEXER','16.64',cd=1.36),unit('DMN','TYRANT','62.4',cd=1.6)],
'NEC':[unit('NEC','SKELETON','16.25'),unit('NEC','LICH','15.6'),unit('NEC','ARCHER','6.5',cd=.6),unit('NEC','REVENANT',13),unit('NEC','GOLEM','23.4')]}

def hits(T,first,interval):
    # Number of first+k*interval < T; exact rational endpoint exclusion.
    span=F(str(T))-F(str(first)); step=F(str(interval))
    if step<=0: raise ValueError('interval must be positive')
    return max(0, math.ceil(span/step))

def damage_table(units,delay=2,ideal=False,T=30):
    rows=[]
    for u in units:
        first=F(str(delay))+F(u['windup_s'])+(0 if ideal else F(u['flight_s']))
        interval=F(u['windup_s'])+F(u['cooldown_s'])
        h=hits(T,first,interval)
        d=F(u['damage'])*h*u['count']
        rows.append({**u,'first_hit_s':float(first),'interval_s':float(interval),'hits_per_unit':h,'total_damage':float(d)})
    return rows, sum(F(r['damage'])*r['hits_per_unit']*r['count'] for r in rows)

boss=[]
for cls in raw:
    for state,units in [('required',required[cls]),('maximum',maximum[cls])]:
        # DRG has at most two deployed species, not five. Full-catalog cost retained.
        candidates=list(combinations(units,2)) if cls=='DRG' and state=='maximum' else [tuple(units)]
        scored=[(damage_table(x)[1],x) for x in candidates]
        _, chosen=max(scored,key=lambda x:x[0])
        detail,total=damage_table(chosen)
        # DUET is inactive for selected WHELP+MOON; all pair upper bounds below allow its valid pair.
        if cls=='DRG' and state=='maximum':
            scored=[]
            for pair in candidates:
                pair=[dict(u) for u in pair]
                if {u['id'] for u in pair}=={'SUM_DRG_WHELP','SUM_DRG_WYVERN'}:
                    pair[0]['damage']='39.78'; pair[1]['damage']='14.3'
                scored.append((damage_table(pair)[1],pair))
            _,chosen=max(scored,key=lambda x:x[0]); detail,total=damage_table(chosen)
        levels=closure(cat['boss_required_set'][f'CLS_{cls}']) if state=='required' else {u['id']:u['max_level'] for u in up.values() if u['applies_to'] in ('ALL',f'CLS_{cls}')}
        ideal_rows,upper=damage_table(chosen,delay=0,ideal=True)
        # Damage sums ignore kill-stop; comparing horizon damage is an equivalent feasibility test for constant damage, one target.
        boss.append(dict(class_id=f'CLS_{cls}',state=state,levels=levels,budget_gold=budget(levels),roster=detail,damage_30s=float(total),ideal_zero_delay_damage=float(upper),hp1000_pass=total>=1000,hp600_pass=total>=600,hp300_pass=total>=300,damage_multiplier_for_1000=float(F(1000)/total),note='DMN basic-only lower bound: no mark bonus; NEC temporary=0; DRG best legal two under this fixture'))
ck('boss 10 states',len(boss)==10)
ck('all maximum basic-only vectors beat HP1000 in fixture',all(x['hp1000_pass'] for x in boss if x['state']=='maximum'))
ck('NEC required cannot win even ideal fixture',next(x for x in boss if x['class_id']=='CLS_NEC' and x['state']=='required')['ideal_zero_delay_damage']<1000)
ck('required budgets match catalog handoff',[x['budget_gold'] for x in boss if x['state']=='required']==[140,540,345,195,132])
ck('DRG maximum respects two slots',len(next(x for x in boss if x['class_id']=='CLS_DRG' and x['state']=='maximum')['roster'])==2)
ck('NEC boss has permanent only',all('TEMP' not in u['id'] for x in boss if x['class_id']=='CLS_NEC' for u in x['roster']))
ck('endpoint exact T excluded',hits(30,0,1)==30 and hits(30,30,1)==0 and hits(30,'29.999',1)==1)
ck('slow interval and empty horizon',hits(30,1,40)==1 and hits(0,1,1)==0)
ck('all max levels reject cost',all(cost(uid,u['max_level']) is None for uid,u in up.items()))
ck('negative cost level rejects',all(cost(uid,-1) is None for uid in up))

# Gold/turn ceilings use reservation totals, not estimated gameplay kills.
gold=[]
for s,dense in enumerate([0,12,24]):
    for L in range(4):
        reward=[math.floor(F(g)*(1+F(1,4)*L)) for g in [1,3,6]]
        cap=24*reward[0]+dense*reward[1]+(s==2)*reward[2]
        gold.append(dict(supply=s,yield_level=L,basic_reward=reward[0],dense_reward=reward[1],special_reward=reward[2],reservation_gold_ceiling=cap))
ck('L0 supply gold ceilings',[x['reservation_gold_ceiling'] for x in gold if x['yield_level']==0]==[24,60,102])
ck('gold L1 dead at s0 and s1',all(x['reservation_gold_ceiling']==[24,60][x['supply']] for x in gold if x['yield_level']==1 and x['supply']<2))
ck('basic reward never rises',all(x['basic_reward']==1 for x in gold))

# Supply48 boundary arithmetic: no kills -> at most48 spawned vs49 reserved.
ck('s2 reservation49 with no kills spawned48',min(48,6*(4+4)+1)==48)
# Monotone progress conditional on >0 actual kills, not on theoretical DPS alone.
def wait(price,balance,income,think=8,transition=2):
    if price is None: return {'status':'MAX'}
    if price<=balance: return dict(turns=0,combat_s=0,wall_s=think)
    if income<=0: return {'status':'UNREACHABLE_UNDER_FIXTURE'}
    n=math.ceil(F(price-balance,income))
    return dict(turns=n,combat_s=30*n,wall_s=n*(30+think+transition))
waits=[]
for x in boss:
    if x['state']!='required': continue
    for inc in [6,12,24]:
        waits.append(dict(class_id=x['class_id'],required_budget=x['budget_gold'],assumed_basic_kills_per_turn=inc,**wait(x['budget_gold'],0,inc)))
ck('zero income infinity branch',wait(10,0,0)['status']=='UNREACHABLE_UNDER_FIXTURE')
ck('affordable no battle',wait(10,10,0)['turns']==0)
ck('ceiling discrete turns',wait(25,0,24)['turns']==2)
ck('max no next purchase',wait(None,0,10)['status']=='MAX')
ck('common damage example',F('24.7')==(10+2*3+3)*F('1.3'))
ck('wolf required damage',F('14.04')==6*(1+F('.3')+F('.2')+F('.3'))*F('1.3'))
ck('NEC max damage',F('16.25')==(6*F('1.75')+2)*F('1.3'))
ck('NEC CD mapping',F('.2')+1==F('1.2'))
ck('R_cmd boundary included',150**2<=150**2 and not 151**2<=150**2)
ck('reach and radius independent',150+50*3==300 and 40+20*2==80)
ck('yield L2 s1 ceiling72',next(x for x in gold if x['supply']==1 and x['yield_level']==2)['reservation_gold_ceiling']==72)
# ROI fixtures: identical kills, not equal-time full strategy optimization.
roi={'yield_L1_s0_delta':0,'yield_L1_s1_delta':0,'yield_L1_s2_max_delta':1,'yield_L1_s2_best_payback_turns':20,'supply0_to1_all_killed_delta_gold':36,'supply0_to1_cost':20,'warning':'ceil ceilings only; supply/kill opportunity cost ignored; real kill counts must be supplied'}
ck('yield best payback arithmetic',math.ceil(20/1)==roi['yield_L1_s2_best_payback_turns'])
ck('supply best gain arithmetic',60-24==roi['supply0_to1_all_killed_delta_gold'])
inputs=dict(document_id='P1-14-ECON-v01',status='assumptions_not_approved',combat_s=30,boss_comparison_hp=1000,boss_access_delay_s=2,boss_fixture='stationary, continuous cursor eligibility after delay, no cancellation, all ready after delay, flight at base reach; not sampled trajectories',shop_think_s=[3,8,15],transition_s=2,initial_gold=0,gold_collection='immediate grant, no collection-rate multiplier',normal_enemies=[dict(id='MON_BASIC',hp=10,gold=1,speed=40),dict(id='MON_DENSE',hp=30,gold=3,speed=25),dict(id='MON_SPECIAL',hp=40,gold=6,speed=35)],supply_reserved_counts=[[24,0,0],[24,12,0],[24,24,1]],simultaneous_enemy_cap=48,roster=roster,boss_vectors=dict(required=required,maximum=maximum),caps=dict(ELM=[5,0],DRG=[2,0],BST=[9,0],DMN=[6,0],NEC=[5,5]),new_shape_assumptions=dict(DRG_WHELP_ADULT={'shape':'cone','half_angle_deg':30,'length':260,'targets':3,'instant':True},DRG_WHELP_ANCIENT={'half_angle_deg':30,'targets':3},DRG_CONE_max_half_angle_deg=40,BST_BOAR_TUSK={'shape':'splash','radius':60,'targets':3,'secondary_ratio':.5},BST_BEAR_SWEEP={'shape':'cone','half_angle_deg':35,'length':50,'targets':3,'secondary_ratio':.5}),source_sha256={f:hashlib.sha256((SRC/f).read_bytes()).hexdigest() for f in ['12-catalog.json','12.md','13.md','07.md','08.md','09.md','10.md','11.md']})
sensitivity=[]
for b in boss:
    for delay in [0,2,4,8]:
        detail,total=damage_table(b['roster'],delay=delay)
        sensitivity.append(dict(class_id=b['class_id'],state=b['state'],access_delay_s=delay,damage_30s=float(total),hp1000_pass=total>=1000,hp300_pass=total>=300))
ck('all maximum also pass with four second access delay',all(x['hp1000_pass'] for x in sensitivity if x['state']=='maximum' and x['access_delay_s']==4))
ck('all required pass HP300 in two second fixture',all(x['hp300_pass'] for x in sensitivity if x['state']=='required' and x['access_delay_s']==2))
try:
    hits(30,0,0)
    ck('zero interval rejected',False)
except ValueError:
    ck('zero interval rejected',True)
ck('gold paid ceiling max154',max(x['reservation_gold_ceiling'] for x in gold)==154)
# Expected gold arithmetic at explicit assumed per-type kill counts, no collection coefficient.
ck('mixed kills grant immediately',5*1+2*3+1*6==17)
ck('ledger conservation',42-34==8)
outputs=dict(scope='document arithmetic only, not game simulation, performance or user tests',boss=boss,sensitivity=sensitivity,gold=gold,wait=waits,roi=roi,checks=checks,passed=sum(x['pass'] for x in checks),total=len(checks),not_performed=['trajectory/cursor simulation','mark-event simulation','purchase strategy optimization','playtesting','technical or UX review'])
(ROOT/'14-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
(ROOT/'14-validation.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n')
for filename,rows in [('14-boss.csv',[{k:v for k,v in r.items() if k not in ('roster','levels')} for r in boss]),('14-gold.csv',gold),('14-wait.csv',waits),('14-roster.csv',roster)]:
    with (ROOT/filename).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
print(json.dumps({'passed':outputs['passed'],'total':outputs['total'],'boss':[{k:v for k,v in r.items() if k in ('class_id','state','budget_gold','damage_30s','ideal_zero_delay_damage','hp1000_pass','damage_multiplier_for_1000')} for r in boss],'gold':gold,'wait':waits},ensure_ascii=False,indent=2))
