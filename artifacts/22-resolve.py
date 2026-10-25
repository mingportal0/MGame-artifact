from pathlib import Path
import json,hashlib,collections
A=Path('/home/mj/.hermes/company/kanban/game-planning-phase1/artifacts');W=Path(__file__).parent
text=(A/'22.md').read_text();lines=text.splitlines();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def loc(needle):
 found=[i+1 for i,l in enumerate(lines) if needle in l]
 if not found:raise ValueError(needle)
 return '22.md L'+','.join(map(str,found))
# ID => correction location search, reason, residual, disposition exception if any
fixes={
'JAMES-01':('축소 보스 재계산의 전제','채택: 축소 ID/상태/정확 타격/HP별/합성손실을 새로 계산. 해금과 최대 동일 단일보스화력 확인.','치명 유지: B개화단독 a2 q0 피해299<HP300; 자연경제·실제손실/완주 미검증·대표HP/집합 선택 필요.'),
'JAMES-02':('CFG22 구성 정본','채택: AND A/대표성장 OR B/화력 C 논리식·가격·X/Y와 필수동기/장면기대 코딩 분리. B 권고.','높음 유지: B의 선택경로 도달성 반례. 집합 선택 대표 미승인. A에서 선택은 순서라는 한계.'),
'JAMES-03':('추가핵심veto','채택: 3종 총괄뿐 아니라 5ID 개인표·불변/반경오해veto·전원미식별 항목실패. 이해/만족/미적 분리.','실제 식별/대표품질 관찰 없음. 특정항목 미식별을 총괄지지로 숨기지 않음.'),
'JAMES-04':('노출순서는','채택: 자연경제 선행 B권고·각 participant 노출목록·H4질문이 H5도 오염함을 명시.','과제순서 실제 사용성 확인/접촉 미실행. 미노출 신규유입·유지율 일반화 금지.'),
'JAMES-05':('공급 선구매·진척 회복','채택: 공급 선구매 직후부터 다음화력까지 BASIC/DENSE 예약/가정생성/처치/지급/부족액 CSV. 3전투 회복가정/4중단사유 구별.','높음 유지: 외생K 현금흐름일뿐 실제 K/slot/집중 경로 미측정. 환불·선행·단계선택 미채택.'),
'JAMES-06':('C22-BATCH 공통','채택: 같은t 합산피해 뒤 terminal결정 우선·보스토큰/생성 이벤트 자체0. 일반동시사망 규칙 별도.','문서 정렬 제안·확장기능 미시험·U01 최소시각 미정. 정령 비활성으로 전체해결 간주금지.'),
'JAMES-07':('H1 지휘/관찰 재미','채택·측정안 명료화: 첫combat진행 t0 활성벽시계60초, 상점포함/준비·정지제외, 첫성공=유효지정 발사·처치별도. 도움/결측/실패 사례.','Mia/Sam 계측/과제 수용은 실제재검토만 반영. 접촉·관찰 미실행.'),
'MIA-01':('W03 현재 구성 바인딩','채택: W03 가까이에 역사집합 축소복사금지·A3조건/B2조건과 정확X 계산 정본.','원지적 A집합의 표시수용과 B집합 채택은 구별. 대표 집합 선택 미승인.'),
'MIA-02':('상점상태 산술예시','채택: rev10 전24/0/3/1부족, rev11 후4/1/3/21부족을 초기상태 포함 분리.','실제 UI 렌더·동기화 미시험.'),
'MIA-03':('접근성 상태표','채택: 기본/무음/모션축소/동시 정적대체·확대후보·긴문구/버튼도달·중심 경계표.','실제 대비/렌더/인지 미측정·해상도 지원확정 아님.'),
'MIA-04':('UX A 재진입요구','채택: B 새클릭 권고/갱신중 비활성·명령쌍·별개더블클릭 오구매 위험/측정 분리.','사용자우열 미판정·Sam 실제재검토 외 합의 추정금지.'),
'MIA-05':('과부하·복귀 상태표','채택: 정상/정지/재개가능/복구불가/반복/탈출 구별·보존문구 제한.','높음 유지: 측정임계치/안전경계/탈출 런경제 정책 미채택. 계속연타를 복구라고 하지 않음.'),
'MIA-06':('대표품질·납품·출처','채택: 제한 대표품질 묶음·상태/포맷/프레임 필드·인일 미산정 근거·담당 재개조건.','높음 유지: 품질/방식/사용권/제작량·인일 미정·실물 없음.'),
'MIA-07':('H3 자료표','채택: 정확5항목 전후·불변·입력/배치고정/공급예외·숫자숨김 정보·단일보스 오해 구분.','실제 화력/공급/전체H3 관찰 없음·3종지표를 5종으로 확대금지.'),
'MIA-08':('시작/복귀 대안','채택: 준비/재개준비/진행·시계0/새확인 소비·UI→필드 손실의 A/B 명시. B권고.','높음 유지: 추가절차/오차/원복귀비용 검토·대표 핵심변경 확인 전 미채택.'),
'MIA-09':('출처원장:','채택: asset별 제작자/URL/날짜/라이선스/수정배포/사용위치·폰트음향/미확인제한.','실물근접성/독자성/법률검토 미실행, 외부사용허가 아님.'),
'SAM-01':('U01 입력·시간 계약','채택: 수신순/시간/좌표세대/무효사유·정지·관측안밖안 보존/양끝만 보장한계·재생원장필드.','높음 유지: 매핑/지연/동일t 의미·장치시계 구체수치 미확정.'),
'SAM-02':('실제 시간단위','채택: 연속구간과 T/수명/접선/반사 경계 기대표, 고정60Hz 대체금지·수치 미정 명시.','높음 유지: 양자화/교차오차/최소t/갱신주기 미정으로 구현사양 고정불가.'),
'SAM-03':('C22-BATCH 공통','채택: 공통 순서에 만료/스냅샷/기본양수/ID→attack/합산/생존재적용/새t 정본+사례.','높음 잔여가능: 일반공격·효과 중복키 세부/수치 t·표식 예외 최신 실제 Sam응답 우선. 비활성이라해결이라고 하지 않음.'),
'SAM-04':('보스 사망이면 terminal','채택: 전체같은t피해합산후 terminal 먼저·허용보상1·보스토큰/생성 자체0·늦은death0.','문서정합 범위와 실제 기능검증 별개·최소t/보상0 대표미승인.'),
'SAM-05':('핵심 인터랙션 C22-PURCHASE','채택: 요청ID/세대/revision/상태 재검사·중복/결과불명·늦은응답/명령순서·입력취소 정본.','안전 의미제안·구현/저장복구 미증명. A/B UX우열 별도.'),
'SAM-06':('과부하·복귀 상태표','채택: 완결t배치 정지·접수큐보존/추가벽시계0·다른복구조건·중첩정지·반복탈출안.','높음 유지: 발동/해제 실제수치/원장복구/자기탈출경로 확정전 충분성보장불가.'),
'SAM-07':('CFG22 구성 정본','채택: 원ID보존+variant/schema/data/hash·override·포함/비활성/공급/집합·보존식.','A/B 미선택, 실제payload/검사기 구현없음. 별도선택 없이혼합금지.'),
'SAM-08':('축소 보스 재계산의 전제','채택: 전체값 복사없음·해금/최대/선택경로·첫타/비행/손실/HP표·입력지문.','높음 유지: 자연경제/실제전력여유/HP·집합 채택미승인. B개화단독치명잔여는JAMES01과중복주제.'),
'SAM-09':('필수자산레코드','채택: 논리앵커/margin과pivot/바운드 분리·사건읽기/대체표현·납품/권리 필드.','실제납품포맷/수량·Mia수용·Sam연결/비용확인 미정은실제응답에만근거.'),
'SAM-10':('개발인일 작업묶음 영향표','채택: 각과거묶음에데이터/유지/추가검증/재추정 연결·제외·5배/축소중복차감금지.','높음 유지: 현재확정견적/납기/기기성능 근거없음·아트미산정.'),
'SAM-11':('장기 런 정수·원장 정책','부분채택: 잘못된정수거부·몰래포화금지·세대/중복키/로그수명 구별·미정공개.','구체표현범위/초과/ID수명/관찰로그 용량실패/보존책임 미정. 정책결정·Sam확인필요.')}
original=json.loads((A/'21-defects.json').read_text())['findings']; results=[]
for r in original:
 needle,reason,remaining=fixes[r['id']]
 record={k:r[k] for k in ['id','title','reviewer','severity','owner','evidence_file','evidence_first_line']}
 record.update({'baseline_status':r['status'],'baseline_evidence_sha256':sha(A/r['evidence_file']),'disposition':'adopted_with_open_limits' if r['id']!='SAM-11' else 'partially_adopted_explicitly_deferred','reason':reason,'location':loc(needle),'reverification':'22-validate.py structure/provenance/independent arithmetic; real reviewer response below','remaining':remaining,'status':'partial_open','responsible_response':None})
 if r['reviewer']=='james':
  record['responsible_response']={'kind':'actual_parent_james_self_review_not_independent','target_sha256':sha(A/'22.md'),'response_file':'22-review-james.md','verdict':'partial_open','reason':reason,'remaining':remaining}
 else:
  path=A/f"22-review-{r['reviewer']}.json"
  if path.exists():
   review=json.loads(path.read_text()); found=[v for v in review['findings'] if v['id']==r['id']]
   if len(found)!=1:raise ValueError(r['id'])
   v=found[0];record['status']=v['verdict'];record['responsible_response']={'kind':'actual_named_profile_review','profile':review['profile'],'session_id':review.get('session_id'),'target_sha256':review['target_sha256'],'response_file':path.name,**v}
 results.append(record)
counts=dict(collections.Counter(r['status'] for r in results))
for r in results:
 r['final_package_addendum']='22-addendum.md: E01 MIA-02 / E02 JAMES-04,MIA22-N01 / E03 SAM-03/04,MIA22-N03 / E04 JAMES-01/02,SAM-08,MIA22-N02. Reviewer v01 verdict preserved; no implied re-review of addendum.'
(A/'22-resolutions.json').write_text(json.dumps({'document_id':'P1-22-RESOLUTIONS-v01','target_sha256':sha(A/'22.md'),'scope':'document disposition; not all defects resolved/approved','findings':results,'counts':counts},ensure_ascii=False,indent=2)+'\n')
md=['# P1-22 原지적 전수 대응/재확인','', '상태 review, 최종수치/GDD/G3 미승인. 채택은 문서수정 방향이며 결함해소와 다름. original severity 유지; 중복주제도 원ID별 보존. James 자신의7지적은 실제 작성자 자체재검토이며 독립리뷰라고 부르지 않음. Mia/Sam은 실제 새프로필 응답만 연결.','',f'현재 집계: {json.dumps(counts,ensure_ascii=False)}','']
md += ['## 최종 제출 정정 부록','[22-addendum.md](22-addendum.md)를 본문과 함께 읽는다. 본문/실제 검토 지문은 보존하고 E01 옛 구매오류, E02 질문순서, E03 확장 부분전달, E04 보스/집합 채택제한을 정정한다. v01 담당 판정을 소급 변경하지 않으며 부록 재검토는 별도 응답만 증거로 인정한다.','']
for r in results:
 md += [f"## {r['id']} / {r['severity']} / {r['title']}",f"원문: {r['evidence_file']} L{r['evidence_first_line']} / 단일 책임 {r['owner']} / {r['baseline_status']}",f"채택/미채택: {r['disposition']} — {r['reason']}",f"수정 위치: {r['location']}",f"재검증: {r['reverification']}",f"실제 담당 응답: {json.dumps(r['responsible_response'],ensure_ascii=False)}",f"현재 상태: {r['status']}; 남은 위험: {r['remaining']}",'']
md += ['## 미채택/보류 이유 요약','原지적의 문제제기 자체를 기각한 건은 없다. 해결수단을 전부 무조건 채택하지는 않았다. I07 A 강제유지는 역사비교로 보존/B는권고만; 정밀도·정수상한·과부하수치를 근거없이 메우는 안, 환불/공급선행/단계선택 UI 추가, 참가자 추가나 미술인일 생성, 원밖명중·시간증가·실패농사는 미채택/보류한다. 전자는 실제기기/전문담당·대표 결정이 없고, 후자는 G1/최소범위/측정권한을 침범하기 때문이다. 잔여를 닫지 않은 채 검토패키지로 제출한다.','']
(A/'22-resolutions.md').write_text('\n'.join(md))
james=[r for r in results if r['reviewer']=='james']
(A/'22-review-james.md').write_text('# James 실제 작성자 자체 재검토\n\nP1-22-GDD-v01 / SHA256 '+sha(A/'22.md')+'\n담당: 현재카드 James. 독립프로필 새리뷰라고 주장하지 않음. 21 실제 James 응답 이후 이번22 본문과 새산술을 작성·재확인.\n\n'+'\n\n'.join(f"## {r['id']}\n{r['reason']}\n{r['location']}\n현재 partial_open: {r['remaining']}" for r in james)+'\n\n실제 사용자/게임/성능/실물/승인 검증 없음. 지적 채택은 담당자의 실제 문서 답변이며 Mia/Sam 역동의·대표승인 대체가 아님.\n')
print(json.dumps({'findings':len(results),'counts':counts,'missing_actual_responses':[r['id'] for r in results if not r['responsible_response']]},ensure_ascii=False))
