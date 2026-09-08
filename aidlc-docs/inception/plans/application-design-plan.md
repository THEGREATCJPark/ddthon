# Application Design Plan — Agent SkillLoop

**단계**: INCEPTION / Application Design — Part 1 (Plan)
**작성일**: 2026-09-08
**상태**: ✅ **승인됨 (2026-09-08)** — AD-Q1~Q6 응답 반영, 정합성 확인. Part 2 생성 근거.
**근거**: 승인된 `requirements.md`, 승인된 `stories.md`/`personas.md`, `execution-plan.md`(SKIP-BOUNDARY-1/2)

> 이 계획은 **어떤 컴포넌트/책임/계약을 정의할지**와 **설계 결정 질문**을 확인받는 문서다. 컴포넌트는 **분석·제안**이며, **실제 Unit 분해·사람별 배정은 Units Generation에서 결정**한다. **기존 seam 6개(a~f)를 컴포넌트/Unit 6개로 확정하지 않는다.**
> 아래 **AD-Q1~AD-Q6에 `[Answer]:` 태그로 답**해 주세요. 맞는 게 없으면 **X) Other**에 직접 적어 주세요. 질문 응답 전에는 산출물(Part 2)을 생성하지 않습니다.

---

## 1. 설계 범위 (분석 요약)

승인된 요구사항·스토리에서 도출한 **책임 영역**(컴포넌트 후보 — 개수 확정 아님):

- **Skill 표현·무결성**: 구조화 descriptor의 불변 identity(id/version/digest/origin/applicability/procedure) + 가변 usage(actual_reuse/DEMO_SEED)의 **논리적 분리**, digest 계산·dedup (FR-SKILL-1~4, FR-USAGE-1~3, NFR-RES-1)
- **로컬 저장·상태 보존**: Skill·usage·상태의 로컬 영속화, 재시작 보존 (NFR-RES-4)
- **원격 동기화·충돌**: private Git clone/pull/push, digest 확인, CONFLICT 판정(동일 (id,version)+상이 digest만), 실패 시 로컬 보존 (FR-SYNC-1~4, NFR-RES-2/3)
- **검색·매칭**: 결정적 키워드·태그 검색 + applicability 확인 + 매칭 근거 (FR-MATCH-1~3)
- **적용·검증(P0)**: 이중 mock index 환경에서 실제 설치·검증, reuse 카운트 트리거 (FR-P0-1~4)
- **새 경험 loop(P1)**: 직접 접근 실패·실제 검색·NO_MATCH, 환경 사실 확인, 대안 탐색, 업무 완료(OLS), 절차만 후보화, 검토·독립 Replay·게시 게이트 (FR-P1-1~7)
- **제품 표면**: CLI 명령 집합 + 얇은 Agent Skill wrapper, 사람 단독 재현 (FR-SURF-1~3)

**핵심 설계 관심사(사용자 지시)**: (1) Skill **identity/usage 책임 분리**, (2) **검토·Replay·게시** 책임, (3) **원격 sync** 책임을 명확히 구분하고, **공유 state·lifecycle의 중복 구현과 동시 수정 위험**(NFR-INT-1)을 줄인다.

---

## 2. 생성 예정 산출물 (Part 2 — 공식 필수)

- [ ] `application-design/components.md` — 컴포넌트 정의·책임·인터페이스
- [ ] `application-design/component-methods.md` — 메서드 시그니처·입출력(상세 비즈니스 규칙은 Functional Design)
- [ ] `application-design/services.md` — 서비스 정의·오케스트레이션(P0/P1 흐름 조율)
- [ ] `application-design/component-dependency.md` — 의존성 매트릭스·통신 패턴·데이터 흐름(Mermaid + 텍스트 대안)
- [ ] `application-design/application-design.md` — 위 문서 통합
- [ ] 설계 완전성·정합성 검증(요구사항/스토리 추적, SKIP-BOUNDARY-1/2 반영 확인)

**경계**: 새 기능/NFR 추가 금지. Unit 수·사람 배정·라이브러리·클래스 세부는 확정하지 않음(제안·후보만). seam은 후보 유지.

---

## 3. 설계 결정 질문 (AD-Q1 ~ AD-Q6)

### AD-Q1 — 컴포넌트 경계 구성 방식
책임 영역을 컴포넌트로 묶는 기준은?

A) **책임(도메인) 기준으로 응집도 높게 묶되 개수는 설계에서 도출** (Recommended) — 표면(CLI/Skill), Skill 모델·무결성, 저장·동기화, 검색·매칭, 실행 흐름(P0/P1 오케스트레이션) 등 **책임 축**으로 나누고 seam 6개에 강제 대응시키지 않음

B) 기존 seam (a)~(f)를 그대로 6개 컴포넌트로 채택

C) 최소 컴포넌트(2~3개)로 크게 묶고 내부 모듈로 세분

X) Other (please describe after [Answer]: tag below)

[Answer]: A — 책임 축으로 도출. seam 일대일 대응·컴포넌트 수 사전 고정 안 함. 함께 변경되는 공통 lifecycle은 과도하게 쪼개지 않음.

### AD-Q2 — Skill identity vs usage 책임 분리
불변 identity와 가변 usage의 책임을 어떻게 나눌까요?

A) **별도 컴포넌트/저장 책임으로 분리 — identity(읽기 위주·digest 대상)와 usage(append 위주·카운트) 인터페이스를 분리** (Recommended) — digest 불변 보장(FR-SKILL-4)과 동시 수정 위험 감소에 유리

B) 단일 컴포넌트가 둘 다 관리하되 내부에서 논리 분리만

X) Other (please describe after [Answer]: tag below)

[Answer]: A — 인터페이스 분리. 불변 content와 가변 usage의 조회·변경 책임 구분, usage 변경은 digest 불변. 별도 DB·별도 실행 서비스까지 분리 불필요.

### AD-Q3 — 검토·Replay·게시(P1-7)의 책임 위치
게시 게이트(사람 승인·독립 Replay·digest 동일성·상태 구분)를 담당하는 책임은?

A) **전용 "게시 파이프라인" 서비스로 분리 — Replay 실행은 독립 컴포넌트에 위임, 게시 결정(게이트)만 이 서비스가 오케스트레이션** (Recommended) — 상태 구분·무승계·FAIL/NOT_RUN 게시 금지 규칙을 한 곳에서 강제

B) 원격 sync 컴포넌트가 게시까지 함께 담당

C) CLI 표면이 각 단계를 직접 순차 호출(전용 서비스 없음)

X) Other (please describe after [Answer]: tag below)

[Answer]: A — 전용 게시 파이프라인 서비스(내부 논리 서비스). 검토·독립 Replay·게시·상태 전이를 한곳에서. 검증 실제 결과 + exact candidate 승인 근거 확인 후 게시, CLI·sync가 게이트 우회 금지.

### AD-Q4 — 원격 sync와 로컬 저장의 책임 경계
private Git 원격 동기화와 로컬 영속화의 관계는?

A) **로컬 저장(store)과 원격 sync를 분리하고, sync는 store 위에서 동작(clone/pull/push·digest·CONFLICT 판정)** (Recommended) — SKIP-BOUNDARY-2(원격 sync 유지) 준수, 실패 시 로컬 보존(NFR-RES-3) 명확

B) 저장과 sync를 한 컴포넌트로 통합

X) Other (please describe after [Answer]: tag below)

[Answer]: A — 로컬 저장소의 명시적 import/export 계약 위에서 sync 동작. Git adapter=전송, 로컬 저장 컴포넌트=무결성·충돌·중복 방지·저장. sync가 저장 파일 직접 수정·별도 승인/게시 lifecycle 구현 금지. 원격 상태 문자열만으로 검증 완료 인정 금지.

### AD-Q5 — 컴포넌트 간 통신·계약 스타일 (NFR-INT-1)
동시 수정 위험을 줄이기 위한 통신·소유 방식은?

A) **컴포넌트 간은 명시적 인터페이스(함수/모듈 계약) 호출, 공유 state는 소유 컴포넌트만 쓰기·타 컴포넌트는 인터페이스 경유 읽기** (Recommended) — 계약을 먼저 고정해 병렬 개발 시 동시 수정·중복 구현 회피

B) 공유 데이터 구조를 여러 컴포넌트가 직접 읽고 씀

X) Other (please describe after [Answer]: tag below)

[Answer]: A — 명시적 계약 + 소유 컴포넌트만 쓰기. Python 내부 호출 기본, 입력·출력·오류·상태 변경 책임 정의. 타 컴포넌트 저장 상태 직접 수정 금지. 실제 성공 기록 식별로 retry·sync·restart 중복 집계 방지. 네트워크 서비스·메시지 브로커 미도입.

### AD-Q6 — CLI 표면과 Agent Skill의 책임
CLI와 얇은 Agent Skill의 관계는?

A) **핵심 로직은 CLI(단독 재현 가능), Agent Skill은 자연어→CLI 호출만 하는 얇은 wrapper** (Recommended) — FR-SURF-3(사람 단독 재현) 정합, 로직 중복 없음

B) Agent Skill에도 일부 핵심 로직을 둠

X) Other (please describe after [Answer]: tag below)

[Answer]: A — CLI로 핵심 기능 제공, Agent Skill은 얇은 wrapper(자연어→CLI). 검증·카운트·게시 판단 wrapper 중복 구현 금지. 사람이 CLI만으로 동일 재현 가능.

---

## 4. 승인 후 진행

AD-Q1~AD-Q6 응답 → (모호하면 후속 질문) → 계획 확정 → Part 2에서 위 5개 산출물 생성 → **REVIEW REQUIRED**에서 정지. Unit 분해·사람 배정은 이후 Units Generation.

---

## ⛔ REVIEW REQUIRED
위 **AD-Q1 ~ AD-Q6에 답**해 주시면 계획을 확정하고 설계 산출물(Part 2)을 생성합니다. 답변 전에는 산출물을 생성하지 않습니다.
