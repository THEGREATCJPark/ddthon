# B / 한석훈님 — 다음 날 GitHub 공용 Skill 시연 준비

목표는 새 기능 개발보다 **B PC에서 CJ가 게시한 Skill을 가져와 실제 업무에 재사용하고, 그 실적을 다시 공유하는 장면**을 완성하는 것입니다. GitHub의 `team-skill-store`는 이미 CJ 검증 과정에서 생성했습니다. 새 저장소나 브랜치를 다시 만들 필요 없습니다.

## 1. 가져올 것과 보존할 것

- 제품 코드: `THEGREATCJPark/ddthon`의 최신 `main`.
- 공용 데이터: 같은 저장소의 `team-skill-store`. 제품 checkout과 별도의 mirror 폴더에서 CLI가 관리합니다.
- B의 기존 `work/u2-p1-git`와 로컬 변경은 보존합니다. 기존 checkout을 강제로 reset하지 말고 새 폴더에 clone하는 것이 간단합니다.
- GitHub 로그인 계정 `smallmemory9-source`의 collaborator 초대 수락을 확인합니다. 공개 데이터 pull에는 write 권한이 필요 없지만 실적 push에는 필요합니다. commit author와 push 인증 계정은 별개입니다.
- 제품 코드 변경은 작업 브랜치와 PR로 CJ에게 인계합니다. `team-skill-store`의 검증된 공유 이벤트는 제품의 sync CLI가 직접 push하는 데이터 흐름입니다. 두 작업을 혼동해 main에 런타임 데이터를 올리지 않습니다.

```powershell
git clone https://github.com/THEGREATCJPark/ddthon.git "$env:USERPROFILE\Desktop\skillloop-b-demo"
cd "$env:USERPROFILE\Desktop\skillloop-b-demo"
git rev-parse HEAD
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[p1]"
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

필요 환경: Windows, Python, Git, **데스크톱 Excel 설치·실행**, pywin32/openpyxl/matplotlib(위 p1 설치에 포함), GitHub 접근 가능한 네트워크와 인증. P0는 Excel 없이 실행할 수 있습니다. Excel 없는 P1은 NOT_RUN으로 구분합니다.

## 2. B의 작업 환경 준비

제품 루트 터미널 하나에서 실행한 채 유지합니다. 경로는 새 디렉터리여야 합니다.

```powershell
.\.venv\Scripts\python.exe scripts/prepare-p1.py "$env:USERPROFILE\Desktop\skillloop-b-work"
```

두 문서가 Excel에서 열린 채 준비됩니다. 이 터미널은 환경 유지용입니다. 암호를 Agent에게 전달하지 않습니다. 환경 유지 시간은 최대 2시간이므로 시연 직전에 준비합니다. 종료할 때는 해당 루트에 `STOP` 파일을 만들면 준비 도구가 자신이 만든 문서만 닫습니다.

다른 PowerShell에서 다음을 실행합니다. `warm`은 경로·배치·생산량이 다른 업무 문서입니다.

```powershell
$bProduct = "$env:USERPROFILE\Desktop\skillloop-b-demo\.venv\Scripts\python.exe"
$bWork = "$env:USERPROFILE\Desktop\skillloop-b-work\warm"
$bStore = "$bWork\.skillloop\store.json"
$bUsage = "$bWork\.skillloop\usage.json"
$bMirror = "$env:USERPROFILE\Desktop\skillloop-b-team-mirror"
$bRemote = "https://github.com/THEGREATCJPark/ddthon.git"
& $bProduct -m skillloop store-init --store $bStore --mirror $bMirror --remote $bRemote
& $bProduct -m skillloop sync --store $bStore --usage $bUsage --mirror $bMirror --remote $bRemote
& $bProduct -m skillloop status --store $bStore --usage $bUsage --team "디디톤 기술혁신팀" --alias "한석훈"
```

첫 sync는 기존 공개 Skill을 검증·import합니다. 재실행의 imported=0은 이미 가져온 항목의 중복 방지일 수 있습니다. `ok`, `conflicts`, exact digest와 게시 근거를 함께 확인하세요. DB·Excel·업무 결과 파일을 직접 Git에 add하지 않습니다.

## 3. Claude에서 실제 업무 요청

`$bWork` 폴더에서 새 Claude Code 세션을 시작하고 다음 한 문장으로 요청합니다.

> BBBBB02_직전_3달_생산량.xlsx를 읽고 다음달 예상 생산량을 포함한 추세선을 보여줘.

원격 Skill 실행 확인을 요청하면 내용을 확인한 뒤 사람이 승인합니다. 이번 공개 Skill의 참조는 다음과 같습니다.

- id: `file-access-8738e696cff8bbb20c98`
- version: `1.0.0`
- digest: `359c5c1763416cdb3aa9828adef40219d1ac5448f82d62f91ebbca82768727af`
- 절차: 이미 열어둔 Excel에 read-only 접근. 암호·업무 계산·시트/열 위치 없음.

승인되지 않은 다른 digest까지 포괄 승인하지 않습니다. CJ의 후보 게시 승인과 **B 환경에서 가져온 Skill을 실행하는 확인**은 구분됩니다. Agent가 새 사람 review를 만들어서는 안 됩니다.

확인할 실제 장면:

1. 표준 직접 읽기 실패 → 팀 Skill MATCH.
2. 승인된 접근 절차로 원본 무변경 읽기.
3. 이번 문서의 시트·열을 판단해 실제 3개월 + 예상 1개월 차트 생성.
4. 예상 생산량 2550, `work_verified=true`, `counted=true`, `candidate_delta=0`.
5. Skill digest 유지. B 환경에서 처음 성공한 실행은 로컬 reuse=1입니다. 조직 총계와 혼동하지 않습니다.

팀원 이름이 실적에 반영되도록 run-p1 호출 시 `--author "한석훈"`을 전달하도록 Agent에게 운영 설정으로 알려주세요. 이것은 해결법 지시가 아니라 실적 작성자 표기입니다. `status --alias`는 조회 대상 이름이며 이미 기록된 이벤트의 작성자를 바꾸지 않습니다.

## 4. 실제 재사용 이벤트 공유

```powershell
& $bProduct -m skillloop sync --store $bStore --usage $bUsage --mirror $bMirror --remote $bRemote --push-usage
```

`usage_push.ok=true`와 원격 commit을 CJ에게 전달합니다. CJ가 자신의 저장소에서 sync하여 B 실적을 확인합니다. 같은 이벤트를 다시 sync해도 조직 실적이 추가 증가하지 않아야 합니다. 기존 테스트 실적을 임의로 삭제하거나 숫자를 덮어쓰지 않습니다. 새 테스트 실행은 실제로 새 업무 검증을 해야 합니다.

상태줄은 동기화 연결 시 **팀 게시 Skill의 검증된 공유 이벤트**로 인기·팀 실적을 표시하고 로컬 숫자를 별도로 표시합니다. 수신만 한 CJ 화면은 팀1/로컬0이 될 수 있습니다. 같은 이벤트가 로컬·공유 양쪽에 있어도 팀 집계는1입니다. 팀 기여는 실제 게시 exact descriptor 작성자 기준입니다. 동기화 미연결은 확인 대기로 표시하며, last-sync 이후 로컬에 관찰된 데이터 범위로서 실시간 전체 조직의 완전한 집계를 뜻하지 않습니다. 기존 공유 Skill의 작성자는 `local`로 기록되어 있으므로 실명으로 꾸며 바꾸지 않습니다(내용 변경은 digest와 승인 대상 변경).

## 5. 인계할 결과와 문제 대응

- 구버전 requirements-dev.txt의 한글 주석을 읽다 cp949 UnicodeDecodeError가 발생하면 `python -X utf8 -m pip install -r requirements-dev.txt`로 설치할 수 있습니다. 현재 파일은 주석만 ASCII로 정정했으며 의존성 선언은 동일합니다. 이미 우회 설치에 성공했다면 재설치나 새 clone 없이 해당 제품 SHA를 기록하고 다음 단계로 진행하세요.
- 채팅 복사 시 경로 구분자가 빠질 수 있으므로 위 코드 블록을 기준으로 합니다. `skillloop-b-demo\.venv`, `warm\.skillloop` 사이의 역슬래시를 보존하세요.

- 제품 main SHA, 공용 branch commit SHA, 실행한 명령, 성공/실패 출력.
- 자연어 요청부터 차트·재사용 +1까지 캡처/영상. 원격 공유 후 CJ 화면도 촬영.
- 403: GitHub 인증 계정·초대 수락·write 권한 확인. 토큰을 채팅이나 저장소에 넣지 않음.
- Excel NOT_RUN: 준비 터미널과 대상 문서가 열려 있는지 확인. 제품은 암호를 대신 풀거나 문서를 강제 열지 않음.
- Git 충돌/실패: mirror와 로컬 데이터를 보존하고 오류·SHA를 전달. main으로 공유 데이터를 우회 push하지 않음.
- 예상과 다른 결과면 성공으로 보정하지 말고 실제 출력 그대로 전달. CJ는 승인된 계약 내 결함을 수정하고 해당 검증만 재실행.

## 6. 투표자에게 설명할 문구

> 사내환경에서 Agent가 막혔을 때, 팀이 검증한 해결 방법을 찾아 적용합니다. 새로운 해결 경험은 사람 검토와 독립 재실행을 통과한 뒤 공유하고, 다음 Agent가 다른 업무에 재사용합니다. 이번 해커톤에서는 GitHub를 공용 Skill 저장소로 구현했습니다. 사내 도입 시에는 접근 권한과 감사 체계에 맞춰 S3나 사내 저장소에 연결하도록 확장할 수 있습니다.

**현재 구현 = Git 공유 어댑터. S3/DB 연동 = 향후 확장안.** 저장소만 교체하면 즉시 상용 배포된다는 뜻은 아닙니다. S3/DB에는 별도 어댑터·인증·권한·동시성/동기화 설계가 필요합니다. 공유되는 것은 DB 파일이나 업무 원문이 아니라 검증된 환경 접근 절차와 재사용 이벤트입니다.
