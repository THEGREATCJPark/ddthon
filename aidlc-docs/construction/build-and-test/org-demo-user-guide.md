# GitHub 조직 Skill 시연 — 사용자 실행 안내

현재 시연 DB: https://github.com/THEGREATCJPark/ddthon/tree/team-skill-demo-20260909

초기 데이터 commit: 75b6e54225a9fa4e71e7174168161d61fa923e31. P0 Skill 1개, P1 Skill 0개, 공유 재사용 이벤트 0건으로 준비했다. 기존 team-skill-store의 과거 P1/실적은 삭제하지 않았다. 이 수치는 준비 시점 기준이며 실제 사용자 실행 후에는 달라진다.

## 1. P0 — 조직 DB에서 받아 설치 해결

PowerShell에서:

```powershell
$env:PYTHONUTF8 = '1'
Set-Location 'C:\Users\cik61\Desktop\skillloop-org-p0-20260909'
& 'C:\Users\cik61\.local\bin\claude.exe'
```

Claude에:

> 이 프로젝트 requirements.txt의 패키지를 설치해줘.

예상 흐름: 현재 작업 venv 실제 설치 실패 → 동기화된 팀 Skill 검색 → 선택한 원격 Skill 실행 확인 → 허락 후 같은 작업 venv 설치·버전·import 검증 → 로컬 실적 +1 → GitHub에 이벤트 공유. 원격에서 받았다는 이유만으로 실행 허락을 자동 생성하지 않는다. 이번 준비는 실제 사용자 설치를 대신하지 않았으며 작업 패키지는 아직 미설치 상태다.

하단 초기 상태: 팀 공개 Skill 1개, 박찬준 기여 1개, 실제 재사용 0회. 명시적 실행 확인은 Claude 대화에서 한다. 같은 설치를 다시 요청해 이미 설치된 상태라면 추가 reuse가 발생하지 않는 것이 정상이다.

## 2. P1 Cold — 없는 해결책 발견 후 승인·게시

문서 확인/재열람: 아래 파일을 탐색기에서 더블클릭한다. 운영자 문서 열기이며 Agent에 실행을 맡기지 않는다.

`C:\Users\cik61\Desktop\skillloop-org-p1-20260909\Open-cold.cmd`

별도 PowerShell에서:

```powershell
$env:PYTHONUTF8 = '1'
Set-Location 'C:\Users\cik61\Desktop\skillloop-org-p1-20260909\cold'
& 'C:\Users\cik61\.local\bin\claude.exe'
```

Claude에:

> AAAAA01_직전_3달_생산량.xlsx를 읽고 7월 생산량을 알려줘.

일반 직접 읽기 실패와 실제 팀 검색 NO_MATCH를 확인한 뒤, 사용자가 직접 관찰한 환경 사실을 자연스럽게 전달한다. 예: “지금 Excel에서는 잘 보여.” 정해진 문장을 외울 필요는 없다.

Agent가 환경을 조사하여 업무를 해결하면 환경 접근 절차만 후보로 남기고, **사용자가 먼저 게시 요청을 하지 않아도 Claude Code 대화에서 공유 승인을 묻는다.** Windows GUI나 별도 터미널 확인창을 열지 않는다.

후보 내용을 확인하고 대화에서 승인하면 Agent가 실제 답변/검토자/exact 후보를 기록하고 독립 Replay를 수행한다. PASS와 실제 GitHub push 성공 후에만 게시 완료다. 보류·거절·미준비·검증 실패에는 게시하지 않는다. 원문·암호·시트/열·계산값·차트는 공유 Skill에 포함하지 않는다.

Cold 성공은 재사용이 아니므로 reuse +0. 게시 후 DB에는 P0와 P1이 각각 1개가 된다. 7월 실제 데이터는 조회값으로 답하며, 요청하지 않은 8월 예측을 실제값처럼 보여주지 않는다.

## 3. 게시 후 다른 문서/동료 Warm

P1 게시 성공 이후에만 warm 폴더 또는 동료 PC에서 같은 remote/branch를 sync한다. 현재 warm 폴더도 P0-only 초기 상태이므로 먼저 sync하지 않고 기존 P1 Skill이 있다고 말하면 안 된다.

연결된 작업의 `skillloop-work.json`에서 product_python/store/usage/mirror/remote/branch를 읽어 다음을 실행한다:

```text
<product_python> -m skillloop sync --store <store> --usage <usage> --mirror <mirror> --remote <remote> --branch <branch>
```

새 문서는 `Open-warm.cmd`로 열 수 있다. 원격 P1 Skill의 exact 실행 허락을 받은 뒤 다른 문서의 실제 값을 읽어 업무를 완료하면 재사용 +1, 후보 +0이어야 한다. 이후 `sync ... --push-usage`로 공유하고 수신 환경에서 첫 이벤트 1건/반복 0건을 확인한다.

## 4. 기록과 제약

- 이번 자동 준비 검증과 사용자가 직접 수행할 Claude 시연은 구분한다. 전체 대화·도구 출력·상태줄 변화·원격 commit을 같은 실행으로 보존한다.
- 초기 P0 실증은 별도 임시 작업 폴더에서 실행했고 공유 이벤트는 push하지 않았다. 사용자의 P0/P1 저장소에 테스트 성공 횟수를 넣지 않았다.
- Excel 원본 두 문서는 운영자 준비 프로세스가 유지한다. 약 2시간 후 닫히더라도 Open-cold.cmd/Open-warm.cmd로 다시 연다. 프로그램이 다른 사용자 Excel을 종료하지 않는다.
- NASCA 직접 표현은 승인된 해커톤 화면 표현으로 유지한다. 구현/증거는 Office 암호화와 허용 앱 접근임을 정확히 기록한다.
- 실제 다른 PC Warm은 해당 PC의 실행 증거가 있어야 완료다. 자동 로컬 검증을 다른 사람의 실제 시연으로 표시하지 않는다.
- 새로운 복구 코드를 범용적으로 학습하는 엔진은 아니다. MVP의 차별점은 환경 해결 절차의 검토·독립 재검증·공유·다음 실행 재사용을 연결하는 것이다.
