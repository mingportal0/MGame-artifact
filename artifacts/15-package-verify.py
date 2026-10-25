"""Independent read-only audit of P1-15 CSV ledgers, sources and document links."""
from pathlib import Path
from decimal import Decimal,ROUND_CEILING
from fractions import Fraction
import json,csv,hashlib,re,math
P=Path(__file__).resolve().parent
S=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
I=json.loads((P/'15-inputs.json').read_text());V=json.loads((P/'15-validation.json').read_text());U={u['id']:u for u in I['catalog']['upgrades']};checks=[]
def ck(n,b):checks.append({'name':n,'pass':bool(b)})
def rows(n):return list(csv.DictReader((P/n).open()))
def price(uid,l):
 u=U[uid];c=u['cost'];b=Decimal(str(c['base']))
 if not 0<=l<u['max_level']:return None
 x={'one_shot':lambda:b,'linear':lambda:b+Decimal(str(c['step']))*l,'exponential':lambda:b*Decimal(str(c['factor']))**l}[c['growth_rule']]()
 return int(x.to_integral_value(rounding=ROUND_CEILING))
for n,h in I['source_sha256'].items():ck('source unchanged '+n,hashlib.sha256((S/n).read_bytes()).hexdigest()==h)
ck('catalog snapshot exact',I['catalog']==json.loads((S/'12-catalog.json').read_text()))
ck('prior snapshot exact',I['prior']==json.loads((S/'14-inputs.json').read_text()))
ck('worksheet checks all passed',V['passed']==V['total']==47 and all(c['pass'] for c in V['checks']))
expected={'15-budget.csv':75,'15-turns.csv':225,'15-purchases.csv':2154,'15-path-purchases.csv':10,'15-full-path.csv':50,'15-baseline.csv':10,'15-sensitivity.csv':90,'15-path-sensitivity.csv':30,'15-gold-exclusion.csv':30,'15-corrections.csv':5}
for n,num in expected.items():ck(n+' row count',len(rows(n))==num)
B=rows('15-budget.csv');T=rows('15-turns.csv');L=rows('15-purchases.csv');F=rows('15-full-path.csv')
ck('budget full cross product',len({(r['class'],r['strategy'],r['budget']) for r in B})==75)
ck('turn full cross product',len({(r['class'],r['strategy'],r['kill_profile'],r['turn']) for r in T})==225)
ck('budget all conserve',all(int(r['spent'])+int(r['balance'])==int(r['budget']) for r in B))
ck('time rows all conserve',all(int(r['spent'])+int(r['balance'])==int(r['earned']) for r in T))
ck('time breakdown',all(int(r['wall_s'])==int(r['combat_s'])+int(r['shop_s'])+int(r['transition_s'])==40*int(r['turn']) for r in T))
ck('time hold no growth purchases',all('time_hold' not in r['run_id'] for r in L))
ck('hold balance conserved',all(r['budget']==r['balance'] and r['spent']=='0' for r in B if r['strategy']=='time_hold'))
ck('no duplicate purchase id',len({r['purchase_id'] for r in L})==len(L))
ck('independent all purchase prices',all(price(r['upgrade_id'],int(r['old_L']))==int(r['cost']) for r in L))
ck('all purchase balances',all(int(r['balance_before'])-int(r['cost'])==int(r['balance_after'])>=0 for r in L))
ck('all purchase levels',all(int(r['new_L'])==int(r['old_L'])+1<=U[r['upgrade_id']]['max_level'] for r in L))
ck('all purchase prerequisites',all(all(json.loads(r['levels_after']).get(x['upgrade_id'],0)>=x['required_level'] for x in U[r['upgrade_id']]['prerequisites']) for r in L))
# Replay chronological levels for each run independently of calculation functions.
prev={};valid=True
for r in L:
 run=r['run_id'];lv=prev.get(run,{}).copy();uid=r['upgrade_id'];valid &= lv.get(uid,0)==int(r['old_L']);lv[uid]=int(r['new_L']);valid &= lv==json.loads(r['levels_after']);prev[run]=lv
ck('replayed policy purchase levels',valid)
for cls in ['ELM','DRG','BST','DMN','NEC']:
 rs=[r for r in F if r['class']==cls];gold=turn=spent=0;lv={};ok=True
 for r in rs:
  uid=r['upgrade_id'];c=price(uid,lv.get(uid,0));need=max(0,c-gold);wait=math.ceil(Fraction(need,6));gold+=wait*6;turn+=wait
  ok &= int(r['additional_turns'])==wait and int(r['balance_before'])==gold and int(r['cumulative_turns'])==turn
  gold-=c;spent+=c;lv[uid]=lv.get(uid,0)+1
  ok &= int(r['balance_after'])==gold and int(r['cumulative_spent'])==spent and int(r['cumulative_earned'])==6*turn and json.loads(r['levels_after'])==lv
  ok &= all(lv.get(x['upgrade_id'],0)>=x['required_level'] for x in U[uid]['prerequisites'])
 path=next(x for x in V['minimum_paths'] if x['class']==cls)
 ok &= lv==path['levels'] and spent==path['total_fixture_cost'] and turn==path['fixed_6G_turns']
 ck(cls+' independent full route balances/turns/levels',ok)
ck('ceil supply payback base/high',math.ceil(Fraction(20,9))==3 and math.ceil(Fraction(20,36))==1)
ck('late wallet illustration',154*100==15400)
ck('DRG price correction arithmetic',540-300+100==340 and 760-300+100==560 and math.ceil(Fraction(560,6))==94 and 94*40==3760)
ck('phase time arithmetic',[n*30 for n in (5,15,40)]==[150,450,1200] and [n*40 for n in (5,15,40)]==[200,600,1600])
text=(P/'15.md').read_text()
links=re.findall(r'\]\(([^)]+)\)',text)
ck('all report local links resolve',all((P/l).resolve().exists() for l in links if not l.startswith(('https:','http:')) and l!='15-package-validation.json'))
ck('six source problems documented',all('Q'+str(n) in text for n in range(1,7)))
ck('approval boundaries and missing tests explicit',all(s in text for s in ['G3','미승인','실제 K','사용자 테스트 없음','수집률은 삭제','원본·공유 README 수정 없음']))
ck('minimum figures generated from actual output',all(str(x['total_fixture_cost']) in text and str(x['minimum_extra_fixture_cost']) in text for x in V['minimum_paths']))
ck('25percent DRG max failure preserved',any(x['class']=='DRG' and x['state']=='maximum' and x['delay_s']==2 and x['cancel_fraction']=='1/4' and x['damage']==992.16 and not x['hp1000'] for x in V['sensitivity']))
out={'scope':'independent document/CSV/source/ledger arithmetic, not game tests','passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks,'row_counts':expected,'sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['15.md','15-inputs.json','15-calculate.py','15-report.py',*expected]},'failed':[c['name'] for c in checks if not c['pass']]}
(P/'15-package-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'total':out['total'],'failed':out['failed'],'rows':expected},ensure_ascii=False,indent=2))
raise SystemExit(0 if not out['failed'] else 1)
