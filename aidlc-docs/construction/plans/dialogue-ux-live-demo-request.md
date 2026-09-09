현재 진행 중인 AI-DLC workflow를 그대로 이어서 진행해.

기존 `aidlc-state.md`, `audit.md`, 승인된 Requirements / User Stories /
Application Design / Units / Functional Design / NFR Requirements / Code Plan과
현재 실제 실행 증거를 source of truth로 유지해.

새 AI-DLC workflow를 시작하거나 Inception을 재시작하지 마.
이미 승인된 결정을 다시 질문하지 말고, 이번 변경이 기존 승인 범위 안의 결함/사용성 보완인지
먼저 판단해. 제품 의미·요구사항·lifecycle 계약을 바꾸는 부분만 실제 change gate를 거쳐.

현재 목표는 새로운 범용 기능을 추가하는 것이 아니다.

1. 현재 구현된 P0/P1이 우리가 의도한 자연스러운 사용자 대화 흐름으로 실제 작동하게 한다.
2. 최신 Cold 검증에서 발견된 UX 문제를 최소 수정한다.
3. 웹 설명용 시연과 실제 제품 동작의 흐름을 정합화한다.
4. 수정 완료 후 실제 Claude Code UI를 열어 P0 자연어 시나리오를 단 한 번 수행하고,
   실제 질문/응답/SkillLoop 상태줄이 보이는 화면을 Computer Use로 캡처하여
   실제 시연 증거로 보존한다.

외부 사전 구현 Reference를 다시 검색하거나 참고하지 마.
현재 ddthon의 승인 산출물과 실제 실행 결과만 사용해.

────────────────────────────────────
0. 먼저 현재 상태 확인
────────────────────────────────────

작업 전 반드시:

- 현재 HEAD / branch / git status
- 다른 팀원이 현재 수정 중인 파일
- aidlc-docs/aidlc-state.md 최신 상태
- audit.md 최신 entry
- 현재 승인된 관련 Code Plan
- result/cold-review-20260909/
- result/p1-acceptance/
- result/final-alignment/
- .claude/skills/skillloop/SKILL.md
- skillloop/cli.py
- skillloop/experience_service.py
- skillloop/envharness_p1.py
- team-hub의 현재 Demo.tsx / demoScenarios.ts

를 읽어.

이미 해결된 문제를 다시 고치지 마.

이번 수정이 기존 Requirements/Stories의 의미 안에서
C9/CLI/시연 표현/사용성 결함을 정합화하는 범위라면
기존 AI-DLC change/code-generation 절차에 따라 최소 Code Plan을 만들고 승인 gate를 지켜.

과거 audit·실패·누락 기록을 삭제하거나 소급 승인하지 마.

────────────────────────────────────
1. P0 실제 사용자 시나리오를 이 흐름으로 고정
────────────────────────────────────

P0의 핵심은 사용자가 SkillLoop 사용법을 아는 것이 아니다.

사용자는 아래 자연어 업무 요청 한 번만 한다.

[사용자]
“이 프로젝트 requirements.txt의 패키지를 설치해줘.”

이후 이상적인 실제 흐름:

1) Agent가 현재 프로젝트 Python과 requirements.txt 확인
2) 기존/일반 package 공급 경로로 실제 pip 설치 시도
3) 실제 공급 실패 관찰
4) 사용자의 추가 힌트 없이 Agent가 현재 실패와 맞는 Team Skill 검색
5) applicability 확인
6) 기존 검증된 Skill 적용
7) 같은 작업 Python에 실제 설치
8) 설치/version/import 검증
9) 별도 확인까지 성공한 경우에만 실제 reuse +1
10) 새 Candidate는 0

사용자가 다음과 같은 말을 해야 성공하는 구조는 금지:
- “SkillLoop로 찾아봐”
- “Team Skill 검색해”
- “그 Skill 적용해”
- “내부 index 써”

Agent가 실패를 보고 스스로 조직의 기존 해결 경험을 확인해야 한다.

사용자에게 보여주는 진행 설명은 짧고 한국어로 한다.

권장 수준:

[Agent]
“현재 프로젝트의 Python 환경과 requirements.txt를 확인했습니다.
기존 설정으로 먼저 설치해 보겠습니다.”

실패 후:

[Agent]
“현재 패키지 공급 경로에서는 필요한 패키지를 찾지 못했습니다.
같은 문제를 팀에서 해결한 경험이 있는지 확인하겠습니다.”

Skill 발견 후:

[Agent]
“현재 실패 조건과 맞는 검증된 Team Skill이 있습니다.
이 작업 환경에 해당 절차를 적용하겠습니다.”

성공 후:

[Agent]
“설치와 사용 가능 여부까지 확인했습니다.
이번 실행은 실제 검증된 Skill 재사용으로 1회 기록됐습니다.”

기본 사용자 답변에 아래를 길게 노출하지 마:
- 전체 digest
- run_id
- counted=True
- reason=ok
- candidate_delta
- 내부 Python dataclass/schema
- 제품 CLI 진단 세부사항

필요하면 “상세” 또는 원문 로그에 보존하되,
현업 사용자의 기본 대화는 업무 중심이어야 한다.

기능 판정은 기존 실제 기준을 유지:
- 실제 pip 실패
- 실제 설치 성공
- 요청 version 확인
- import 성공
- 같은 작업 환경
- 성공한 실행만 usage +1
- retry/search/download만으로 +1 금지
- 기존 Skill 재사용 시 Candidate +0

────────────────────────────────────
2. P1 실제 사용자 대화를 원래 의도한 2-turn 흐름으로 정합화
────────────────────────────────────

P1은 지금보다 사람의 환경 지식이 자연스럽게 들어오는 스토리로 만든다.

핵심 제품 메시지:

“Coding Agent가 모든 사내환경을 처음부터 아는 것이 아니라,
업무를 아는 현업 사용자의 환경 사실 + Agent의 탐색 + 팀의 기존 경험을 결합한다.”

P1 시작:

[사용자]
“AAAAA01_직전_3달_생산량.xlsx를 읽고
다음달 예상 생산량을 포함한 추세선을 보여줘.”

Agent 흐름:

1) 실제 파일 대상 확인
2) 일반적인 XLSX direct parser 접근 실제 시도
3) 실제 실패 관찰
4) 현재 Case의 Team Skill 검색
5) 적용 가능한 Skill이 없으면 NO_MATCH
6) 여기서 곧바로 해결법을 알고 있는 것처럼 진행하지 않는다.

실패 + NO_MATCH 뒤 Agent는 짧게 사용자 환경 사실을 기다린다.

예:

[Agent]
“일반적인 XLSX 읽기로는 파일을 열 수 없었고,
현재 팀 Skill에서도 적용 가능한 해결 절차를 찾지 못했습니다.
사용자 환경에서 이 파일을 Excel로 직접 열어 볼 수 있는지는 확인이 필요합니다.”

이 상태는 실패 완료가 아니라 정상적인 operator-assisted discovery 중간 상태다.

그 뒤 실제 데모에서 사용자가:

[사용자]
“이상하네, 난 엑셀을 열어서 데이터를 볼 수 있는데?
한번 다른 방법으로 진행해봐.”

라고 말한다.

이 문장은 정답 힌트가 아니다.
xlwings / COM / pywin32 / library / API 이름을 사용자가 말하지 않는다.

이후 Agent가:

- Windows 환경
- 실제 Excel 애플리케이션
- 대상 workbook
- 허용된 read-only 접근 가능성

을 조사한다.

잠금 파일 하나만 보고 “정확한 workbook이 현재 열려 있다”고 확정하지 마.
환경 metadata의 NASCA(가상) 표시는 제공된 모의 환경 정보이지
Agent가 실제 보안제품을 진단한 결과가 아니다.

Agent가 실제 환경 조사 결과
이미 열린 Excel 애플리케이션을 통한 read-only 접근 방법을 발견한다.

현재 지원 구현은 Excel COM attach adapter이지만,
사용자 설명의 중심은 library 이름이 아니라:

“이미 사용자가 볼 수 있는 Excel 애플리케이션을 통해
원본을 저장하지 않고 값을 읽는 방법”

으로 한다.

필요하면 상세 정보에서:
“현재 구현 adapter: Excel COM attach”
정도로 표시할 수 있다.

────────────────────────────────────
3. P1 업무 완료 흐름
────────────────────────────────────

접근 성공 뒤 Agent는 현재 문서 자체를 보고:

- 시트
- UsedRange
- 월 column
- 생산량 column
- 데이터 시작 row

를 판단한다.

이 정답을 Skill이나 고정 prompt에서 제공하지 마.

task-mapping 도구 계약 자체는 명확하게 알려줘.

CLI/C9 help에서 최소한:

- 필수 key:
  `sheet`
  `month_col`
  `total_col`
  `first_row`
- column/row는 1-based integer
- UsedRange 상대좌표가 아니라 worksheet 절대 좌표
- month_col != total_col

임을 명시한다.

이것은 답을 가르치는 것이 아니라 도구 사용 계약이다.

그 후:

최근 완료 3개월
→ x=1,2,3
→ 3-point OLS
→ x=4
→ 음수이면 0 clamp

로 다음 달을 계산한다.

결과:

- 실제 3개월
- 예상 1개월
- 대상 월
- 단위
- 예상값

을 명확히 보여준다.

실제 PNG chart_ref를 생성한다.

최종 사용자 답변에는 반드시
사용자가 실제 열 수 있는 chart_ref의 파일 경로 또는 링크를 명확히 표시해.

“위 차트”라고만 쓰지 마.

────────────────────────────────────
4. P1 Candidate → Human → Replay → Publish → 다음 Agent
────────────────────────────────────

업무 성공과 Skill 게시를 섞지 않는다.

업무 완료 후 사용자에게 이해하기 쉽게:

[Agent]
“분석은 완료했습니다.

이번 과정에서 확인한 ‘환경 접근 절차’는 다른 팀원에게도 도움이 될 수 있습니다.
업무 데이터나 예측식은 제외하고 환경 접근 방법만 Team Skill 후보로 남길 수 있습니다.”

현재 lifecycle 계약상 Candidate 생성 시점과 사람 검토 시점은 기존 구현을 유지한다.
단지 사용자에게 후보와 게시를 같은 것으로 보이게 하지 마.

후보 화면/설명:

포함:
- 적용 조건
- 환경 접근 절차
- 검증 근거

제외:
- 생산량
- sheet
- column
- row
- 예측식
- 차트
- password
- 현재 file path

그 다음 human review에서는 exact:

id
version
digest

를 검토한 대상과 연결한다.

사람이 승인하기 전에는 승인 상태를 만들지 않는다.

승인 후:
→ 다른 workbook으로 independent Replay
→ exact candidate 동일성
→ fresh access
→ read-only 근거
→ PASS

Replay FAIL / NOT_RUN / 미실행이면 게시하지 않는다.

Replay PASS 후에만:
→ export
→ team-skill-store
→ Git push
→ 실제 remote commit 확인
→ PUBLISHED

push 실패:
→ PUBLISH_PENDING
→ PUBLISHED로 표시 금지

────────────────────────────────────
5. P1 마지막 장면은 반드시 “다음 팀원”이어야 함
────────────────────────────────────

최종 데모 가치는 후보 생성이 아니라
다음 Agent가 실제 도움받는 데 있다.

새 작업환경 / 새 Agent:

[다른 팀원]
“BBBBB02_직전_3달_생산량.xlsx도
다음달 예상 생산량을 포함해 보여줘.”

Agent:
→ 원격 Published Skill 수신
→ 현재 실패와 MATCH
→ exact Skill 확인
→ 원격 Skill이므로 사용자 실행 확인 요청

[사용자]
“확인한 이 Skill의 실행을 승인할게.”

Agent:
→ 새 workbook을 실제 읽음
→ 현재 문서의 다른 layout을 다시 해석
→ 업무 완료
→ chart
→ verified reuse +1
→ Candidate 0

마지막 제품 메시지:

“한 Agent가 해결한 사내환경의 시행착오를,
다음 Agent는 처음부터 다시 찾지 않습니다.”

이 장면을 P1의 최종 payoff로 둬.

────────────────────────────────────
6. 웹 ‘시연’ 탭도 위 실제 스토리와 일치시켜
────────────────────────────────────

현재 웹에서 이미 구현된:

P0 4단계
P1 Candidate / Review / Replay / Publish / Warm
실제 보관 chart
Manual Simulation 표시
실제 증거 링크

는 유지한다.

되돌리지 마.

P0 웹 흐름:

업무 요청
→ 실제 package supply failure
→ Agent가 Team Skill 검색
→ 적용
→ 설치/검증
→ verified reuse +1
→ Candidate 0

P1 웹 흐름은 반드시 사용자 환경 사실 한 턴을 추가:

업무 요청
→ direct access 실패
→ Team Skill NO_MATCH
→ Agent가 환경 사실 필요
→ 사용자:
  “이상하네, 난 엑셀을 열어서 데이터를 볼 수 있는데?
   한번 다른 방법으로 진행해봐.”
→ Agent 환경 탐색
→ Excel app read-only access 발견
→ 업무/graph 완료
→ 환경 절차 Candidate
→ Human Review
→ independent Replay
→ Git Publish
→ 새로운 Agent Warm
→ candidate 0 / reuse +1

웹 설명에서는 Org Knowledge 검색을 실제 제품이 실행하지 않았다면
실행한 것처럼 쓰지 않는다.

────────────────────────────────────
7. P0 웹 상태줄의 +1 의미를 더 직관적으로
────────────────────────────────────

우리가 승인된 DEMO_SEED baseline 20을 사용하는 설명용 상태가
현재 제품 계약에 실제 존재하는지 먼저 확인해.

그 계약이 현재 유효하다면 설명용 웹 시뮬레이션에서는:

초기:
DEMO_SEED 20
실제 검증 0
총 표시 20

P0 성공:
DEMO_SEED 20
실제 검증 1
총 표시 21

즉:

20회 적용 → 21회 적용
실제 검증 0회 → 1회

가 눈에 띄게 변하도록 해.

단:
- 이것은 `DEMO_SEED`라는 설명용 baseline임을 명시
- 실제 이력이라고 주장 금지
- 실제 backend 카운트를 조작하지 않음

현재 승인 계약에서 DEMO_SEED 20이 이미 폐기됐거나 사용하지 않는다면
다시 만들지 말고 현재 사실에 맞는 기존 Skill 사용 횟수 → +1 표현을 사용해.

특히 아래 두 개념을 섞지 마:

- 기존에 사용 가능한 Published Team Skill 수
- 이번 시연에서 새로 Published 된 Skill 수

P0 시작부터 기존 Team Skill을 사용하면서
“팀 Skill 0개”라고 보여 관객이 혼란스럽지 않게 해.

────────────────────────────────────
8. 최신 실제 Cold에서 발견된 UX 문제 수정
────────────────────────────────────

result/cold-review-20260909/response-review.md를 기준으로 최소 수정해.

A. 한국어 일관성
- 한국어 사용자 요청이면 기본 진행 설명도 한국어 유지
- 영어 한두 줄로 갑자기 전환하지 않기

B. 내부 개발용 용어 최소화
사용자에게 기본적으로 다음을 길게 보여주지 마:
- 제품 CLI
- procedure schema
- 내부 필드명
- coordinate correction
- candidate_delta
- run_id
- digest 전체

필요한 사용성/보안 한계만 짧게.

C. 입력 형식 재시도 감소
- 정확한 schema와 자료형을 --help/C9에서 제공
- 정답 sheet/column/value는 제공 금지

D. 관찰과 추정 분리
- lock file = 단서
- app attach/target workbook 확인 = 실제 확인
- NASCA(가상) = 제공된 환경 설명
- 특정 실제 보안제품 진단으로 확대 금지

E. chart 전달
- 결과에 실제 열 수 있는 chart_ref 명시
- headless Agent가 image Read 했다는 이유만으로
  사용자 Claude 화면에 그림이 보였다고 주장 금지

────────────────────────────────────
9. Requirements와 구현의 남은 정합성도 확인
────────────────────────────────────

FR-P1-2의 “Team Skill 및 제공된 Org Knowledge 실제 검색”과
현재 실제 구현을 대조해.

실제로 별도 Org Knowledge가 현재 실행에 제공되지 않는다면:
- “제공된 조직 지식 없음”
- “이번 검색 scope는 Team Skill”
처럼 정확히 표현할 수 있는지 확인해.

아직 존재하지 않는 Confluence/vector DB 연동을 새로 만들지 마.

Requirements 의미 변경이 필요하다면 그 한 항목만
AI-DLC change impact + 사용자 승인 대상으로 올려.

Replay도 확인해.

현재 제품이 실제 새 접근을 실행한다는 것과,
항상 다른 PC / 다른 Agent / 다른 문서를 기술적으로 강제한다는 것은 구분해.

기존 실제 다른-workbook Replay 증거는 보존한다.
없는 보장을 문서 표현으로 확대하지 마.

업무 OLS 검증도:
- 제품 내부 self-check
- 별도 expected oracle 기반 acceptance

를 구분해.

이미 있는 독립 expected-value 검증이 충분하면
새 검증 프레임워크를 만들지 마.

────────────────────────────────────
10. 수정 후 제품 검증
────────────────────────────────────

변경된 경로만 먼저 targeted regression.

그 후 필요한 전체 regression.

기존 성공 증거를 반복 실행해서 숫자를 부풀리지 마.

최소 확인:

P0:
- 실제 공급 실패
- Team Skill MATCH
- install 성공
- version/import 확인
- actual reuse +1
- candidate 0
- 같은 run retry 추가 카운트 없음

P1 Cold:
- direct parser 실제 실패
- Team Skill 실제 검색
- NO_MATCH
- 사용자 환경 사실 turn
- 그 뒤 Agent discovery
- read-only access
- 다른 layout 해석
- OLS
- chart_ref
- Candidate 1
- reuse 0
- 원본 불변

P1 lifecycle:
기존 candidate content/digest를 변경하지 않았다면
기존 검증된 approval/Replay/Publish evidence를 재사용 가능 여부를 명확히 판단해.
변경했다면 사람 재검토와 Replay를 다시 수행해야 한다.

────────────────────────────────────
11. 여기까지 완료 후 실제 Claude Code UI P0 시연을 딱 1회 수행
────────────────────────────────────

기능/UX 수정과 regression이 끝난 뒤에만 진행한다.

이 단계는 테스트 runner나 `claude -p` headless evidence가 아니다.

**실제 사람이 시연할 Claude Code UI를 Computer Use/desktop interaction으로 열어
P0 자연어 업무를 단 한 세션에서 1회 진행한다.**

조건:

- 새 isolated P0 workspace 사용
- 패키지 미설치 상태
- 기존 Team Skill은 준비된 상태
- usage는 해당 시연 시작 전 상태를 기록
- 사용자 prompt에 Skill 이름/실패 원인/해결 방법 힌트 없음
- `run-p0` 데모 명령을 직접 입력하지 않음
- Claude Code의 자연어 업무 진입점으로 수행
- statusline이 실제 Claude Code 하단에 표시되는 환경

Computer Use가 실제 사용 가능한 환경이면 반드시 그것으로:

1. P0 workspace에서 Claude Code UI 실행
2. Claude Code 입력창에 정확히 입력:

   “이 프로젝트 requirements.txt의 패키지를 설치해줘.”

3. 실제 Claude가 답변하고 도구를 사용하도록 진행
4. 일반 설치 실패를 실제 화면에서 확인
5. Agent가 스스로 Team Skill을 검색하는 과정 확인
6. Skill 적용
7. 설치/검증 성공
8. 최종 사용자 답변 확인
9. SkillLoop 하단 상태줄의 실제 reuse 변화 확인

**이 전체를 ‘P0 LIVE DEMO RUN #1’ 한 번의 실제 세션으로 취급한다.**

중간 오류가 나더라도 세션을 버리고 새 성공 세션으로 교체하지 마.
같은 세션 안에서 정상적으로 복구 가능하면 그대로 이어가고 기록해.

단,
환경 자체가 깨져 실행 불가능한 경우에는
FAIL/NOT_RUN으로 남기고 원인을 보고한 뒤
사용자 승인 없이 성공 증거를 새로 연출하지 마.

────────────────────────────────────
12. P0 LIVE DEMO RUN #1 화면 캡처
────────────────────────────────────

이 한 세션에서 실제 화면을 캡처해.

최소 권장 캡처:

A. `01-request.png`
- Claude Code 실제 UI
- 사용자가 입력한 자연어 P0 질문
- 하단 SkillLoop 상태줄
- 실행 시작 전 상태가 보이도록

B. `02-failure-and-search.png`
- 실제 pip supply failure
- Agent가 Team Skill을 찾는 흐름
- 가능하면 같은 Claude Code 화면에서 확인 가능하게

C. `03-success-and-reuse.png`
- 최종 설치/검증 성공 응답
- 하단 상태줄의 실제 reuse 증가
- Candidate 0 또는 기존 Skill 재사용임을 확인할 수 있는 화면

캡처는 한 번의 같은 세션에서 발생한 장면이어야 한다.
세 장의 서로 다른 성공 실행을 합쳐 하나처럼 만들지 마.

실제 한 화면에서 질문+핵심 답변+성공+상태줄까지 충분히 보이면
대표 screenshot 1장을 추가로 선정해도 좋다.

예:
`00-hero.png`

화면의 실제 내용은 조작하지 마.
자르기(crop)는 비관련 UI 제거 정도만 허용.
텍스트를 합성하거나 다른 실행 화면을 붙이지 마.

secret/token/password/private user data가 화면에 보이면
그 캡처를 제출하지 말고 안전하게 다시 화면 배치를 조정해서 캡처해.
실제 대화 내용 자체를 바꿔 가리는 방식은 금지.

────────────────────────────────────
13. 실제 시연 로그/증거 저장
────────────────────────────────────

예를 들어 다음처럼 별도 폴더를 사용해:

result/live-demo-p0-20260909/

최소:

README.md
01-request.png
02-failure-and-search.png
03-success-and-reuse.png
visible-transcript.md
run-context.json
verification.json

가능하면 추가:
00-hero.png

README.md에는:

- 이 기록이 실제 Claude Code interactive UI의
  `P0 LIVE DEMO RUN #1`이라는 점
- source SHA
- workspace가 fresh/isolated였는지
- exact 사용자 질문
- 시작 usage
- 최종 usage
- package/version/import 검증
- Candidate delta
- 캡처별 의미
- 중간 오류/재시도가 있었으면 그것
- 이 실행이 웹 설명용 simulation이 아니라 실제 실행이라는 점

을 기록해.

visible-transcript.md:
- 사용자에게 화면에 보인 질문/답변 위주
- private chain-of-thought 저장 금지
- secret/credential 저장 금지
- tool output은 필요한 범위만 사실 그대로
- 성공만 남기기 위해 중간 visible 오류를 삭제하지 마

verification.json:
- source_sha
- input prompt
- initial_count
- final_count
- expected_delta = 1
- actual_delta
- install_exit
- version_verified
- import_verified
- candidate_delta
- screenshots
- verdict

정도로 충분하다.

이 실제 시연 기록을 audit.md에도 새 entry로 append하되
기존 audit를 수정하지 마.

표현 예:
“P0 interactive live demonstration RUN #1 performed through actual Claude Code UI.
Natural-language request only; actual supply failure → Team Skill reuse → install/version/import PASS
→ verified reuse +1. Screenshots and visible transcript preserved under ...”

실제로 성공한 경우에만 PASS를 기록해.

────────────────────────────────────
14. Computer Use가 제공되지 않는 경우
────────────────────────────────────

Computer Use / desktop GUI interaction을 실제로 사용할 수 없다면:

- screenshot을 HTML로 재현해서 실제 Claude Code 캡처라고 만들지 마.
- 기존 headless trace를 interactive UI 증거라고 부르지 마.
- `P0 LIVE DEMO RUN #1 = NOT_RUN (computer-use unavailable)`로 보고해.
- 사용자에게 실제 Claude Code에서 수행해야 할 정확한 3~4단계만 안내해.

실제 GUI 사용 가능 여부를 추측하지 마.

────────────────────────────────────
15. 최종 웹/제출 표현
────────────────────────────────────

웹 `시연`은 계속:

“설명용 시뮬레이션”

으로 표시한다.

실제 P0 화면 캡처는 별도로:

“실제 Claude Code 실행”

이라고 명확하게 표시한다.

둘을 섞지 않는다.

가능하다면 웹 시연 또는 캡처 탭에서
`P0 실제 실행 보기`
링크/카드로 이번 실제 screenshot/evidence에 접근할 수 있게 하되,
이 변경이 현재 승인된 presentation artifact 범위 안인지 먼저 확인해.

────────────────────────────────────
16. 최종 제출 전 검증
────────────────────────────────────

모든 수정 후:

- targeted tests
- 전체 Python regression
- PBT
- web tests
- web production build
- P0/P1 demo progression
- 실제 chart asset
- README/state/audit 정합성
- public Pages
- GitHub CI

를 최종 source SHA에 대해 확인해.

CI가 아직 실행 중이라면 success라고 미리 쓰지 마.

다른 PC Warm은 팀원이 준비된 경우에만 실제 1회 수행:
remote Published Skill pull
→ exact confirmation
→ 업무 success
→ reuse +1
→ candidate 0
→ usage event push
→ receiver first import +1
→ repeated import +0

다른 PC를 못 쓰면 SAME_PC independent workspace와 TWO_DEVICE를 구분하고
B-PC NOT_RUN으로 남겨.

────────────────────────────────────
17. 하지 말 것
────────────────────────────────────

- 새 AI-DLC workflow 시작
- Inception 재시작
- 외부 사전 구현 Reference 재참조
- 기존 audit 삭제/재작성
- fake screenshot
- fake approval
- fake Replay
- fake PUBLISHED
- fake TWO_DEVICE
- P1을 범용 arbitrary-code learning engine으로 재개발
- 새 vector DB / Confluence integration
- 새 보안 서명 시스템
- 새 시나리오 추가
- 실제 카운트를 화면 연출 때문에 변경
- 후보 안에 업무 데이터/시트/열/예측식 저장
- 모든 오류를 성공처럼 숨기기

────────────────────────────────────
18. 마지막 보고 형식
────────────────────────────────────

마지막에는 아래만 보고해.

1. 변경 파일
2. 이번 작업이 따른 기존 AI-DLC 승인/계획 근거
3. P0 실제 대화 흐름 최종본
4. P1 실제 대화 흐름 최종본
5. 기능 검증 결과
6. UX 검증 결과
7. P0 LIVE DEMO RUN #1
   - PASS / FAIL / NOT_RUN
   - source SHA
   - 실제 질문
   - 시작/종료 reuse
   - screenshot 경로
   - visible transcript 경로
8. 웹 시연 검증 결과
9. CI / Pages 결과와 exact SHA
10. B-PC 여부
11. 남은 한계 / NOT_RUN
12. 사용자에게 필요한 다음 행동

설명보다 실제 결과와 증거를 우선해.