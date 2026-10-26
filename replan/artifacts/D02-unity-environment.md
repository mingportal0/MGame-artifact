# D02 Unity MCP 환경 검증 요약

상태: 개발환경 연결 및 임시 Cube smoke test 검증 완료. 게임 데모 구현·빌드 완료 아님.
담당: Sophie(설정/증빙 확인), Sam(Unity 실제 호출/개발).

## 검증 결과
- Windows Unity Editor 6000.6.7f1 및 기존 CoplayDev MCP for Unity 10.3.0 설치·실행 확인.
- 기존 HTTP 서버는 Windows loopback의 8080 포트를 사용한다. WSL NAT에서 직접 접근되지 않아, WSL stdio → Windows Python → 기존 loopback HTTP 어댑터로 연결했다. 방화벽/외부 포트 공개는 하지 않았다.
- 기존 Sam 설정 백업 후 Unity MCP만 추가. 기존 MCP/다른 에이전트 설정은 유지했다.
- `hermes -p sam mcp test unity` 성공. 최종 확인에서 연결 1256ms, 서버 도구 49개 발견. 발견 수는 필터 후 노출 수와 다르다.
- 실제 Sam 세션에서 네이티브 Unity MCP 도구를 호출하여 임시 Cube 1개 생성, Transform·Mesh·Collider 조회, Unity Editor Scene View 캡처 확인을 수행했다.
- 임시 Cube 삭제 후 재검색 0개. 기존 root 3개의 ID·Transform·구성요소는 전후 동일했다. Sophie가 실제 원 tool 응답과 Scene View 캡처를 확인했다.

## 접근 분리 및 제한
- Unity 도구 등록은 Sam 프로필만 적용. 다른 에이전트에는 추가하지 않았다.
- 프로필별 설정/도구 노출 분리는 가능하지만 동일 OS 계정의 파일·terminal 접근까지 차단하는 강제 보안 격리는 아니다.
- 서버주도 sampling은 비활성화하고, 유료/외부 생성 및 불필요한 연동 도구 5개를 제외했다. 승인 정책은 변경하지 않았다.
- Editor와 기존 HTTP 서버가 실행 중이어야 한다. 어댑터는 요청/응답 tools·resources용이며 별도 장기 비동기 알림 수신 지원은 검증하지 않았다.
- Cube 정리는 확인했지만 씬의 미저장 표시가 남아 있다. 기존 씬을 임의 저장·재로드하지 않았다.
- 추가 C# 선택/mesh 진단 1건은 Unity의 폐기 API 컴파일 오류로 실패했다. CRUD·리소스 조회·화면 캡처 성공과 별도로 기록한다.
- 라이선스 신규 활성화·약관 동의·유료 설치 없음. 실제 Edit/Play Mode 게임 테스트, 플레이어 빌드, 성능·재미·사용성 검증은 이 환경 smoke test의 통과 범위가 아니다.

## 후속 실행 범위
대표 요청에 따라 기존 D02를 재개한다. Sam은 기존 계약의 최소 전문 자문·구현·테스트·실행물 검증을 이어간다. 현재 SampleScene과 기존 사용자 변경은 보호하고 데모 전용 영역을 사용한다. 내부 프로젝트 정본과 Windows 작업경로의 대응은 구현 인계에 명시한다. D02 완료는 별도 산출물과 검증으로 판단한다. D03 및 장기기획 후속은 별도 명시 승인 전 실행하지 않는다.

이 공개본은 승인된 검토용 문서 요약이다. 로컬 개인경로, 프로필 설정/백업 원문, 세션·Slack 식별자, 게임 소스/빌드, 원 실행로그 및 Editor 이미지는 포함하지 않는다.
