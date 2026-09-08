# P0 재현 기준 확정 → P1 조건부 진행 계획

사용자 요청: “과적합으로 구현하는건 지양해야해 … 수용할것만 수용하고 멈추지말고 p0을 재현 가능하게 정리하고, 너가 직접 테스트를 3회 동작하고, 그 로그를 잘 기록해둬. 그리고 결과가 괜찮으면 p1 구현까지 돌입해도돼. ai-dlc 절차를 충실히 이행해.”

이는 P0 재현 정리·3회 실행 및 통과 후 기존 승인 P1 구현의 조건부 진행 허가다. 기존 Requirements/Units/Excel 예외/게시 게이트는 재결정하지 않는다. 문서는 구현 전에 작성하며 이후 추가 범위 승인으로 확대 해석하지 않는다.

## 영향·설계·NFR

피드백 수용: 최종 P0 성공 보존, 단일 합성 한계 공개, digest/사람 승인 유지, 작업환경 보존, 개인 경로와 소스 하드코딩 구분, 최신 전체 회귀, P1 우선. 미수용: 예제 identity 변경을 기존 승인 자동 승계 사유로 삼거나 범용 패키지 엔진으로 확장.

P0 기능·계약은 기존 개정 2를 유지한다. 새로운 위치의 저장소와 그 안의 제품 venv로 준비하여 Codex 세션 runtime 의존 없이 재현한다. 개발 checkout+fixture가 필요한 범위를 명시하며 wheel 단독 배포 지원을 주장하지 않는다. 준비 도구는 기존 tests/prepare_p0_work.py 호출, 기존 작업 덮어쓰기 금지. 신규 PowerShell 진입점 scripts/prepare-p0.ps1은 시스템 Python을 인자로 받아 프로젝트 .venv 설치 후 준비만 한다. 외부 네트워크는 최초 선언 의존성 설치에만 필요하며 실제 P0 pip은 오프라인이다.

P1은 이미 승인된 A cb25a62/B 1760d32 계약과 FD/NFR/Code Plan을 로드해 이어간다. B의 잘못된 digest Replay PASS·사용자 Excel 전체 종료·가짜 Office 파일 표기를 먼저 수정한다. S2 업무 계산/후보화, S3 상태 단독 소유/사람 검토/exact Replay 게이트, C4 Git 전송과 실패 보존을 기존 설계에 맞춰 구현한다. 새로운 상태/역할/프레임워크를 추가하지 않는다. 공통 파일 CJ 소유, A 소스는 인계본 그대로 우선 통합, 후속 변경은 소유 이관 기록 후 최소한으로만 수행한다.

## Code Plan

- [x] R1. scripts/prepare-p0.ps1 + 재현 안내 작성. 새 위치 checkout의 독립 제품 venv에서 선언 의존성 설치. README/EVALUATION 편집 보존.
- [x] R2. 동일 소스 기준 최신 전체 pytest. 기존 결과와 혼합 금지.
- [x] R3. 새 Claude 세션 3회, 서로 다른 작업 폴더/주석·공백/무관 Skill 조건. 자연어 한 문장으로 실제 실패→MATCH→같은 작업 venv 설치→별도 import→count 1 확인. 각 로그·exit·source hash 저장. 지원 외 입력/승인 불일치/기존 설치 +0는 기존 회귀 증거로 구분.
- [x] R4. 세 결과·전체 회귀 검토 후 P0 기준 기록. 허위 PASS나 임의 범위 확대 없으면 사용자 조건부 지시에 따라 P1 진입. 문제가 있으면 해당 결함을 고치고 필요한 검증만 반복.
- [x] P1. A/B 코드·관련 문서 인계본을 현재 작업에 통합하고 provenance 기록. 충돌 시 양쪽 audit 보존, main state는 최신 결론 유지.
- [x] P2. B Replay 무결성 판정과 소유 Excel cleanup/placeholder 정직성을 수정하고 검증. 실제 Excel 준비를 사용자 Excel과 격리하기 전 실행하지 않는다.
- [x] P3. CJ 인수 S2/S3/C4 최소 구현과 CLI·조회 연결. 사람 승인 없는 게시, 내용 변경 후 승인 승계, 최초 결과 재사용 Replay, 원격 상태→로컬 승인 생성 금지. Agent 탐색을 CLI가 정답 자동 선택으로 대체하지 않는다.
- [x] P4. 관련 단위·계약·통합 검사. 실제 Excel/원격 Git 검증은 실행 환경·권한과 증거가 있을 때만 PASS. 불가하면 NOT_RUN. 결과 코드 REVIEW REQUIRED와 전체 Build and Test 잔여를 분리 보고.

확정 NFR/PBT Partial은 유지, NFR/Infra Design SKIP 경계 유지. 필요 이상의 문답이나 전체 Inception 재시작 없음. 단계별 실제 OS UTC audit append, source of truth는 현재 ddthon 승인 산출물·현재 실행 증거뿐이다.

P2/P3 코드 구현·대역 검증 완료. 실제 Excel 통합 시도는 FAIL_TIMEOUT이며 미완료로 보존. 실제 Excel 완료/P1 전체 종단 PASS를 체크 의미로 확대하지 않는다. P4 최신 전체 회귀/결과 정리 진행 중.

P4 검토 완료: 통합 회귀130 PASS/2 SKIP, 추가 CLI2건 포함 서비스9 PASS. 실제 Excel FAIL_TIMEOUT, GitHub/Agent P1 종단 NOT_RUN. 따라서 P1 전체 완료 승격 없이 코드 결과 검토·실행 결함 잔여 상태로 유지한다. 검증 파일은 result/p1-integration/.
