# 요구사항 확인 질문 (Requirements Verification)

**대상**: Agent SkillLoop (MVP) — Greenfield
**작성 목적**: WHAT/WHY를 확정하기 위한 요구사항 명확화. (Unit 개수·이름·사람별 할당·아키텍처 등 HOW는 이후 **Workflow Planning / Units Generation** 단계에서 제안·결정합니다.)

## 응답 방법
- 각 질문의 `[Answer]:` 뒤에 **선택지 문자(A, B, …)**를 적어 주세요.
- 맞는 선택지가 없으면 마지막 **X) Other**를 고르고 `[Answer]:` 뒤에 직접 설명을 적어 주세요.
- 여러 개를 함께 고르고 싶으면 문자를 함께 적고(예: `A, C`) 필요 시 설명을 덧붙여 주세요.
- 모두 작성하신 뒤 "완료" 또는 "done"이라고 알려 주세요.

---

## 인텐트 분석 요약 (AI 사전 분석 — 참고용)
- **요청 유형**: 신규 프로젝트(Greenfield MVP)
- **범위 추정**: 다중 컴포넌트 (Skill 저장/공유, 검색·적용, 결과 검증, 새 Skill 후보화, Agent 통합)
- **복잡도 추정**: 보통(Moderate) — 시간 제약과 4인 병렬 개발, 통합 위험 회피가 핵심 변수
- **명확성**: 제품 의도·시나리오는 명확. 제품 표면(Agent 호출 방식)·Skill 표현/공유 방식·환경 재현 방식·성공 조건이 미확정

아래 질문은 이 미확정 항목을 좁히기 위한 것입니다.

---

## Question 1 — MVP 완성 범위(P0/P1 우선순위)
제한된 시간 안에서 어떤 흐름을 "핵심 완성 대상"으로 확정할까요? (평가 완성도는 넓이보다 선택한 흐름의 실제 완료가 중요합니다.)

A) **P0 우선** — 기존 Skill 재사용 흐름을 먼저 완성하고, 시간이 남으면 P1 진행

B) **P0 + P1 둘 다** 핵심 흐름으로 완성 목표

C) **P1 우선** — 새 경험 축적 흐름을 먼저 완성하고, 시간이 남으면 P0 진행

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 2 — 제품 표면 / Agent 통합 방식
데모에서 "코딩 Agent"가 SkillLoop를 실제로 어떻게 호출하나요? (완성도·사용성 평가의 진입점과 직결됩니다.)

A) **Claude Code용 Skill + 로컬 스크립트(파일 기반)** — Agent가 프로젝트 내 Skill/스크립트를 호출

B) **독립 CLI 도구** (예: `skillloop search|apply|record ...`) — Agent가 셸 명령으로 호출

C) **라이브러리/모듈** — Agent 코드가 import해서 사용

D) **조합** — 핵심 로직은 CLI, Claude Code Skill이 얇은 wrapper로 감쌈

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 3 — Skill 공유 transport
검증된 Team Skill을 팀원 간 어떻게 공유·동기화하나요? (private Git sync를 선호한다고 하셨으나 아직 미승인 상태입니다.)

A) **private Git 기반 sync** — 별도 Git 저장소를 clone/pull/push로 Skill 동기화 (선호안)

B) **로컬 공유 폴더/디렉터리** — 단일 머신 또는 오프라인 공유, 네트워크 의존 최소화

C) **같은 저장소 내 디렉터리**(`skills/` 등)로 단순화 — 별도 transport 없이 커밋으로 공유

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 4 — Skill 아티팩트 표현 형태
공유되는 하나의 "Skill"은 무엇으로 표현되나요?

A) **메타데이터(YAML/JSON front-matter) + 절차 설명 Markdown** (사람이 읽고 Agent가 따르는 절차 문서)

B) **메타데이터 + 실행 가능한 스크립트 번들**(디렉터리: 설명 + `.ps1`/`.py` 등)

C) **단일 구조화 파일**(JSON/YAML)에 조건·절차를 필드로 기술

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 5 — Skill 검색 / 매칭 방식
사용자 요청에 맞는 기존 Skill을 어떻게 찾나요? (MVP 신뢰성·시간 예산에 영향)

A) **태그·키워드 기반 매칭** (간단·결정적, 디버깅 쉬움)

B) **자연어/의미 기반(임베딩) 매칭** (유연하나 모델·의존성 필요)

C) **목록에서 수동 선택** (Agent/사용자가 후보 중 선택)

D) **키워드 매칭 + 후보 제시 후 확인** (A + C 결합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 6 — P0 환경 제약(사내 패키지 공급)의 합성 재현 방식
"requirements.txt 설치 실패"를 어떤 합성 환경으로 재현하나요? (실제 회사 데이터·DRM 우회는 사용하지 않음)

A) **로컬 mock 패키지 인덱스 2개** — 기본(공개) 인덱스는 차단/실패, 사내 허용 인덱스에서만 성공

B) **오프라인 wheelhouse 디렉터리** — 허용된 로컬 경로에서만 설치 성공

C) **가짜 사내 index URL + 접근 조건** — Skill이 허용된 URL/경로/옵션을 알려줘 성공

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 7 — P1 보호 XLSX 재현 및 "허용된 대안"
"보호 XLSX 직접 읽기 실패 → 허용된 대안으로 업무 완료"를 어떻게 재현하나요?

A) **비밀번호/권한 보호로 직접 읽기 실패** → 환경에서 허용된 **export 경로**(예: 승인된 CSV 산출물)로 우회

B) **파일 접근 차단(권한/락)** → 허용된 **읽기 전용 복제/변환 도구** 경로 사용

C) **특정 라이브러리로는 실패** → 환경이 허용한 **다른 접근 절차/도구**로 성공

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 8 — 새 Skill 후보의 검토·재실행 게이트 (P1 성공 조건)
P1에서 만든 "새 Skill 후보"는 어디까지가 MVP 완료 상태인가요? (제안/승인/재실행/게시를 같은 상태로 표시하지 않도록)

A) **"공유 제안" 상태까지** — 사람 승인·재실행·게시는 상태 표시만(미수행)

B) **제안 → 사람 검토(승인/거절) → 재실행 검증 → 게시까지 실제 수행**

C) **제안 → 사람 검토(승인/거절)까지 실제 수행**, 재실행/게시는 상태 표시

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 9 — 사용 실적 / 검증 카운트 정의
"사용 실적 변화"를 어떻게 정의·집계하나요? (실패·단순 검색을 성공으로 세거나 재시도로 중복 집계되지 않도록)

A) **실제 성공 실행만 +1** — 실패·단순 검색은 미집계, 재시도 중복 방지

B) **성공/실패/적용 시도를 각각 별도 지표로 기록·표시**

C) **초기 합성 이력값 + 실제 성공 실행 증가분을 구분 표시**

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 10 — 구현 언어 / 런타임 선호
(Windows-native, 새 clone/압축해제본에서 실행 가능해야 함. 최종 확정은 NFR 단계지만 Unit·역할 분해 제안을 위해 방향을 확인합니다.)

A) **Python** — 표준 pip/`requirements.txt`, P0 시나리오와 자연스럽게 연결

B) **Node.js / TypeScript**

C) **PowerShell 중심 스크립트 + 최소 런타임**

D) **팀 역량에 맞춰 AI가 추천** (NFR 단계에서 확정)

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 11 — 통합 위험 회피(동시 편집)를 요구사항 제약으로 확정
"공통 state/lifecycle을 여러 세션이 동시에 수정해 통합 위험이 커지는 구조 회피"를 요구사항 수준 제약으로 명시할까요?

A) **예** — 각 Unit이 독립 파일/디렉터리를 소유하고 공유 mutable state를 최소화하는 것을 **필수 제약**으로 명시(요구사항·Workflow Planning에 반영)

B) **아니오** — 설계 단계에서만 고려하고 요구사항에는 명시하지 않음

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 12 — 보안 확장(Security Baseline) 적용 여부
이 프로젝트에 보안 확장 규칙을 강제할까요?

A) **예** — 모든 SECURITY 규칙을 차단 제약으로 강제 (프로덕션급 애플리케이션 권장)

B) **아니오** — SECURITY 규칙 전체 생략 (PoC·프로토타입·실험 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 13 — 복원력 확장(Resiliency Baseline) 적용 여부
복원력 베이스라인을 적용할까요? (AWS Well-Architected 신뢰성 기둥 기반의 **설계 시점 방향성 모범사례**이며, 프로덕션 준비·가용성/RTO/RPO 보장을 의미하지는 않습니다.)

A) **예** — 방향성 모범사례/설계 지침으로 적용 (business-critical 워크로드에, 이후 검증·강화 전제)

B) **아니오** — 복원력 베이스라인 생략 (빠른 반복이 중요한 PoC·프로토타입·실험 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

## Question 14 — 속성 기반 테스트(Property-Based Testing) 적용 여부
PBT 규칙을 강제할까요?

A) **예** — 모든 PBT 규칙을 차단 제약으로 강제 (비즈니스 로직·데이터 변환·직렬화·상태 컴포넌트가 있는 프로젝트 권장)

B) **부분** — 순수 함수와 직렬화 round-trip에만 PBT 강제 (알고리즘 복잡도가 제한적인 프로젝트에 적합)

C) **아니오** — PBT 규칙 전체 생략 (단순 CRUD·UI 전용·얇은 통합 계층에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 
