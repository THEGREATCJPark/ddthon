# 요구사항 문서 — Agent SkillLoop (MVP)

**단계**: INCEPTION / Requirements Analysis
**깊이(Depth)**: Standard
**Project Type**: Greenfield
**작성일**: 2026-09-08
**근거**: `requirement-verification-questions.md`의 사용자 응답(Q1–Q14) + `README.md` / `EVALUATION.md`

> 이 문서는 **WHAT/WHY**를 확정합니다. Unit 개수·이름·사람별 할당·아키텍처 등 **HOW**는 Workflow Planning / Units Generation에서 결정합니다.

---

## 1. 인텐트 분석 요약

| 항목 | 내용 |
|---|---|
| **User Request** | AI-DLC로 "Agent SkillLoop" MVP 개발. 핵심 의도: **"한 Agent의 해결 경험을 다음 Agent의 Skill로."** |
| **Request Type** | 신규 프로젝트(Greenfield) |
| **Scope** | 다중 컴포넌트 (Skill descriptor 관리 · Git sync · 검색/매칭 · 적용+검증(P0) · 새 Skill 후보 loop(P1) · 사용 실적 · CLI+Agent Skill 표면) |
| **Complexity** | 보통(Moderate) — 4인 병렬 개발 + 제한된 시간 + 통합 위험 회피가 핵심 변수 |
| **팀·시간** | 4명 / 9-8 13:30~21:00, 9-9 09:30~12:30 · 13:30~17:00 |
| **런타임 목표** | Windows-native, Python (Q10=A), 새 clone/압축해제본에서 실행 가능 |

---

## 2. 문제 정의와 대상 사용자 (평가: 문제 정의)

- **문제**: 사내 패키지 공급 경로·문서 접근 방식 등 환경 제약 때문에 코딩 Agent가 같은 실패·탐색을 반복한다. 해결 방법이 개인 대화에만 남으면 다른 작업/팀원이 재사용하기 어렵다.
- **Primary User (핵심 대상)**: **코딩 경험이 적은 사내 엔지니어**가 Coding Agent(Claude Code)를 이용해 **데이터 분석·업무 자동화**를 수행할 때, **사내환경 제약 때문에 반복해서 막히는 문제를 팀의 검증된 해결 경험으로 줄이고자 하는 사용자.**
- **관련 이해관계자(persona 후보)**: (1) 코딩 Agent와 함께 일하는 **개발자/팀**, (2) 새 Skill 후보를 검토·승인하는 **팀 리뷰어**, (3) 검증된 Skill을 재사용하는 **다음 Agent**. — 상세 persona/스토리는 User Stories(조건부) 또는 Workflow Planning에서 다룸.
- **범위 주의**: **P0/P1은 이 문제를 보여주는 대표 시나리오**이며, 제품을 pip 설치 도구나 Excel 분석 도구로 재정의하지 않는다. 제품 본질은 "검증된 팀 해결 경험(Skill)의 재사용·축적 loop"다.
- **성공 조건(제품 수준)**: 검증된 팀 Skill이 (a) 새 문제에 **실제로 재사용**되어 업무를 성공시키고, (b) 해결책이 없던 문제는 검증·검토·재실행을 거쳐 **재사용 가능한 새 Skill로 게시**되는 loop가 통제된 합성 환경에서 실제로 동작한다.

---

## 3. 제품 표면 및 통합 (Q2=D)

- **FR-SURF-1**: 사용자는 Claude Code에 자연어로 요청한다. **얇은 Agent Skill**이 요청을 받아 핵심 로직을 담은 **CLI 도구**를 호출한다.
- **FR-SURF-2**: 핵심 기능은 재현·디버깅 가능한 **CLI 명령**으로 제공된다(예시 동사: search / apply / record / propose / review / publish — 최종 명령 집합은 설계에서 확정).
- **FR-SURF-3**: CLI는 사람이 단독으로도 실행 가능해야 하며(데모·검증·재현), Agent Skill 없이도 동일 결과를 재현할 수 있어야 한다.

---

## 4. 기능 요구사항 (Functional Requirements)

### 4.1 Skill Descriptor 모델 (Q4=C)
- **FR-SKILL-1**: 하나의 Skill은 **단일 구조화 descriptor**(JSON/YAML)로 표현하며, 의미상 두 부분으로 구분한다:
  - **불변 content identity**: `id`, `version`, `digest`(아래 content에 대한 무결성 해시), `origin`(출처), `applicability`(적용 조건/태그·키워드), `procedure`(허용된 환경 접근 절차).
  - **가변 usage 이력·통계**: 실제 사용 실적(예: `actual_reuse`, 시연용 `DEMO_SEED`) — content identity와 **논리적으로 분리**된 별개 정보다.
  - 구체적인 저장 파일 배치·schema 분해(예: identity와 usage를 물리적으로 어떻게 나눌지)는 **HOW로 이후 Design에서 결정**한다.
- **FR-SKILL-2**: descriptor는 **실행 스크립트 자체를 공유·포함하지 않는다**. 절차는 "무엇을 어떻게 시도할지"에 대한 서술적 절차로 기술한다. (보안: NFR-SEC-4 원격 자동 실행 금지와 연결)
- **FR-SKILL-3**: descriptor는 **업무 원문·계산 결과·인증정보를 포함하지 않는다**(환경 접근 절차만). — NFR-SEC-1과 연결.
- **FR-SKILL-4**: `digest`는 **불변 content identity에 대해서만** 계산하며, 동일 내용의 중복 등록 방지(dedup)에 사용한다. **가변 usage 이력·통계(예: actual reuse +1)의 변경은 content의 `digest`를 바꾸지 않는다.** — NFR-RES-1, FR-USAGE와 연결.

### 4.2 공유 Transport — Git sync (Q3=A, 범위 변경 2026-09-08: 공유 대상 채택)
- **FR-SYNC-1 (범위 변경)**: 검증된 Team Skill은 **Git 원격의 공유 대상**에 저장되며 clone/pull/push로 팀 간 동기화한다. **이번 시연의 채택 대상**은 **동일 저장소(`THEGREATCJPark/ddthon`)의 `team-skill-store` branch**이며, 별도 private 저장소도 동일 transport 의미로 허용된다. `main`은 제품 소스·`aidlc-docs/` 산출물·실행 안내·시연 증거, `team-skill-store` branch는 **합성·비민감 공유 데이터**(공유 가능한 Skill descriptor + 필요한 재사용 이력)에 사용한다. (변경 근거·이력: `plans/change-impact-ui.md`. 과거 Q3=A "별도 private 저장소" 결정은 보존하고 이번 변경으로 일반화.)
- **FR-SYNC-2**: sync는 별도 서버/서비스 구축 없이 Git만으로 동작한다.
- **FR-SYNC-3**: sync 시 descriptor 무결성(`digest`)을 확인한다. **CONFLICT는 동일 `(id, version)`에 서로 다른 `digest`/content가 들어오는 경우로만 정의**하며, 이 경우 **감지·표시하고 자동 overwrite/파괴적 병합을 금지**한다. 서로 다른 **version 자체는 conflict가 아니며**, 정상적인 새 version 추가는 허용한다. — NFR-RES-2.
- **FR-SYNC-4**: sync 실패(네트워크·인증·충돌) 시 로컬 상태를 손상시키지 않고 명확한 오류·재시도 가능 상태를 남긴다. — NFR-RES-3.
- **FR-SYNC-5 (신규 — 로컬 상태 비전달)**: **각 실행 환경의 로컬 저장 상태(DB 파일 자체)는 Git으로 전달하지 않는다.** 공유 대상은 **공유 가능한 descriptor + 비민감 재사용 이력 레코드**뿐이며, 로컬 상태는 각 환경에 보존된다(NFR-RES-4, NFR-SEC-1과 정합).

### 4.3 검색 / 매칭 (Q5=D)
- **FR-MATCH-1**: 결정적 **키워드·태그 기반 검색**으로 후보 Skill 목록을 만든다.
- **FR-MATCH-2**: 후보를 곧바로 적용하지 않고, **현재 문제에 실제 적용 가능한지 확인(applicability 체크)** 후 선택/적용한다.
- **FR-MATCH-3**: 무관한 Skill(예: P0용 Skill)이 다른 문제(P1)의 해결책으로 잘못 선택되지 않도록 매칭 결과에 근거(매칭된 키워드/조건)를 제시한다.

### 4.4 P0 — 기존 Skill 재사용 흐름 (Q1=B 우선순위 1, Q6=A)
- **FR-P0-1**: `requirements.txt` 설치 요청 시나리오에서 **실제 pip 설치 실패**를 통제된 합성 환경으로 재현한다.
- **FR-P0-2 (환경 재현)**: 로컬 mock 패키지 인덱스 2개를 둔다 — **공개환경 모의 index에는 대상 패키지를 두지 않아 실패**시키고, **허용된 사내 모의 index에만 무해한 wheel**을 두어 성공 가능하게 한다. 외부 인터넷 장애에 의존하지 않는다.
- **FR-P0-3**: 기존 Team Skill을 검색·적용하여 허용된 index/옵션으로 **실제 설치를 성공**시키고, 설치 결과를 **검증**한다(패키지 import/존재 확인 등 실제 효과 확인).
- **FR-P0-4**: 적용 성공 시 해당 Skill의 **actual reuse 카운트를 +1**(NFR/§4.6 규칙 준수).

### 4.5 P1 — 새 경험 축적 loop (Q1=B 우선순위 2, Q7=C, Q8=B)
- **FR-P1-1**: 보호된 합성 XLSX의 **직접 parser 접근을 실제로 실패**시킨다.
- **FR-P1-2 (실제 검색 후 판정)**: 현재 Case에서 **Team Skill 및 제공된 Org Knowledge를 실제로 검색**하고, **검색 범위·질의·결과를 기록**한다.
  - 적용 가능한 Skill이 **실제로 없을 때만 `NO_MATCH`**로 진행한다.
  - 관련 Skill이 **실제 존재하면 숨기거나 제거하지 말고 재사용 경로(§4.4 P0 계열)를 따른다.**
  - **검색 미호출·오류·timeout은 `NO_MATCH`가 아니다**(별도 오류 상태로 표시하며, 재사용 기회를 무단 스킵하지 않는다).
- **FR-P1-3 (환경 사실 확인)**: 사용자에게 환경 사실을 확인한다(대화형 입력).
- **FR-P1-4 (허용된 대안 탐색)**: 정답 라이브러리를 요구사항에서 **고정하지 않고**, Agent가 Windows 환경에서 **허용된 read-only 대안 절차**를 탐색해 파일 내용을 얻는다.
- **FR-P1-5 (업무 완료 — 계산 기준 확정, CQ-1)**: 이전 3개 완료 월의 생산량을 읽어 다음 달 예상 생산량을 반영한 **추세선**을 산출한다(합성 데이터). 성공 기준:
  - **기준월**: "다음 달"은 **데이터에 포함된 마지막 완료 월의 다음 달**로 한다(실행 시점/오늘 날짜의 다음 달이 아니다).
  - **예측 방식**: 이전 3개 완료 월의 **월별 총생산량 3점**을 이용한 **단순 OLS 선형 추세**. 세 월을 시간순 `x=1,2,3`으로 두고 월별 총생산량에 선형 추세를 적합하여 **`x=4`를 다음 달 예상 생산량**으로 계산한다.
  - **음수 clamp**: 계산 결과가 음수이면 **0으로 제한**한다(생산량 업무 의미상).
  - **표시**: 결과 화면/그래프에 **실제 3개월과 예상 1개월을 구분**하고, **예측 대상 월·단위·예상값**을 명확히 표시한다.
  - **경계**: 이 계산 기준은 **P1 업무 결과 검증용**이다. 새 Skill 후보에는 **예측 계산식·생산량 값·차트 로직을 넣지 않고 환경 접근 절차만** 남긴다(FR-P1-6, NFR-SEC-1과 정합).
- **FR-P1-6 (Skill 후보화)**: 업무 계산법이 아니라 **환경 접근 절차만** 새 Skill 후보 descriptor로 만든다.
- **FR-P1-7 (검토·재실행·게시 loop — 실제 수행)**: 후보 → **사람 검토(승인/거절)** → **독립 Replay 검증** → 승인 시 **Git 공유 대상(이번 시연: `team-skill-store` branch)에 게시**까지 실제 수행한다. 각 상태(제안/검토/Replay/게시)는 **서로 다른 상태로 명확히 구분**해 표시한다. **게시 완료(PUBLISHED) 상태는 원격 push 성공 확인 후에만** 표시하며, 게이트는 충족했으나 원격 전송이 실패하면 로컬 확정 상태를 보존하고 재시도 근거를 남긴다(로컬 확정 ≠ 원격 게시 완료, FR-SYNC-4와 정합).
  - **게시(Published) 성공 조건** (모두 충족해야 게시):
    - 사람이 승인한 **exact candidate의 content/version/digest**와 **Replay에 사용한 candidate의 content/version/digest가 동일**해야 한다.
    - 해당 **exact candidate에 대한 사람 승인**이 있어야 한다.
    - 해당 **exact candidate의 독립 Replay가 실제 `PASS`**여야 한다.
    - Replay가 **`FAIL` / `NOT_RUN` / 미완료이면 게시하지 않는다.**
    - **사람 승인 후 candidate 내용/version/digest가 바뀌었다면**, 기존 승인을 새 내용에 승계하지 않는다. 변경된 candidate는 **다시 검토·Replay 대상**이다.
  - (구체적 schema/class/API/state machine 구현 방식은 Design에서 결정 — HOW)

### 4.6 사용 실적 / 카운트 (Q9=A,C)
- **FR-USAGE-1**: **검증된 실제 Skill 적용 성공만** `actual_reuse += 1`.
- **FR-USAGE-2**: 실패·단순 검색·Replay·retry·sync는 카운트를 증가시키지 않는다(재시도 중복 집계 금지).
- **FR-USAGE-3**: 초기 시연용 이력(`DEMO_SEED`, 합성)은 **실제 성공 증가분과 명확히 구분**해 표시한다.
- **FR-USAGE-4 (신규 — 공유 재사용 이력 집계, 범위 변경)**: 여러 실행 환경의 **실제 검증 재사용 이력**을 공유 대상(§4.2)으로 주고받아 조직 관점으로 집계할 수 있다. **재동기화 시 재사용 이벤트를 이벤트 식별자 기준으로 dedup**하여 중복 집계(+1 중복)를 금지한다. 공유 재사용 이력은 **비민감·합성**만 포함하며 원본 업무 데이터·secret를 포함하지 않는다(NFR-SEC-1). `DEMO_SEED`는 실제 실적으로 집계하지 않는다(FR-USAGE-3과 정합).

### 4.7 UI 표면 — 상태줄 + 로컬 읽기전용 대시보드 (신규, 범위 변경 2026-09-08)
> UI 요구사항의 현재 근거는 **사용자가 승인한 상태줄·로컬 읽기전용 대시보드 범위(SCOPE-CHANGE-1)**다. 아래 FR-UI/FR-ORG와 현재 승인 산출물을 기준으로 구현하며 특정 외부 저장소의 구현 코드·backend 구조를 요구하지 않는다. 과거 표현 참고 사실은 audit 및 변경 검토 이력에 보존한다.
- **FR-UI-1 (상태줄)**: Claude Code 하단 상태줄에 조직 현황을 **간단히** 표시한다 — 조직 Skill 수·내 기여·인기 Skill·재사용 현황. 실제 검증 실적과 `DEMO_SEED`를 구분해 표시한다.
- **FR-UI-2 (로컬 읽기전용 대시보드)**: **로컬 브라우저 읽기전용** 대시보드로 조직 요약·Skill 목록/검색/상세·기여 및 실제 재사용 현황·검토/Replay/게시 상태·최근 활동을 표시한다. **쓰기·승인·게시 등 상태 변경 액션은 제공하지 않는다**(NFR-SEC-2). localhost 시연 범위이며 인증·호스팅·멀티유저 서버는 범위 외.
- **FR-UI-3 (동일 집계 기준)**: 상태줄과 대시보드는 **동일한 집계 기준(단일 read-model 스냅샷)** 위에서 같은 수치·상태를 표시하고, **실제 검증 실적과 `DEMO_SEED`를 구분**한다(FR-USAGE-3/4). 화면은 **마지막 동기화 기준과 현재 조회 가능한 데이터 범위**를 함께 표시한다.

### 4.8 조직 집계 (신규, 범위 변경 — WHAT만; 소유·계약은 Application Design, schema/알고리즘은 Functional Design)
> **판단 정정**: 로컬 Skill 조회·로컬 usage 조회가 있다는 사실만으로 조직 전체 현황을 제공할 수 있다고 보지 않는다. 아래 계약 충족이 필요하다.
- **FR-ORG-1**: 여러 환경에서 받은 공유 게시 Skill을 **중복·버전을 구분**해 집계한다(서로 다른 Skill 기준 수, dedup은 digest·`(id,version)` 기준).
- **FR-ORG-2**: **작성자·재사용자 식별 기준**(작성자=`origin`, 재사용자=alias)과 **팀원별 기여·재사용 집계** 규칙을 둔다.
- **FR-ORG-3**: **다른 환경의 실제 재사용 이력을 전달·반영**하고 재동기화 시 중복 집계를 방지한다(FR-USAGE-4).
- **FR-ORG-4**: **로컬 후보/검토/게시대기 상태**와 **원격 공유 완료(PUBLISHED=push 성공) 상태**를 구분해 집계·표시한다.
- **FR-ORG-5**: **마지막 동기화 기준(시각·branch revision)과 현재 조회 가능한 데이터 범위**를 제공한다. 화면은 읽기전용이나, 조직 집계를 위해 **공유 usage 동기화·import 계약 보완이 필요**하다(HOW는 설계 단계).

---

## 5. 비기능 요구사항 (Non-Functional Requirements — 최소·핵심만)

> 사용자 요청에 따라 불필요한 범용 NFR·미래 인프라는 포함하지 않는다. 아래는 제품 의미상 필수 항목만.

### 5.1 런타임/이식성
- **NFR-RUN-1**: Windows-native, **Python** 기반. 새 clone 또는 ZIP 압축해제본에서 선언된 의존성만으로 실행 가능해야 한다(개인 PC 전역 설정 비의존).
  - 승인된 P1 Excel 한정 예외(B bb3ac2e 이후 인계 반영): Office 암호화 합성 파일 + 실행 중 Excel read-only attach는 Excel 설치·실행, 사용자가 파일을 열어둔 상태, pywin32를 사전조건으로 한다. 미충족은 NOT_RUN. P0/기타 범위로 확대하지 않고 독립 Replay·게시 게이트는 유지한다.
- **NFR-RUN-2**: 하나의 명확한 제품 진입점과 의존성 선언(`requirements.txt` 등)을 둔다. 외부 모델/서비스가 필요하면 그 사실과 대안을 명시한다.

### 5.2 통합 위험 회피 (Q11=X — 제약만 명시)
- **NFR-INT-1**: **공유 mutable state와 공통 lifecycle의 동시 수정을 최소화**해야 한다. (구체적 파일/디렉터리 소유권·단일 owner 등 HOW는 Workflow Planning / Units Generation에서 결정)

### 5.3 보안 (Q12=X — 핵심만 유지, Security Baseline 전체 강제 아님)
- **NFR-SEC-1**: 공유 Skill 및 제출 증거에 **secret·인증정보·원본 업무 데이터**를 포함하지 않는다.
- **NFR-SEC-2**: 승인된 대상에 대해서만 **read-only** 접근을 수행한다(DRM 우회·비허용 접근 금지).
- **NFR-SEC-3**: 입력 및 descriptor에 대한 **입력/무결성 검증**(digest 확인 포함)을 수행한다.
- **NFR-SEC-4**: **원격에서 받은 Skill을 자동 실행하지 않는다**(절차는 서술적, 실행은 사람/명시적 확인 하에).

### 5.4 복원력 (Q13=B — 범용 복원력 미확대, 아래만)
- **NFR-RES-1**: 중복 등록 방지(dedup, digest 기반).
- **NFR-RES-2**: **CONFLICT는 동일 `(id, version)`에 서로 다른 `digest`/content가 존재할 때만 판정**한다(서로 다른 version 자체는 conflict가 아니다). CONFLICT는 감지·표시하며 자동 overwrite/파괴적 병합을 금지한다. — FR-SYNC-3과 동일 의미.
- **NFR-RES-3**: sync 실패 시 로컬 상태 보존 및 재시도 가능.
- **NFR-RES-4**: 프로세스 재시작 시 로컬 Skill 상태·카운트 보존.

### 5.5 테스트 (Q14=B — PBT Partial + 프로세스/계약/회귀)
- **NFR-TEST-1**: **PBT(Partial)** — 강제 규칙 PBT-02(round-trip), PBT-03(invariant), PBT-07(generator), PBT-08(shrinking·seed 재현), PBT-09(framework: Python은 Hypothesis). 적용 대상: descriptor 직렬화 round-trip, digest·dedup 등 순수·불변 로직.
- **NFR-TEST-2**: P0/P1 사용자 흐름은 **실제 process·contract·회귀 테스트**로 검증한다(화면 문구가 아닌 실제 효과 확인).
- **NFR-TEST-3**: 외부 모델/서비스가 필요한 검증은 모의 검증과 **분리 표시**하고, 미실행은 `NOT_RUN`으로 표시한다.

---

## 6. 제약·가정 (Constraints & Assumptions)
- **CON-1**: 실제 회사 데이터·DRM 우회 사용 금지. 모든 데이터는 **합성**, 환경은 통제된 모의 환경.
- **CON-2 (확정)**: 제출은 **public GitHub 기본 branch 또는 source ZIP**로 하며, **private Git 제출은 불가**하다. 제출본에는 실제 source + **`aidlc-docs/` 전체 보존** + README + 동작 screenshots/result를 포함한다. **정합 주석(범위 변경)**: 공유 대상을 동일 저장소 `team-skill-store` branch로 채택한 것은 CON-2와 정합한다(같은 public 저장소 사용). 단 해당 branch에는 **secret·원본 업무 데이터를 포함하지 않고**(NFR-SEC-1) 합성·비민감 공유 데이터만 둔다.
- **CON-3 (확정 — 최신 운영진 제출 가이드)**: 최종 점수 = **AI 심사 40% + 인간 투표 60%**. AI 심사는 **100점 만점의 6개 항목**으로 구성되며, 공개된 항목별 배점은 **AI-DLC 활용도 25 / 문제 정의 및 해결 20 / 창의성 15 / 완성도 15 / 사용성 15 / 유지보수성 및 보안 10**이다. AI 심사 결과는 인간 심사위원의 Gating으로 보정될 수 있다. 인간 투표는 전시 페이지의 참가자 표를 환산한다. 제출 방식/보존 요건은 CON-2와 동일(확정).
- **CON-3a (미확정)**: 이번 최신 안내에서 **확인되지 않은** 항목만 별도 미확정으로 둔다 → **제출 기한, 인터넷 접근 조건, 모델 접근 조건**. (확인되면 반영)
- **ASSUMPTION-1 (범위 변경 갱신)**: Git sync 대상은 **동일 저장소 `THEGREATCJPark/ddthon`의 `team-skill-store` branch**(합성·비민감 공유 데이터)로 채택한다. 로컬 저장 상태(DB)는 Git으로 전달하지 않는다(FR-SYNC-5). 실제 branch·Git 작업 경로와 세부 운용 방식은 **미결정**이며 설계 승인 + Units 담당 확정 후 초기 구현 준비에 배치한다. (과거 "별도 private 저장소" 가정은 change 이력으로 보존.)

---

## 7. 범위 외 (Out of Scope, MVP)
- 범용 HA/RTO/RPO 복원력 설계, 프로덕션급 보안 전체 강제, 미래 배포/모니터링 인프라(Operations).
- 의미 기반(임베딩) 검색, 실행 스크립트 자체의 공유·자동 실행.
- P0/P1 외 추가 시나리오.

---

## 8. 리스크
- **RISK-1 (범위/시간)**: Q1=B(P0+P1 모두) + Q8=B(승인된 candidate → human review → independent Replay → publish까지 실제 수행)는 4인·제한 시간 대비 **야심적**이다.
  - **요구사항 지위**: Q8=B의 전체 loop(검토·독립 Replay·게시)는 **현재 요구사항으로 유지**된다. **이 Risk 문단은 요구사항을 선택사항으로 낮추지 않는다.**
  - **허용되는 것**: Workflow Planning에서 실행을 **time-box** 하고 P0 안정화를 선행할 수 있다.
  - **범위 축소가 필요할 경우**: 별도의 **scope/change approval**을 받아야 하며, 승인 없이 요구사항을 축소하지 않는다.
  - **미완료 처리**: 요구사항을 변경하지 않은 상태에서 시간상 완료하지 못하면 해당 흐름을 **`PARTIAL` / `NOT_RUN`으로 정직하게 기록**한다(완료로 표시하지 않음).
- **RISK-2 (통합 위험)**: 병렬 개발 중 공유 state 충돌. → NFR-INT-1 + Workflow Planning의 Unit 분해로 완화.

---

## 8.1 Clarification 상태
- **CQ-1** (`requirement-clarification-questions.md`): ✅ **결정됨** — P1 "다음 달"=마지막 완료 월+1, 3점 OLS(`x=1,2,3`→`x=4`), 음수 0 clamp, 실제3+예상1 구분 표시, 계산법·값·차트 로직은 Skill 후보 제외. FR-P1-5에 반영 완료.
- **남은 미해결 clarification**: 없음(요구사항 승인만 대기).

## 9. 확장 규칙 준수 요약 (이 단계)
| 확장 | 상태 | 이 단계 적용 |
|---|---|---|
| Security Baseline | Disabled(전체) | 핵심 보안 요구를 NFR-SEC-1~4로 반영 |
| Resiliency Baseline | Disabled(전체) | 필요한 항목만 NFR-RES-1~4로 반영 |
| Property-Based Testing | **Enabled (Partial)** | PBT-09 framework(Hypothesis) 선정 방향 기록, 대상 로직 식별 → Functional Design(PBT-01)에서 구체화 예정. 현 단계 blocking 위반 없음 |

---

## 10. 핵심 요구사항 요약
Agent SkillLoop MVP는 **Python/Windows-native CLI + 얇은 Claude Code Skill**로, **구조화 descriptor** 기반 Team Skill을 **Git 공유 대상(이번 시연: 동일 저장소 `team-skill-store` branch, 합성·비민감)**로 공유하고, 결정적 검색으로 재사용한다. **P0**(합성 이중 index로 pip 실패→Skill 적용→실제 설치 성공·검증·reuse+1)와 **P1**(보호 XLSX 직접 접근 실패→환경 사실 확인→허용 read-only 대안 탐색→업무 완료→환경 절차만 새 Skill 후보→사람 검토·독립 Replay·게시)을 통제된 합성 환경에서 실제로 동작시키는 것이 목표다. **상태줄 + 로컬 읽기전용 대시보드**(FR-UI)로 동일 집계 기준의 조직 현황을 표시하되 실제 검증 실적과 `DEMO_SEED`를 구분하며, 조직 집계에는 공유 usage 동기화·dedup·last-sync 계약(FR-USAGE-4, FR-ORG)이 필요하다. 보안·복원력은 제품 의미상 핵심 항목만, 테스트는 PBT(Partial)+실제 프로세스/계약/회귀로 한정한다. 통합 위험은 공유 state 동시 수정 최소화 제약으로 다룬다.

## Approved operator/org demo alignment (2026-09-09)

Existing product scope maintained. The live demonstration may select explicit team-skill-demo-20260909 on the same ddthon remote, while preserving original team-skill-store history. New live database starts with validated P0 only; P1 Cold searches it and the user approves newly discovered P1 publication. Exact human review, independent Replay and confirmed push remain required. Operator-only no-prompt viewing is environment preparation, not Agent discovery. End-of-task candidate triggers a publication permission invitation; no separate user publish request is required. No S3 adapter or general NASCA detection is claimed.
