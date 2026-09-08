# Functional Design Plan — P0 경로 (U0 P0 필수 + U1)

**단계**: CONSTRUCTION / Functional Design (per-unit, 결합: U0 P0 필수 + U1)
**작성일**: 2026-09-08
**깊이**: 최소(minimal). 근거: 승인된 Application Design(계약 1~5 동결) + Units Generation(정정 반영) + stories.md(US-P0-1).
**대상 스토리**: US-P0-1 (설치 실패 → Skill 적용 → 실제 설치·검증 → reuse+1). 앵커: 9/8 17:30 P0 샘플 실행.

> **상태: 승인됨(2026-09-08, 정합화 3건 반영).** 아래 결정은 사용자 명시 답변(Q1~Q6)을 승인 근거로 확정. 상세 schema·라이브러리·CLI 문자열은 Code Plan에서 확정.
>
> **승인 시 정합화 3건(반영 완료)**: (1) **카운트 쓰기 주체 C3 단독** — 모든 실제 재사용 기록은 `C3.record_actual_reuse`, C2 descriptor dedup은 usage 병합·카운트 변경 없음. (2) **run_id = 실행(execution) 식별** — 입력이 아니라 한 번의 실제 실행을 식별. 같은 문제의 다른 환경 재사용은 다른 run_id(각각 +1), 재검증·재시도·재시작만 dedup. 사전 적재 Skill의 실제 재사용 성공은 실적 반영(DEMO_SEED 제외는 미리 만든 실적에만). (3) **허용 index 적용은 선택된 descriptor.procedure에 근거** — harness는 두 index 제공만, MATCH가 정답 환경을 강제 선택하지 않음. 실제 실패·설치·버전·import 검증 기준 유지.

---

## 대상 범위 (P0 최소 계약 = 1·3·4 + 로컬 저장·환경)
- **U0 P0 필수**: C1 SkillDescriptor(직렬화+digest), C2 SkillStore(로컬 저장·조회·dedup·CONFLICT), C3 UsageTracker(카운트+ReuseEvidence), envharness_p0(이중 mock index), cli.py run-p0 골격.
- **U1**: C5 SkillSearchMatcher(결정적 검색+applicability+근거, NO_MATCH), S1 ReuseService(시나리오 비의존 적용+효과 검증+실제 성공만 카운트).
- **제외(이 plan 아님)**: S2/S3/게시/Replay/조직 집계/UI(U2·U3 별도 Functional Design), P1 harness.

---

## 계획 체크리스트

### 도메인 모델 (business logic model / domain entities)
- [x] SkillDescriptor 도메인 정의: 불변 content {id, version, digest, origin, applicability, procedure} + 가변 usage {actual_reuse, DEMO_SEED 표식}
- [x] Applicability 구조 정의(적용 대상 판별 근거 필드)
- [x] SearchOutcome 구조 정의(MATCH{descriptor, 근거} | NO_MATCH{사유} | ERROR/TIMEOUT/NOT_INVOKED 구분)
- [x] ReuseEvidence 구조 정의(is_real_success, 검증 방법·결과, DEMO_SEED 여부, 타임스탬프, **안정적 실행 식별자**)
- [x] SkillStore 저장 모델(로컬 JSON, (id,version) 키, digest 보관, content/usage 경계)

### 비즈니스 규칙 (business rules)
- [x] **digest 규칙**: 불변 content에 대해서만 계산(digest 필드·가변 usage 제외). round-trip 후 동일(PBT-02).
- [x] **CONFLICT 판정**: 동일 (id,version) + 다른 digest = CONFLICT. 다른 version = CONFLICT 아님.
- [x] **카운트 규칙**: actual_reuse는 **실제 적용+효과 검증 성공** 시에만 +1. 실행 식별자로 중복 +1 방지. 시연/DEMO_SEED는 실적과 분리.
- [x] **검색 규칙**: 결정적. 유효 후보 다수는 안정 정렬·동점 규칙으로 선택+근거. NO_MATCH는 유효 후보 0건만.
- [x] **P0 재사용 규칙**: pip 설치 실패 관찰 → 매칭 Skill 절차 적용 → clean 환경에서 설치 성공 **검증** → 성공만 카운트.

### 데이터 흐름 / 통합점
- [x] run-p0 흐름: cli.run-p0 → envharness_p0(실패 index 재현) → C5.search → S1.apply → 검증 → C3.record_actual_reuse → 결과 출력
- [x] envharness_p0 이중 mock index: (a) 실패하는 index, (b) Skill 적용 후 성공하는 index — 결정적·오프라인

### 오류·엣지 처리
- [x] NO_MATCH 시 흐름(카운트 없음, 명확 메시지)
- [x] 적용했으나 검증 실패 시(카운트 없음, 실패로 기록)
- [x] CONFLICT 발견 시 저장 처리(거부/보류)

### 테스트 관점(PBT partial — 설계에 반영)
- [x] 직렬화 round-trip(PBT-02), digest 불변(PBT-03), dedup/CONFLICT invariant

---

## 확정 결정 (사용자 명시 답변 = 승인 근거, 2026-09-08)

**Q1. digest 정규화 방식 — 확정**
- 불변 content를 **canonical JSON**(키 정렬, 공백/인코딩 정규화)으로 직렬화 후 **SHA-256**. 해시 입력은 불변 content이며 **digest 필드 자체와 가변 usage는 제외**. 정규화 규칙을 명시해 직렬화·역직렬화 후 동일 digest 보장(PBT-02/03).

**Q2. C5 매칭 신호 — 확정(정정 포함)**
- 관찰된 실패 신호 ↔ applicability의 **결정적 매칭**. **유효 후보가 여럿이어도 NO_MATCH가 아님** — 안정적 정렬·동점(tie-break) 규칙으로 단일 후보 선택 + 근거 반환. **NO_MATCH는 유효 후보 0건일 때만.** 검색 오류·timeout·미호출은 기존 SearchOutcome 계약대로 별도 구분.

**Q3. S1 "실제 설치 성공" 검증 — 확정(정정 포함)**
- **깨끗한(clean) 실행 환경**에서 실제 pip 설치 **종료코드 성공 + 대상 배포 패키지 설치 여부·요구 버전 확인**. 합성 패키지는 **import까지** 확인. 기존/전역 Python 설치로 인한 오판 방지, **성공 index를 선택했다는 사실 자체는 성공 근거로 삼지 않음**.

**Q4. P0 저장소 형태 — 확정**
- **로컬 JSON 파일 기반**. content와 usage의 **소유·갱신 경계 유지**. P0 병렬 구현에 필요한 **최소 schema·저장/조회 계약을 이번 Functional Design에서 명확화**. 세부 코드 구성은 Code Plan.

**Q5. run-p0 시연 데이터 — 확정**
- 합성 descriptor + **이중 mock index**: 실패 index에는 대상 패키지 없음, 허용 index에는 무해한 패키지 존재 → **실제 pip 실행 결과로 실패·성공 관찰**. 사전 적재(preload)와 실제 재사용 실적 구분. 사내 데이터·secret 미사용(NFR-SEC).

**Q6. 추가 결정 — 없음(단, dedup 명시)**
- 추가 기능 결정 없음. **ReuseEvidence에 동일 성공을 식별하는 안정적 실행 식별자 포함** → 반복 검증·재시작 시 **중복 +1 방지**(NFR-RES-1 idempotent 카운트).

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/U0-P0/functional-design/` : business-logic-model.md, business-rules.md, domain-entities.md
- `aidlc-docs/construction/U1/functional-design/` : business-logic-model.md, business-rules.md, domain-entities.md
- (UI 없음 → frontend-components.md 생성 안 함)

> 승인 시 위 제안값(또는 사용자 수정값)으로 Functional Design 아티팩트를 생성하고, 이어서 **NFR Requirements(minimal) → Code Plan** 순으로 짧은 승인만 요청합니다. 코드 작성은 Code Plan 승인 + 공통 기준 SHA·작업 경로 확인 후.
