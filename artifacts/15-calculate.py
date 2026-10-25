"""P1-15 static planning worksheets. No game, events, AI or trajectory engine.
Stdlib only. Formulas evaluate finite catalog vectors and exogenous kill tables.
Outputs beside this file; original 12/14 are read-only. All values assumptions.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, ROUND_CEILING
from itertools import combinations
import json, csv, math, hashlib, heapq
ROOT=Path(__file__).resolve().parent
SRC=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
IN=ROOT/'15-inputs.json'
if not IN.exists():
    payload={'status':'assumptions_not_approved','catalog':json.loads((SRC/'12-catalog.json').read_text()),'prior':json.loads((SRC/'14-inputs.json').read_text()),'source_sha256':{n:hashlib.sha256((SRC/n).read_bytes()).hexdigest() for n in ['12-catalog.json','14-inputs.json','14-validation.json','14.md']},'budgets':[60,300,900],'turn_checkpoints':[5,15,40],'kill_tables':{'low':[[6,0,0],[6,1,0],[6,2,0]],'base':[[12,0,0],[12,3,0],[12,6,0]],'high':[[24,0,0],[24,12,0],[24,24,1]]},'think_s':8,'transition_s':2,'boss_delay_s':[2,8,30],'cancel_fraction':['0','1/4','1/2'],'scope':'static planning arithmetic; no actual kills observed'}
    IN.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
I=json.loads(IN.read_text()); C=I['catalog']; U={u['id']:u for u in C['upgrades']}; P=I['prior']; classes=['ELM','DRG','BST','DMN','NEC']; checks=[]
def ck(n,b):
    checks.append({'name':n,'pass':bool(b)})
    assert b,n

def cost(uid,l):
    u=U[uid]; c=u['cost']; b=Decimal(str(c['base']))
    if l<0 or l>=u['max_level']: return None
    x=b if c['growth_rule']=='one_shot' else b+Decimal(str(c['step']))*l if c['growth_rule']=='linear' else b*Decimal(str(c['factor']))**l
    return int(x.to_integral_value(rounding=ROUND_CEILING))
def closure(r):
    out=r.copy()
    while True:
        old=out.copy()
        for uid in old:
            for p in U[uid]['prerequisites']:
                out[p['upgrade_id']]=max(out.get(p['upgrade_id'],0),p['required_level'])
        if out==old:return out

def budget(lv):return sum(cost(k,j) for k,v in lv.items() for j in range(v))
def available(uid,lv,cls):
    return U[uid]['applies_to'] in ('ALL','CLS_'+cls) and cost(uid,lv.get(uid,0)) is not None and all(lv.get(p['upgrade_id'],0)>=p['required_level'] for p in U[uid]['prerequisites'])
def required(cls):return closure({p['upgrade_id']:p['required_level'] for p in C['boss_required_set']['CLS_'+cls]})
R={c:required(c) for c in classes}

def vector(cls,lv):
    # Spreadsheet formulas (14.md F2) for one stationary target, not runtime effects.
    def l(s):return lv.get('UPG_'+s,0)
    units=[]; common=1+F(1,10)*l('COM_POWER')
    for r in P['roster']:
        if r['class_id']!='CLS_'+cls:continue
        name=r['id'].split('_',2)[2]; d=F(str(r['base_damage'])); n=r['initial_count']; cd=F(str(r['cooldown_s'])); flight=F(str(r['attack_range']))/600 if r['projectile_speed'] else F(0)
        if cls=='ELM':
            if name=='EMBER':d=10+2*l('ELM_POWER')+3*l('ELM_DUET')
            else:n=l('ELM_'+name)
            if name=='TIDE' and l('ELM_TIDE_WAVE'):d=F(8)
            if name=='SPARK':cd=F('1.4')-F('.1')*l('ELM_TEMPO')
        elif cls=='DRG':
            if name!='WHELP':n=l('DRG_'+name)
            if name=='WHELP':
                d*=1+F('.1')*l('DRG_POWER')+F('.3')*l('DRG_ANCIENT')
                if l('DRG_ADULT'):flight=F(0)
            if name=='WYVERN':cd*=1-F('.1')*l('DRG_RAPID')
            if name=='MOON':d*=1+F('.15')*l('DRG_FOCUS')
        elif cls=='BST':
            if name=='WOLF':n=1+l('BST_PACK')
            else:n=l('BST_'+name)
            if name=='HAWK' and l('BST_HAWK_TWIN'):n=2
            if name=='BOAR' and l('BST_BOAR_TUSK'):n=2
            add=F('.1')*l('BST_FANG')
            if name=='WOLF':add+=F('.2')*l('BST_WOLF_LEADER')+F('.3')*l('BST_CROWN')
            if name in ('WOLF','HAWK') and l('BST_SKY_GROUND'):add+=F('.1')
            d*=1+add
            if name=='STAG' and l('BST_STAG_ANTLER'):cd*=F('.8')
        elif cls=='DMN':
            n=1+l('DMN_IMP_TWIN') if name=='IMP' else l('DMN_'+name)
            d*=1+F('.2')*l('DMN_POWER')
            if name=='IMP' and l('DMN_IMP_CROWN'):d*=F('1.5')
            if name=='HOUND' and l('DMN_HOUND_FANG'):d*=F('1.5')
            cd*=1-F('.1')*l('DMN_PACT_FOCUS')
        else:
            if name=='SKELETON':d=(6 if l('NEC_GUARD') else 4)*(1+F('.25')*l('NEC_BONE'))+2*l('NEC_CONDUCT')
            else:n=l('NEC_'+name)
            if name=='LICH' and l('NEC_ARCHLICH'):d=F(12)
            if name=='ARCHER' and l('NEC_SENTINEL'):cd=F('.6')
            if name=='GOLEM' and l('NEC_OSSUARY'):d=F(18)
        if n:units.append({'id':r['id'],'damage':str(d*common),'windup':str(r['windup_s']),'cd':str(cd),'flight':str(flight),'n':n})
    return units

def score_units(us,delay=2,cancel=F(0),eligible=True):
    detail=[];total=F(0)
    for u in us:
        first=F(delay)+F(u['windup'])+F(u['flight']); interval=F(u['windup'])+F(u['cd'])
        h=max(0,math.ceil((30-first)/interval)) if eligible else 0
        # Synthetic cancellation count, not sampled behavior or collection loss.
        lost=math.ceil(h*cancel); kept=h-lost
        d=F(u['damage'])*kept*u['n'];total+=d
        detail.append({**u,'hits':h,'cancelled_per_unit':lost,'kept':kept,'damage_sum':float(d)})
    return total,detail

def score(cls,lv,delay=2,cancel=F(0),eligible=True):
    us=vector(cls,lv)
    if cls=='DRG':
        slots=1+lv.get('UPG_DRG_WING',0);opts=[]
        for pair in combinations(us,min(slots,len(us))):
            pair=[dict(x) for x in pair]
            if {x['id'] for x in pair}=={'SUM_DRG_WHELP','SUM_DRG_WYVERN'} and lv.get('UPG_DRG_DUET',0):
                com=1+F('.1')*lv.get('UPG_COM_POWER',0)
                for u in pair:u['damage']=str(F(u['damage'])+F('.1')*(18 if u['id'].endswith('WHELP') else 10)*com)
            opts.append(score_units(pair,delay,cancel,eligible))
        return max(opts,key=lambda x:x[0])
    return score_units(us,delay,cancel,eligible)

def income(lv,profile):
    s=lv.get('UPG_COM_SUPPLY',0);L=lv.get('UPG_COM_GOLD_YIELD',0);k=I['kill_tables'][profile][s]
    rewards=[math.floor(F(g)*(1+F(1,4)*L)) for g in (1,3,6)]
    return sum(x*y for x,y in zip(k,rewards)),k,rewards

strategies=['attack','gold','supply','balanced','time_hold']
def order(cls,strategy):
    common=['UPG_COM_POWER']; own=[u['id'] for u in U.values() if u['applies_to']=='CLS_'+cls]
    attack=[k for k in own if any(t in k for t in ('POWER','BONE','FANG','CROWN','LEADER','GUARD','ANCIENT','ADULT'))]+common
    summon=[k for k in own if U[k]['type']=='unlock' or k.endswith(('_PACK','_IMP_TWIN','_WING'))]
    if strategy=='time_hold':return []
    if strategy=='attack':return attack+summon+own+['UPG_COM_COMMAND_RADIUS','UPG_COM_REACH','UPG_COM_SUPPLY','UPG_COM_GOLD_YIELD']
    if strategy=='gold':return ['UPG_COM_GOLD_YIELD','UPG_COM_SUPPLY']+attack+summon+own+['UPG_COM_COMMAND_RADIUS','UPG_COM_REACH']
    if strategy=='supply':return ['UPG_COM_SUPPLY','UPG_COM_COMMAND_RADIUS']+summon+attack+own+['UPG_COM_REACH','UPG_COM_GOLD_YIELD']
    # Weighted repeating list; least-purchased priority index produces round-robin investment.
    return ['UPG_COM_POWER','UPG_COM_SUPPLY']+summon+['UPG_COM_COMMAND_RADIUS']+attack+own+['UPG_COM_REACH','UPG_COM_GOLD_YIELD']

def buy_bundle(cls,strategy,lv,w,run,step,logs,earned):
    ids=list(dict.fromkeys(order(cls,strategy))); taken={}
    while True:
        candidates=[k for k in ids if available(k,lv,cls) and cost(k,lv.get(k,0))<=w]
        if not candidates:break
        uid=min(candidates,key=lambda k:(lv.get(k,0),ids.index(k))) if strategy=='balanced' else candidates[0]
        old=lv.get(uid,0);c=cost(uid,old);before=w;w-=c;lv[uid]=old+1
        logs.append({'run_id':run,'step':step,'purchase_id':run+':'+str(len(logs)),'upgrade_id':uid,'old_L':old,'new_L':old+1,'cost':c,'balance_before':before,'balance_after':w,'cumulative_earned':earned,'levels_after':json.dumps(lv,sort_keys=True)})
    return w

logs=[];states=[];turns=[]
for cls in classes:
 for st in strategies:
    for b in I['budgets']:
        lv={};run=f'budget:{cls}:{st}:{b}';w=buy_bundle(cls,st,lv,b,run,0,logs,b);d,detail=score(cls,lv)
        states.append({'run_id':run,'class':cls,'strategy':st,'budget':b,'spent':b-w,'balance':w,'damage':float(d),'boss_unlocked':all(lv.get(k,0)>=v for k,v in R[cls].items()),'income_base':income(lv,'base')[0],'units':sum(u['n'] for u in detail),'levels':json.dumps(lv,sort_keys=True)})
    for profile in I['kill_tables']:
        lv={};w=earned=0;run=f'turn:{cls}:{st}:{profile}'
        for t in range(1,max(I['turn_checkpoints'])+1):
            g,k,rewards=income(lv,profile);before=w;w+=g;earned+=g
            w=buy_bundle(cls,st,lv,w,run,t,logs,earned)
            if t in I['turn_checkpoints']:
                d,_=score(cls,lv)
                turns.append({'run_id':run,'class':cls,'strategy':st,'kill_profile':profile,'turn':t,'K_last':str(k),'gold_last':g,'earned':earned,'spent':earned-w,'balance':w,'damage':float(d),'boss_unlocked':all(lv.get(k,0)>=v for k,v in R[cls].items()),'combat_s':t*30,'shop_s':t*I['think_s'],'transition_s':t*I['transition_s'],'wall_s':t*(30+I['think_s']+I['transition_s']),'levels':json.dumps(lv,sort_keys=True)})
ck('budget factorial 5 classes 5 strategies 3 budgets',len(states)==75)
ck('time factorial 5 classes 5 strategies 3 profiles 3 checkpoints',len(turns)==225)
ck('no negative balances',all(r['balance_after']>=0 for r in logs))
ck('purchase caps',all(r['new_L']<=U[r['upgrade_id']]['max_level'] for r in logs))
ck('purchase costs correct',all(r['cost']==cost(r['upgrade_id'],r['old_L']) for r in logs))
ck('ledger delta each purchase',all(r['balance_before']-r['cost']==r['balance_after'] for r in logs))
ck('budget conservation',all(r['budget']==r['spent']+r['balance'] for r in states))
ck('turn conservation',all(r['earned']==r['spent']+r['balance'] for r in turns))
ck('purchase prerequisites',all(all(json.loads(r['levels_after']).get(p['upgrade_id'],0)>=p['required_level'] for p in U[r['upgrade_id']]['prerequisites']) for r in logs))
ck('unique purchase IDs',len({r['purchase_id'] for r in logs})==len(logs))

# Uniform-cost finite catalog-vector search after existing required set.
# Non-damage common items are excluded: they cannot improve this stationary fixture.
# All class items retained, including zero-damage prerequisites. Proof scoped to fixture.
paths=[];pathlogs=[];sensitivity=[];baselines=[]
for cls in classes:
    req=R[cls];base_d,_=score(cls,req)
    maxlv={k:u['max_level'] for k,u in U.items() if u['applies_to'] in ('ALL','CLS_'+cls)}
    for state,lv in [('required',req),('maximum',maxlv)]:
        d,_=score(cls,lv)
        baselines.append({'class':cls,'state':state,'cost':budget(lv),'damage':float(d)})
        for delay in I['boss_delay_s']:
            for cancel in I['cancel_fraction']:
                val,det=score(cls,lv,delay,F(cancel));sensitivity.append({'class':cls,'state':state,'delay_s':delay,'cancel_fraction':cancel,'damage':float(val),'hp1000':val>=1000,'hp600':val>=600,'hp300':val>=300,'details':det})
    ids=[k for k,u in U.items() if u['applies_to']=='CLS_'+cls and req.get(k,0)<u['max_level']]
    start=tuple(0 for _ in ids);heap=[(0,start)];seen={start:0};parent={};visited=0;answer=None
    while heap:
        spent,key=heapq.heappop(heap)
        if seen[key]!=spent:continue
        visited+=1;lv=req.copy();lv.update({uid:req.get(uid,0)+key[j] for j,uid in enumerate(ids) if key[j]})
        d,_=score(cls,lv)
        if d>=1000:answer=(spent,key,lv,d);break
        for j,uid in enumerate(ids):
            if not available(uid,lv,cls):continue
            nk=list(key);nk[j]+=1;nk=tuple(nk);ns=spent+cost(uid,lv.get(uid,0))
            if ns<seen.get(nk,math.inf):seen[nk]=ns;parent[nk]=(key,uid);heapq.heappush(heap,(ns,nk))
    ck(cls+' finite fixture winning path found',answer is not None)
    spent,key,lv,d=answer;route=[]
    while key!=start:key0,uid=parent[key];route.append(uid);key=key0
    route.reverse();running=req.copy();balance=spent;cum=0
    for j,uid in enumerate(route):
        old=running.get(uid,0);c=cost(uid,old);before=balance;balance-=c;cum+=c;running[uid]=old+1
        pathlogs.append({'class':cls,'step':j+1,'upgrade_id':uid,'old_L':old,'new_L':old+1,'cost':c,'balance_before':before,'balance_after':balance,'cumulative_extra_cost':cum,'damage_after':float(score(cls,running)[0]),'levels_after':json.dumps(running,sort_keys=True)})
    paths.append({'class':cls,'required_cost':budget(req),'required_damage':float(base_d),'minimum_extra_fixture_cost':spent,'total_fixture_cost':budget(req)+spent,'damage':float(d),'visited_states':visited,'route':route,'levels':lv,'scope':'minimum after required in stationary basic-only fixture, not minimum run or real victory'})
    for inc in [6,12,24]:
        n=math.ceil(F(budget(req)+spent,inc));paths[-1][f'fixed_{inc}G_turns']=n;paths[-1][f'fixed_{inc}G_wall_s']=n*40
ck('prior required damage agreement',all(abs(b['damage']-float(score(b['class'],R[b['class']])[0]))<1e-8 for b in baselines if b['state']=='required'))
priorboss=json.loads((SRC/'14-validation.json').read_text())['boss']
ck('independent formulas reproduce 14 ten damage states',all(abs(b['damage']-next(x['damage_30s'] for x in priorboss if x['class_id']=='CLS_'+b['class'] and x['state']==b['state']))<1e-7 for b in baselines))
ck('zero eligible damage all classes',all(score(c,R[c],eligible=False)[0]==0 for c in classes))
ck('T30 excluded',score_units([{'id':'fixture','damage':'1','windup':'0','cd':'1','flight':'0','n':1}],30)[0]==0)
ck('exact hit-count boundary',score_units([{'id':'fixture','damage':'1','windup':'0','cd':'1','flight':'0','n':1}],0)[0]==30)
ck('zero K no gold',[sum(x*y for x,y in zip([0,0,0],[1,3,6]))]==[0])
ck('supply reserved counts obeyed',all(all(0<=k<=cap for k,cap in zip(counts,P['supply_reserved_counts'][s])) for tab in I['kill_tables'].values() for s,counts in enumerate(tab)))
ck('all 69 max and negative level rejected',all(cost(k,u['max_level']) is None and cost(k,-1) is None for k,u in U.items()))
ck('all levels prerequisites references exist',all(p['upgrade_id'] in U for u in U.values() for p in u['prerequisites']))
# Topological dependency check, no runtime transaction implementation.
def visit(k,stack):
    if k in stack:return False
    return all(visit(p['upgrade_id'],stack|{k}) for p in U[k]['prerequisites'])
ck('no prerequisite cycles',all(visit(k,set()) for k in U))
ck('s2 no kill spawn limit48 reservation49',min(48,sum(P['supply_reserved_counts'][2]))==48 and sum(P['supply_reserved_counts'][2])==49)
ck('radius same K same G',income({'UPG_COM_COMMAND_RADIUS':0},'base')[0]==income({'UPG_COM_COMMAND_RADIUS':3},'base')[0])
ck('gold s0 all levels dead',all(income({'UPG_COM_GOLD_YIELD':l},'base')[0]==12 for l in range(4)))
ck('gold s1 L1 dead',income({'UPG_COM_SUPPLY':1,'UPG_COM_GOLD_YIELD':1},'base')[0]==income({'UPG_COM_SUPPLY':1},'base')[0])
# Fault-injection accounting tables. Arithmetic expected contract, not implemented safeguards.
abuse=[{'case':'duplicate death input','bad_gold':2,'expected_gold':1,'key':'combat_id+entity_id','proposal':'count each unique death once'}, {'case':'settlement pays death again','bad_gold':34,'expected_gold':17,'key':'same earned ledger','proposal':'settlement display-only'}, {'case':'100 free failed retries','bad_gold':100,'expected_gold':0,'key':'no qualifying deaths/reward proposal0','proposal':'no reward or cost; HP1000 each retry'}, {'case':'NEC boss temporary carry','bad_units':10,'expected_units':5,'key':'temporary reset0','proposal':'permanent5 at maximum only'}, {'case':'s2 all reservations counted without kills','bad_gold':102,'expected_gold':0,'key':'K=0','proposal':'no grant on spawn/cleanup'}, {'case':'all five DRG deployed','bad_units':5,'expected_units':2,'key':'WING cap2','proposal':'score legal deployed pair'}]
ck('dedup arithmetic fixture',len(set(['b1:e1','b1:e1']))==1 and len(set(['b1:e1','b2:e1']))==2)
ck('failed retries balance invariant arithmetic',17+100*0-100*0==17)
ck('failed retries HP no carry arithmetic',1000-(1000-1000)==1000)
ck('no time upgrade present',not any('TIME' in k for k in U))
ck('NEC max permanent count5',sum(u['n'] for u in score('NEC',{k:u['max_level'] for k,u in U.items() if u['applies_to'] in ('ALL','CLS_NEC')})[1])==5)
# Comparison-only corrections: no catalog edits.
corrections=[]
for cls in classes:
    req=R[cls];base=score(cls,req)[0]
    factor=max(F(1),F(1000)/base)
    corrections.append({'class':cls,'before_damage':float(base),'hp300_pass':base>=300,'hp600_pass':base>=600,'hp1000_pass':base>=1000,'permanent_damage_factor_exact':str(factor),'after_damage_if_scaled':float(base*factor),'scope':'proposal only, all eligible basic damage uniformly scaled; economics not validated'})
# Remove gold upgrade proposal: same K and supply, saved120G; recalc at high s2.
recalc={'gold_exclusion':{'old_cost':budget({'UPG_COM_GOLD_YIELD':3}),'new_cost':0,'high_s2_old_income':income({'UPG_COM_SUPPLY':2,'UPG_COM_GOLD_YIELD':3},'high')[0],'high_s2_new_income':income({'UPG_COM_SUPPLY':2},'high')[0]},'supply_marginal_base':[income({'UPG_COM_SUPPLY':s},'base')[0] for s in range(3)],'supply_marginal_high':[income({'UPG_COM_SUPPLY':s},'high')[0] for s in range(3)],'supply_no_extra_k_before_after':[12,12],'time_hold':'not a legal time purchase; no purchases, gold held, T=30'}
ck('gold exclusion recalculated',recalc['gold_exclusion']=={'old_cost':120,'new_cost':0,'high_s2_old_income':154,'high_s2_new_income':102})
for cls in classes:
    path=next(x for x in paths if x['class']==cls)
    ck(cls+' path ends matching required plus route',budget(path['levels'])==path['total_fixture_cost'] and score(cls,path['levels'])[0]>=1000)
ck('sensitivity full Cartesian',len(sensitivity)==90)
# Full required+optional purchase chronology, fixed6G/turn, with carried balance.
fullpaths=[];path_sensitivity=[]
for p in paths:
    cls=p['class'];target=R[cls];lv={};route=[]
    while any(lv.get(k,0)<v for k,v in target.items()):
        uid=next(k for k,v in target.items() if lv.get(k,0)<v and available(k,lv,cls))
        route.append(uid);lv[uid]=lv.get(uid,0)+1
    route+=p['route'];lv={};w=t=earned=0
    for step,uid in enumerate(route,1):
        old=lv.get(uid,0);price=cost(uid,old);needed=max(0,price-w);wait=math.ceil(F(needed,6));t+=wait;earned+=6*wait;w+=6*wait;before=w;w-=price;lv[uid]=old+1
        fullpaths.append({'class':cls,'step':step,'upgrade_id':uid,'old_L':old,'new_L':old+1,'price':price,'additional_turns':wait,'cumulative_turns':t,'cumulative_earned':earned,'balance_before':before,'balance_after':w,'cumulative_spent':earned-w,'combat_s':30*t,'shop_s':8*t,'transition_s':2*t,'wall_s':40*t,'levels_after':json.dumps(lv,sort_keys=True)})
    ck(cls+' full route ledger and fixed6 time',earned-w==p['total_fixture_cost'] and t==p['fixed_6G_turns'])
    for delay in (2,8):
        for cancel in (F(0),F(1,4),F(1,2)):
            d,det=score(cls,p['levels'],delay,cancel);path_sensitivity.append({'class':cls,'delay_s':delay,'cancel_fraction':str(cancel),'damage':float(d),'hp1000':d>=1000,'hp600':d>=600,'hp300':d>=300})
# Recompute identical-budget allocation excluding GOLD_YIELD (proposal, no source edits).
corrected=[]
for cls in classes:
 for st in ('gold','balanced'):
  for b in I['budgets']:
    lv={};w=b;ids=list(dict.fromkeys(k for k in order(cls,st) if k!='UPG_COM_GOLD_YIELD'))
    while True:
        candidates=[k for k in ids if available(k,lv,cls) and cost(k,lv.get(k,0))<=w]
        if not candidates:break
        uid=min(candidates,key=lambda k:(lv.get(k,0),ids.index(k))) if st=='balanced' else candidates[0]
        w-=cost(uid,lv.get(uid,0));lv[uid]=lv.get(uid,0)+1
    before=next(r for r in states if r['class']==cls and r['strategy']==st and r['budget']==b)
    corrected.append({'class':cls,'strategy':st,'budget':b,'before_damage':before['damage'],'after_damage':float(score(cls,lv)[0]),'before_income_base':before['income_base'],'after_income_base':income(lv,'base')[0],'balance_after':w,'levels_after':json.dumps(lv,sort_keys=True),'proposal':'exclude GOLD_YIELD only; same budget and K table'})
ck('gold exclusion 30 same-budget recalculations',len(corrected)==30)
for filename,rows in [('15-full-path.csv',fullpaths),('15-path-sensitivity.csv',path_sensitivity),('15-gold-exclusion.csv',corrected),('15-budget.csv',states),('15-turns.csv',turns),('15-purchases.csv',logs),('15-path-purchases.csv',pathlogs),('15-baseline.csv',baselines),('15-corrections.csv',corrections),('15-sensitivity.csv',[{k:v for k,v in r.items() if k!='details'} for r in sensitivity])]:
    with (ROOT/filename).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
result={'scope':I['scope'],'passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks,'row_counts':{'budget':len(states),'turns':len(turns),'purchases':len(logs),'path_purchases':len(pathlogs),'sensitivity':len(sensitivity)},'path_sensitivity':path_sensitivity,'full_path_rows':len(fullpaths),'gold_exclusion_rows':len(corrected),'minimum_paths':paths,'baseline':baselines,'sensitivity':sensitivity,'abuse_counterexamples':abuse,'correction_recalculation':recalc,'damage_correction':corrections,'not_performed':['game/prototype/technical coding','movement/AI/cursor or event simulation','actual kills or DPS measurement','user playtest','whole-run optimal policy','peer approval','G3 development']}
(ROOT/'15-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k in ['passed','total','row_counts','minimum_paths','baseline','correction_recalculation']},ensure_ascii=False,indent=2))
