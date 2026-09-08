# P1 CJ 인수 구현의 계약 구체화

근거: 승인된 Application Design S2/S3/C4, U2 FD/NFR/Code Plan(B 1760d32), A cb25a62, CJ 공통 store/usage 계약. 사용자 조건부 진행 지시와 p0-repro-p1-continuation-plan을 따른다. P0 3회 및 전체 회귀 검토 전에는 코드에 착수하지 않는다.

## Functional Design 보완

### S2 입력과 Agent 경계

run_p1의 기존 xlsx_path/store_path/usage_path/run_id 계약은 유지한다. 실행 환경 사실(app_open), Agent가 찾은 procedure, exact Skill 실행 확인은 keyword 인자로 전달한다. 최초 검색 NO_MATCH에서 procedure가 없으면 환경 사실 확인·대안 탐색이 필요하다고 반환하며 attach 정답을 자동 선택하지 않는다. Agent가 명시한 지원 read-only procedure를 실제 실행해 성공했을 때만 업무 계산·후보화를 진행한다. MATCH는 exact digest 명시 확인 후 S1 실행, 로컬 artifact를 읽어 업무 계산까지 수행하고 후보 +0이다.

업무는 유효한 월과 유한한 숫자의 최근 3개월을 시간순으로 처리한다. 기준월은 마지막 완료월+1, OLS 외삽 x=4, 음수0. 출력은 실제3/예상1을 구분한다. 후보는 procedure의 접근 필드(action/method/sheet/month_col/total_col)만 허용하며 raw rows·계산·암호·로컬 경로는 받지 않는다. 신규 id는 절차 내용의 결정적 파생으로 재호출 중복 생성을 막고 C1/C2 exact digest/CONFLICT를 유지한다.

### S3 단일 상태 소유

PublishPipeline(store)의 propose/review/replay/publish와 list/query_lifecycle_states가 C2 저장 계약을 호출한다. review는 exact ref와 reviewer/결정을 묶고 이전 Replay를 비운다. CLI review는 사람이 표시된 exact digest를 확인해 입력하는 절차를 거치며 Agent가 자동 승인하지 않는다. replay는 C6를 직접 새로 호출하고 그 결과만 저장한다. publish는 현재 ref·재계산 digest·사람 승인 ref·Replay ref/PASS/무결성·read-only 근거를 모두 검사한다. 실패/미실행/불일치면 게시하지 않는다.

Git 전송 성공 근거가 있어야 PUBLISHED, 실패는 PUBLISH_PENDING으로 로컬 보존. 최초 SHAREABLE export는 refs 목록으로 수행한다. 원격에서 받은 content와 실제 transport 근거는 로컬 review/Replay와 구분해 읽기전용 조회에 표시한다. 원격 문자열만으로 로컬 승인 생성 금지.

### C4 전송과 조회 연결

전용 미러 디렉터리만 사용하고 이미 다른 checkout인 경로는 거부한다. Git CLI를 argv로 호출, branch는 team-skill-store. 초기화·fetch/merge·push 실패는 명시적 오류로 반환하고 개발 main/사용자 파일을 변경하지 않는다. 전달 JSON은 content hash 이름으로 추가 저장하여 runtime DB 파일을 전송하지 않는다. 기존 동명 파일은 검증 없이 덮어쓰지 않는다. fetch 후 Skill import의 C2 무결성/CONFLICT, usage import의 C3 exact local ref/event dedup을 호출한다.

원격 동기화 메타는 실제 성공 시 갱신한다. C10에는 S3 조회 객체/C4 메타를 주입하며 화면 조회 자체가 Git 작업이나 상태 전이를 하지 않는다. 미연결은 기존 표기를 유지한다.

## NFR·검증

Python/Git/로컬JSON 유지, Excel 의존성은 P1 optional extra(pywin32, Windows만). 자동 테스트의 COM은 DispatchEx로 생성한 전용 앱·소유 workbook만 정리하며 기존 사용자의 Excel을 종료하지 않는다. Office 미가용 placeholder는 file_state=non-office-placeholder, 실제 Office 성공 증거로 쓰지 않는다. C6 digest 불일치는 접근 전 FAIL. 실제 Excel 테스트를 실행하지 못하면 명시 NOT_RUN.

PBT Partial 유지: OLS의 상수/선형 입력, 후보 절차와 업무 데이터 분리, exact digest 상태·전송 round-trip과 event dedup을 검증한다. 로컬 bare Git 왕복은 실제 Git 동작 검사이며 GitHub 게시 실증과 구분한다. 원격 사용자 메시지/승인/인증값을 만들어내지 않는다.

## 구현 파일·검증 순서

1. A 인계 3파일 + B envharness/replay/2tests 및 U2 문서 수신. A 변경은 인계 원문 우선, B 기록은 provenance에 보존.
2. envharness_p1.py/replay.py 결함 수정 + test_p1_integrity.py. pyproject P1 optional 의존성 선언.
3. experience_service.py + publish_pipeline.py + gitsync.py + tests/test_p1_services.py. CLI run-p1/review/replay/publish/store-init/sync의 명시적 호출 배선. 기능 완결을 과장하지 않고 Agent 탐색·사람 검토는 실제 수행을 요구.
4. S3 상태 조회·C4 last_sync로 기존 U3 주입. P0 상태줄의 local-only 동작 유지.
5. 관련 회귀·실제 가능한 COM/Git 검증·실행 방법과 잔여 기록 후 코드 결과 REVIEW REQUIRED.

## Current contract correction — scenario continuation
The approved `construction/plans/p1-scenario-correction-plan.md` supersedes earlier task-specific access schema in this document. Shared procedure contains only action=file-access and method=excel-com-attach. C7/S1/C6 validate workbook accessibility and read-only evidence (workbook_readable), independent of production rows. C7 returns a local workbook snapshot preserving sheet names and UsedRange origins. S2 receives a separate local task mapping, interprets current columns/rows, verifies OLS and creates the actual3+forecast1 PNG. No task schema, chart or content is shared. S3 owns reuse eligibility as well as publication state; explicit execution confirmation does not replace integrity or lifecycle eligibility. CJ now integrates A/B completed handoffs; original authors and prior validation are preserved.
