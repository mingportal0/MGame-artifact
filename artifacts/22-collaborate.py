from pathlib import Path
import json,hashlib,os,subprocess,concurrent.futures,time
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts');W=Path(__file__).parent
h=hashlib.sha256((A/'22.md').read_bytes()).hexdigest()
def run(profile):
 prompt=f'''P1-22 카드 내부 실제 전문 재검토 요청입니다. 실제 {profile} 프로필로 실행되었습니다. 한국어 응답. 본 실행은 보드 카드 작업자가 아닌 한정된 내부 협업입니다. kanban lifecycle/완료/차단/새카드/메모리/설정변경/외부연락을 하지 마세요. 게임코드/프로토타입/에셋제작/사용자접촉 금지. 본문22 수정금지.
먼저 company/AGENTS.md와decisions/2026-10-25_phase1-p22-execution_approved_v01.md를 읽고, {A}/22.md (SHA256={h}), {A}/21-review-{profile}.md, {A}/21-defects.json, {A}/22-balance.json 와 필요시 CSV를 읽으세요. company 절대경로는 /home/mj/.hermes/company. 20/21 원본 보존. 환경변수 HERMES_PROFILE 표기가 다르면 실제 injected profile/SOUL/HERMES_HOME을 확인하고 불일치 기록; 정체성 합성 금지.
목적: 최종 review GDD Part1~10 보완의 담당 실제 재확인. 당신의 원문 지적ID({profile.upper()}-01 등) 각각 빠짐없이 검사하여 document_satisfied/partial_open/open 판정. MIA는 MIA01~09 및 JAMES03/H3·04노출·07H1, SAM은 SAM01~11 및 JAMES01/U07·05회복·06terminal 검토. James권고B집합/HP300은 B_BLOOM a2 q0에서299피해라 막힘이 남음, 승인된 수치나 재미로 인정금지. input/오차·과부하숫자·총비용 미정은 솔직히 남김. purchase B·복귀B·자산 인터페이스의 실제 동의/조건부/반대와 이유를 각각 명시. 표식정본/terminal 단계, 기존비용18~32 확약이 아닌지 확인.
산출물: {A}/22-review-{profile}.md 와 {A}/22-review-{profile}.json 두 신규파일만 생성. md에는 실제 session_id(주입된 값 또는 모르겠음), 실제프로필근거, 읽은대상SHA256, 질문별 답변, 각원문지적 판정/정확한22줄/근거/잔여·확인못한항목, 추가발견, 최종합의범위/미합의·대표결정/비실행. JSON schema: profile,session_id,target_sha256, findings 배열(각 id,verdict,location,reason,remaining), new_findings 배열, decisions 객체,not_performed 배열. findings는 본인 원문9 또는11건을 각각보존. verdict는 document_satisfied|partial_open|open. 문서수정은사용자/게임/성능/법률검증아님. 다른전문가동의추정금지. 15분 이내 끝내고 최종응답에 파일경로·핵심잔여·실제세션ID 보고.'''
 request=W/f'22-request-{profile}.txt';request.write_text(prompt)
 env=os.environ.copy()
 for k in list(env):
  if k.startswith('HERMES_KANBAN_'):env.pop(k,None)
 env['HERMES_HOME']=f'/home/mj/.hermes/profiles/{profile}';env['HERMES_PROFILE']=profile
 with (A/f'22-response-{profile}.txt').open('w') as out:
  p=subprocess.run(['hermes','-p',profile,'chat','--query-file',str(request),'--oneshot','-Q','--pass-session-id','--max-turns','35','--run-budget','850','--source','tool'],cwd=W,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=920)
 return {'profile':profile,'exit_code':p.returncode,'target_sha256':h}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 result=list(ex.map(run,['mia','sam']))
(A/'22-cli-provenance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
