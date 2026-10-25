"""Structural cross-checks of P1-14 planning deliverables, no gameplay code."""
from pathlib import Path
import csv, json, re, hashlib
P=Path(__file__).resolve().parent
S=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts')
checks=[]
def check(name,cond):
    checks.append({'name':name,'pass':bool(cond)})
    if not cond: raise AssertionError(name)
a=json.loads((P/'14-inputs.json').read_text())
b=json.loads((P/'14-validation.json').read_text())
doc=(P/'14.md').read_text()
check('arithmetic result35/35',b['passed']==b['total']==35 and all(x['pass'] for x in b['checks']))
for stem,n in [('roster',25),('boss',10),('gold',12),('wait',15)]:
    rows=list(csv.DictReader((P/f'14-{stem}.csv').open()))
    check(f'CSV {stem} exactly {n} data rows',len(rows)==n)
check('40 sensitivity rows',len(b['sensitivity'])==40)
for k in range(1,7): check(f'formula F{k} present',f'### F{k}.' in doc)
check('all five classes have required+maximum states',len({(x['class_id'],x['state']) for x in b['boss']})==10)
check('25 source stat vectors unique',len(a['roster'])==len({x['id'] for x in a['roster']})==25)
for cls in ['ELM','DRG','BST','DMN','NEC']:
    r=next(x for x in b['boss'] if x['class_id']==f'CLS_{cls}' and x['state']=='required')
    m=next(x for x in b['boss'] if x['class_id']==f'CLS_{cls}' and x['state']=='maximum')
    check(f'{cls} table matches output damage/budgets',f"| {cls} |{r['budget_gold']}|{r['damage_30s']:.2f}|{r['ideal_zero_delay_damage']:.2f}|" in doc and f"|{m['budget_gold']}|{m['damage_30s']:.2f} |" in doc)
for name,h in a['source_sha256'].items():
    check(f'input snapshot still matches {name}',hashlib.sha256((S/name).read_bytes()).hexdigest()==h)
for target in re.findall(r'\]\(([^)]+)\)',doc):
    if not target.startswith(('http','https','#')): check('local link exists '+target,(P/target).resolve().is_file())
check('approval boundary explicit','G3 개발 미승인' in doc and '목표 플레이시간 확정' in doc)
check('failure runs disclosed','기대값84오기로exit1' in doc and '중복키도구오류exit1' in doc)
result=dict(scope='document package structure/source-snapshot verification, not game or player testing',passed=sum(x['pass'] for x in checks),total=len(checks),checks=checks,files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.glob('14*')) if p.is_file() and p.name not in ['14-package-validation.json','14-run-output.txt']})
(P/'14-package-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'total':result['total'],'files':sorted(result['files']),'scope':result['scope']},ensure_ascii=False,indent=2))
