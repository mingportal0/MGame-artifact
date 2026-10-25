"""G2 document-only conditional arithmetic; not a game simulation."""
from pathlib import Path
from fractions import Fraction as F
import json,csv,hashlib
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data): (A/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def table(name,rows):
 with (A/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
base=json.loads((A/'14-inputs.json').read_text()); roster=[r for r in base['roster'] if r['id'] in ['SUM_ELM_EMBER','SUM_ELM_SPARK']]
inputs={'document_id':'P1-22-BALANCE-v01','scope':'conditional arithmetic, no trajectories/users/game/performance','source_14_sha256':digest(A/'14-inputs.json'),'roster':roster,'T':'30','distance':'300','delays':['0','2','5'],'loss_fractions':['0','0.10','0.25'],'loss_rule':'floor(N*(1-q)) earliest opportunities retained separately per summon; no schedule reflow; not measured','states':{'A_unlock':{'power':3,'bloom':1,'spark':1,'cost':105},'A_max':{'power':3,'bloom':1,'spark':1,'radius':3,'supply':2,'cost':265},'B_bloom_unlock':{'power':3,'bloom':1,'spark':0,'cost':80},'B_spark_unlock':{'power':3,'bloom':0,'spark':1,'cost':85}},'hp_candidates':[300,600,1000]}
input_hash=hashlib.sha256(json.dumps(inputs,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
hits=[];summary=[]
for state,levels in inputs['states'].items():
 for delay in inputs['delays']:
  for q in inputs['loss_fractions']:
   events=[]
   for r in roster:
    if r['id']=='SUM_ELM_SPARK' and not levels['spark']:continue
    wind=F(str(r['windup_s']));period=wind+F(str(r['cooldown_s']));flight=F(inputs['distance'])/F(str(r['projectile_speed']))
    first=F(delay)+wind+flight; times=[];t=first
    while t<F(inputs['T']): times.append(t);t+=period
    retain=(len(times)*(1-F(q))).__floor__(); damage=F(str(r['base_damage']))*(1+F(1,10)*levels['power'])
    for n,t in enumerate(times):
     valid=n<retain
     hits.append(dict(state=state,delay_s=delay,q=q,summon=r['id'],opportunity=n+1,hit_t_exact=str(t),hit_t_s=float(t),retained=int(valid),damage_exact=str(damage if valid else 0)))
     if valid:events.append((t,r['id'],damage))
   events.sort();total=sum((d for _,_,d in events),F(0))
   for hp in inputs['hp_candidates']:
    cumulative=F(0);clear=None
    for t,s,d in events:
     cumulative+=d
     if cumulative>=hp:clear=t;break
    summary.append(dict(state=state,delay_s=delay,q=q,hp=hp,total_damage_exact=str(total),total_damage=float(total),conditional_clear=int(clear is not None),clear_t_exact=str(clear) if clear is not None else '',clear_t_s=float(clear) if clear is not None else '',margin_damage=float(total-hp)))
recovery=[]
for k in [0,1,2,5]:
 W=0
 for n in range(1,11):
  before=W;W+=k
  recovery.append(dict(case=f'supply_first_B{k}_D0',turn=n,reserved_basic=24,reserved_dense=12,assumed_generated_basic=24,assumed_generated_dense=12,assumed_cap_omitted=0,assumed_slot_omitted=0,assumed_killed_basic=k,assumed_killed_dense=0,grant=k,w_before=before,w_after=W,next_power_cost=10,shortfall=max(0,10-W),can_buy=int(W>=10),within_3_turns=int(n<=3 and W>=10)))
  if W>=10:break
checks=[]
def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
check('A unlock cost',sum([10,20,30,20,25])==105);check('max cost',105+15+30+45+20+50==265)
check('B costs',60+20==80 and 60+25==85)
check('source roster exactly two',len(roster)==2)
check('first impact',F('2')+F('0.2')+F(300,600)==F('2.7'))
check('no at T hits',all(F(r['hit_t_exact'])<30 for r in hits))
for d in inputs['delays']:
 for q in inputs['loss_fractions']:
  vals=[r['total_damage_exact'] for r in summary if r['delay_s']==d and r['q']==q and r['state'] in ['A_unlock','A_max']]
  check(f'unlock_max_identical_{d}_{q}',len(set(vals))==1)
for s,n,g in [(0,24,24),(1,36,60),(2,48,96)]:check(f'supply_s{s}',6*(4+2*s)==n and 24+6*2*s*3==g)
check('no600_clear',not any(r['conditional_clear'] for r in summary if r['hp']>=600))
table('22-boss-hits.csv',hits);table('22-boss-summary.csv',summary);table('22-recovery.csv',recovery)
dump('22-balance.json',{'inputs':inputs,'input_hash':input_hash,'results':summary,'recovery':recovery,'checks':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks)})
print(json.dumps({'checks':len(checks),'passed':sum(c['passed'] for c in checks),'hit_rows':len(hits),'summary_rows':len(summary),'recovery_rows':len(recovery),'baseline':[r for r in summary if r['state'] in ['A_unlock','B_bloom_unlock'] and r['delay_s']=='2' and r['q'] in ['0','0.25']]},ensure_ascii=False))
assert all(c['passed'] for c in checks)
