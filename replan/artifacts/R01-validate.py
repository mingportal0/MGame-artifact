"""R01 document/allocation checker; not game code or economy simulation.
Usage: python R01-validate.py [--sources-dir COMPANY/decisions]
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--sources-dir', type=Path)
args = parser.parse_args()
base = Path(__file__).resolve().parent
checks = []

def check(name, condition):
    checks.append({'check': name, 'passed': bool(condition)})

text = (base / 'R01.md').read_text(encoding='utf-8')
data = json.loads((base / 'R01-data.json').read_text(encoding='utf-8'))
trace = json.loads((base / 'R01-trace.json').read_text(encoding='utf-8'))
rows = data['categories']
stages = data['stages']
check('proposal status, not adopted', data['status'] == 'proposal_not_adopted' and '상태: draft' in text)
check('no detailed catalogue claimed', data['detailed_catalogue_count'] == 0 and '실제 항목 수는0개 작성' in text)
check('six unique category owners', len(rows) == len({r['id'] for r in rows}) == 6)
check('independent target 100', sum(r['independent'] for r in rows) == data['independent_slot_target'] == 100)
check('behavior total 56', sum(r['behavior'] for r in rows) == 56)
check('numeric total 44', sum(r['numeric'] for r in rows) == 44)
check('variants do not inflate count', data['variant_added_to_target'] == 0)
check('repeat levels do not inflate count', data['repeat_levels_added_to_target'] == 0)
for r in rows:
    check(r['id'] + ': B+N=I', r['behavior'] + r['numeric'] == r['independent'])
    check(r['id'] + ': stages sum=I', len(r['stages']) == 4 and sum(r['stages']) == r['independent'])
    check(r['id'] + ': nonnegative integer budgets', all(type(n) is int and n >= 0 for n in [r['independent'],r['behavior'],r['numeric'],*r['stages']]))
    table = '| ' + r['name'] + ' | ' + ' | '.join(str(n) for n in [r['independent'],r['behavior'],r['numeric'],*r['stages']]) + ' |'
    check(r['id'] + ': markdown matches JSON allocation', table in text)
check('three allied elements only', {r['id'] for r in rows[3:]} == {'fire','lightning','ice'})
check('four unique roadmap stages', len(stages) == len({s['id'] for s in stages}) == 4)
prev = 0
previous_threshold = -1
for i,s in enumerate(stages):
    check(s['id'] + ': column inventory matches', sum(r['stages'][i] for r in rows) == s['new_inventory'] == 25)
    check(s['id'] + ': cumulative inventory', prev + s['new_inventory'] == s['total_inventory'])
    check(s['id'] + ': threshold fits previous inventory', 0 <= s['minimum_owned'] <= prev)
    check(s['id'] + ': monotonic threshold', s['minimum_owned'] > previous_threshold)
    check(s['id'] + ': threshold documented', ('k>=' + str(s['minimum_owned'])) in text)
    prev = s['total_inventory']
    previous_threshold = s['minimum_owned']
check('roadmap final inventory equals target', prev == data['independent_slot_target'])
# All count states are structurally reachable if purchases are affordable and have no extra prerequisites.
# This is deliberately NOT a check of actual 100-item prerequisites, prices, kills or play time.
k = 0
for _ in range(data['independent_slot_target']):
    inventory = max(s['total_inventory'] for s in stages if k >= s['minimum_owned'])
    check('count-only progression from k=' + str(k), k < inventory)
    k += 1
check('count-only path reaches 100', k == 100)
criteria = trace['criteria']
check('17 unique latest criteria', len(criteria) == len({c['id'] for c in criteria}) == 17)
check('criteria C01-C17 complete', {c['id'] for c in criteria} == {f'C{i:02d}' for i in range(1,18)})
source_fingerprints = {}
for c in criteria:
    check(c['id'] + ': trace row in document', '| ' + c['id'] + ' |' in text)
    check(c['id'] + ': sections exist', all(re.search(r'^## ' + str(s) + r'\.', text, re.M) for s in c['sections']))
    if args.sources_dir:
        source = args.sources_dir / c['source']
        lines = source.read_text(encoding='utf-8').splitlines()
        check(c['id'] + ': exact source line anchor', c['anchor'] in lines[c['line'] - 1])
        source_fingerprints[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
for uid in range(1,10):
    check(f'U{uid:02d} unresolved ownership documented', f'| U{uid:02d} |' in text)
for term in ['즉시 자동지급','커서','30초','상호배타','선택 종료','자동 종료하지 않음','게임코드','R02~15 blocked','실험은 제안이며 실행하지 않았다','이전5항목/69항목 수치 전용 불가']:
    check('boundary text: ' + term, term in text)
for term in ['catalogue_independence','actual_prerequisite_graph','natural_income','prices','all_purchase_orders','target_time','fun','ux','performance','cost']:
    check('unproven scope: ' + term, term in data['not_proven'])
# No raw Slack user/channel IDs, chat timestamps, home paths or obvious credentials in review files.
patterns = [r'xox[baprs]-[A-Za-z0-9-]+',r'gh[pousr]_[A-Za-z0-9]{20,}',r'AKIA[0-9A-Z]{16}',r'-----BEGIN .*PRIVATE KEY',r'\b[UC]0[A-Z0-9]{8,}\b',r'/home/[^/]+/',r'\b1792\d{6}\.\d+\b']
for name in ['R01.md','R01-data.json','R01-trace.json']:
    content = (base / name).read_text(encoding='utf-8')
    check(name + ': review privacy screening', not any(re.search(p,content) for p in patterns))
inputs = {}
for name in ['R01.md','R01-data.json','R01-trace.json','R01-validate.py']:
    inputs[name] = hashlib.sha256((base/name).read_bytes()).hexdigest()
result = {'kind':'document_arithmetic_trace_and_count_only_roadmap','sources_checked':bool(args.sources_dir),'source_fingerprints':source_fingerprints,'inputs':inputs,'checks':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks),'failed':[c for c in checks if not c['passed']],'not_verified':data['not_proven']}
(base/'R01-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['kind','sources_checked','passed','total','failed','not_verified']},ensure_ascii=False,indent=2))
sys.exit(0 if not result['failed'] else 1)
