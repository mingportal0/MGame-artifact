from pathlib import Path
import json,hashlib,sqlite3,re,shutil
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts');W=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((W/'22-resume-baseline.json').read_text());base.pop('22.md')
for n in ['22-validate.py','22-resolve.py','22-collaborate.py']:
 shutil.copy2(W/n,A/n)
reviews=[];cli=json.loads((A/'22-cli-provenance.json').read_text())
for p in ['mia','sam']:
 review=json.loads((A/f'22-review-{p}.json').read_text());resp=(A/f'22-response-{p}.txt').read_text()
 sid=review.get('session_id');session_match=re.findall(r'session_id:\s*(\S+)',resp)
 if not sid or sid=='모르겠음':sid=session_match[-1]
 db=sqlite3.connect(f'file:/home/mj/.hermes/profiles/{p}/state.db?mode=ro',uri=True);db.row_factory=sqlite3.Row
 row=db.execute('select id,source,profile_name,model,started_at,ended_at,tool_call_count from sessions where id=?',(sid,)).fetchone()
 counts=dict(db.execute('select role,count(*) from messages where session_id=? group by role',(sid,)).fetchall());db.close()
 reviews.append({'profile':p,'session_id':sid,'target_sha256':review['target_sha256'],'exit_code':next(r['exit_code'] for r in cli if r['profile']==p),'session_metadata':dict(row) if row else None,'message_role_counts':counts,'verified_session':bool(row and counts.get('tool',0)>0 and row['ended_at'] and sid in resp),'hashes':{n:sha(A/n) for n in [f'22-review-{p}.json',f'22-review-{p}.md',f'22-response-{p}.txt']},'source_warning':'Use actual CLI -p, profile-specific DB and injected-profile statement; inherited environment alone is not identity proof'})
(A/'22-review-index.json').write_text(json.dumps({'document_id':'P1-22-REVIEW-INDEX-v01','target_sha256':sha(A/'22.md'),'reviews':reviews,'previous_failure':'22-response-*-attempt1.txt preserved HTTP429; not review evidence'},ensure_ascii=False,indent=2)+'\n')
(A/'22-manifest.json').write_text(json.dumps({'document_id':'P1-22-GDD-v01','status':'review_not_approved','document_sha256':sha(A/'22.md'),'preserved_baseline':base,'approval':'D-20261025-P1-22-EXEC permits22 only; finalGDD/G3/23 not approved','scope':'planning documents and conditional arithmetic, not executable game','not_performed':['game/prototype/project','real user or render/performance test','spend/contact/external publication','23 execution/approval','README/plan edits']},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(reviews,ensure_ascii=False,indent=2))
