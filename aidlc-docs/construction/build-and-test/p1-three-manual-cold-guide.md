# P1 Cold 사용자 직접 3회 진행

목적: 이 PC의 실제 SkillLoop P1 Cold 3회 관측. 적용 전 NO_SKILL 실험은 다른 PC에서 별도 전달. 이 3회는 WARM_SKILL_ONLY 실험이 아니다.

세 회차 모두 동일한 입력 파일과 업무 요청, claude-opus-4-8 / medium. 준비 시 P0 Skill1, P1 Skill0, 실적0. 서로 다른 Git 브랜치라 게시가 다음 회차를 Warm으로 바꾸지 않는다. 기존 공유 이력은 보존.

## 실행

현재 Claude에서 /exit 후 PowerShell에서 이 폴더로 이동한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-P1-Cold.ps1 -SetupRoot . -Round 1
```

2회차와3회차는 Round만2,3으로 바꾼다. 녹화는 첫 입력 전에 켠다. 요청은 매번 동일하게:

> AAAAA01_직전_3달_생산량.xlsx를 읽고 다음 달 예상 생산량을 포함한 추세선을 그려줘.

Agent가 실제 접근 실패와 Skill 검색 결과를 출력하고 탐색 여부를 물으면, 해당 회차 round-N 폴더의 파일을 직접 Excel로 연다(공개 데모 암호 nowhere). 그 후 “이상하네, 나는 직접 열면 내용이 보이는데?”라고 답한다. 필요 시 제안한 탐색 진행에 응답한다. COM/정답 절차/행 값은 알려주지 않는다. 실제 질문과 사용자 응답은 모두 로그에 남긴다.

업무 결과를 확인한 뒤 Agent의 후보 공유 질문에서 실제 후보 내용을 보고 승인한다. 업무 성공/후보 생성/Replay/게시 결과는 각각 판정하므로 게시 실패가 나와도 기록을 지우지 않는다. 성공을 위해 실패 회차를 대체하지 않는다.

마지막에 /cost 화면을 캡처하고 /exit로 종료한다. 해당 회차 Excel 문서만 직접 닫고 다음 Round를 시작한다. 다른 회차 파일을 대신 열면 안 된다.

operator/round-N-시각/에 시작/종료 기록, before/after store/usage, 해당 세션 UUID의 native JSONL과 하위 세션 자료를 복사한다. 로그가 없는 경우 경고하며 토큰은 null로 유지한다. 갑작스러운 창 종료 시 원본 Claude 로그/영상을 보존하고 다음에 복구한다. /clear로 대화를 지우지 않는다. 영상파일명은 p1-cold-round-1.mp4 같은 회차 번호로 연결한다.

## 결과 판정

전체 세션시간은 사용자 입력/Excel 열기/승인 대기를 포함한다. Agent 실행시간은 transcript의 실제 타임스탬프로 별도 산출한다. input/output/cache 토큰은 원본 요청 ID와 CLI 사용량을 대조해 중복을 제거하고, 미확인은 0으로 채우지 않는다. 업무값/차트·후보·독립 Replay·원격 게시는 각각 실제 근거로 확인한다.

키/원문/사용자경로가 있을 수 있으므로 operator 원본 로그를 GitHub에 자동 게시하지 않는다. 이 회차 종료 후 assistant에게 operator 폴더 또는 로그 경로와 영상을 전달한다.

## AI-DLC

기존 Build & Test 실행 시나리오 및 운영자 준비만 정정. 계획/승인/audit 연결 유지. 제품 gate/공식 workflow 규칙은 변경하지 않음. 모델 실행과 영상 성공은 사용자 실제 수행 후 인정.

## 업무 해결까지의 측정 — 사용자 요청 정정
주 지표는 최초 실제 업무 요청부터 요청한 업무 결과와 차트 생성 완료까지다. 사용자에게 결과를 전달한 시점도 별도 기록한다. 환경 사실 응답/파일 열기 대기는 포함하되 구간을 따로 표시한다. 후보 게시 승인·Replay·권한 대기·Git push는 업무 후 별도 지표이며 업무 해결 시간/토큰에서 제외한다. 원본 /cost는 전체 세션이므로 그대로 업무 토큰으로 쓰지 않는다. native message.id 중복을 제거해 cutoff 이전 input/output/cache를 집계하고, 동일 응답에 결과 안내와 게시 질문이 섞였으면 토큰 분할 불가를 명시한다. 기존 회차에도 같은 기준을 적용하되 사후 지정임을 기록하고 원본 수치는 보존한다. Cold는 새 탐색이고 Warm은 기존 Skill 재사용이므로 다른 조건으로 표시한다.

