# Functional Design (minimal) — U2 P1·후보화·게시·Git 전송

**단계**: CONSTRUCTION / Functional Design (per-unit) — Unit **U2** (담당: B 한석훈)
**깊이**: 최소(minimal)
**작성일**: 2026-09-08 (기준 커밋 `7cbc856`)
**근거**: 승인된 `requirements.md`, `stories.md`, `components.md`, `component-methods.md`, `services.md`, `unit-of-work*.md` + 사용자 결정 3종(2026-09-08T08:43:25Z)
**소유 파일**: `experience_service.py`(S2), `publish_pipeline.py`(S3), `replay.py`(C6), `envharness_p1.py`(C7-P1), `gitsync.py`(C4) + 대응 U2 테스트

> 이 문서는 U2의 **비즈니스 규칙·상태머신·계약 시그니처·검증 알고리즘**을 확정한다. 코드 파일·실행 명령·작업 순서는 후속 **Code Plan**에서 확정한다. HOW 중 UI/집계(U3)·재사용 검증 카운트(usage.py, CJ)는 범위 밖(호출만).

---

## 0. 확정된 진행 파라미터

> **개정 이력**: 초안 D-1(U2 자체 lifecycle.json)은 **CJ FD 검토(2026-09-08)로 철회**되고 아래로 대체됨. D-2·D-3 유지. CJ 결정 5(team-skill-store 초기화=B) 추가.

- **D-1 (S3 lifecycle 영속) — CJ 검토 반영, 개정**: 이전 "U2 자체 `lifecycle.json` 영속" 결정을 **철회**한다. lifecycle **저장 책임은 CJ가 `SkillStore` 쪽으로 정합화**한다(services.md의 "SkillStore lifecycle-state 저장 계약" 유지). 단, **상태 판단·게이트 판정·읽기전용 상태 조회 책임은 U2(S3)가 그대로 유지**한다(단일 소유). → **CJ 계약 대기 항목**: `store`의 lifecycle-state 저장/조회 인터페이스가 확정되기 전까지 영속 연동은 **`NOT_RUN`**, S3는 계약 확정 시 저장 호출만 연결한다(자체 저장으로 우회하지 않음).
- **D-2 (Git 전송 구조)**: `gitsync.py`는 **team-skill-store 전용 로컬 미러 디렉터리**에서만 pull/push 한다. 현재 dev worktree·작업 브랜치(`work/u2-p1-git`)를 절대 오염시키지 않는다.
- **D-3 (push 불가 시)**: 실제 원격 push 인증이 불가하면 로컬 **SHAREABLE(LOCALLY_APPROVED)** 상태를 보존하고 **PUBLISH_PENDING**으로 둔다. 원격 push 검증은 **NOT_RUN**으로 정직 기록하며 **PUBLISHED로 보고하지 않는다**(FR-P1-7 / CON honesty).
- **D-4 (team-skill-store 초기화) — CJ 결정 5**: **team-skill-store branch 최초 초기화는 B(U2) 담당**이다. `main`과 **분리된 작업 경로**(D-2 전용 로컬 미러)에서 **공유 데이터 전용**으로 준비한다(합성·비민감 descriptor + 이벤트만; DB 파일·원본·secret 제외, FR-SYNC-5/NFR-SEC-1).

---

## 1. C7-P1 — EnvHarness (`envharness_p1.py`) : 합성 환경 준비만

### 합성 실패 모델 (핵심 설계 결정)
- 보호 대상은 **합성 XLSX**(OOXML = zip 컨테이너). "직접 parser 접근이 **실제로** 실패"하되 "허용 read-only 대안으로는 내용 획득 가능"을 **DRM·비밀번호·강제 raise 없이** 성립시킨다.
- **직접 parser 실패의 성질**: 환경 사실로서 관찰된 실패여야 한다. EnvHarness는 실패를 `raise`로 연출하지 않고, **정답 대안 절차 목록도 공급하지 않는다**(C7 경계, FR-P1-1/4).
- **합성 모델**(Code Plan에서 구현 확정, FD에서 방향 고정): 대상 XLSX를 "직접 parser"(요청 시나리오의 naive 접근 — 예: 워크북을 단순 텍스트/비-zip 방식으로 읽으려는 시도)로 열면 **실제 실행이 실패**를 반환한다. 반면 파일은 정상 OOXML zip이므로, **허용된 read-only 대안**(zip으로 열어 `xl/worksheets/*.xml`을 읽는 절차 등)으로는 내용 획득이 가능하다. 어떤 대안이 정답인지는 EnvHarness가 판단·공급하지 않으며 **Agent가 탐색·선택·실행**한다.

### 계약 시그니처
```
setup_protected_xlsx_env(path) -> XlsxEnv
    # 보호 속성을 가진 합성 XLSX + Windows read-only 표면을 "배치"만 한다.
    # XlsxEnv = {xlsx_path, readonly_surface, present_facts}  ← 무엇이 존재/허용되는지의 사실만
teardown() -> None

# C7↔Agent 관찰 계약 (강제 raise 아님 — 실제 parser 실행 관찰)
attempt_direct_parse(path) -> DirectParseObservation
    # DirectParseObservation = {ran: bool, ok: bool, error: str|None, evidence: dict}
    # 보호 합성 XLSX에서 실제 실행 결과가 ok=False(관찰된 실패, FR-P1-1).
```
- **경계 규칙**: `attempt_direct_parse`는 실제 parser를 실행하고 결과만 관찰한다. 대안 탐색·코드 작성·실행은 EnvHarness 책임 아님(Agent 책임). 실제 회사 데이터·DRM 없음(CON-1), 승인 대상만 read-only(NFR-SEC-2).
- **의존성 위험(Code Plan에서 처리)**: 직접 parser로 쓸 라이브러리는 Windows-native·requirements 반영 여부 확인. 합성 데이터는 3개 완료월 총생산량을 담되 원본 업무 데이터·secret 미포함.

---

## 2. S2 — ExperienceService (`experience_service.py`) : P1 업무 완료 + 후보화

### 흐름 (services.md run_p1 정합)
```
run_p1(xlsx):
  1. obs = EnvHarness.attempt_direct_parse(xlsx)         # 실제 실행 관찰 → 실패 관찰 (FR-P1-1)
  2. outcome = SkillSearchMatcher.search(problem)        # 실제 검색·범위/질의/결과 기록 (FR-P1-2)
       - status in {ERROR, TIMEOUT, NOT_INVOKED} → 별도 오류 상태(≠ NO_MATCH)  (FR-P1-2)
       - applicable 파일접근 후보 존재:
            r = S1.apply_and_verify(match, problem)       # ★ 파일접근 유형 재사용(pip 흐름 아님, A 계약 호출만)
            if r.is_real_success: usage.record_actual_reuse(build_evidence(..., run_id, ...))  # C3 경유
            content = 재사용으로 획득한 파일 내용;  reused = True
       - else NO_MATCH → 3~4 Agent 탐색
  3. facts = ask_environment_facts(user)                 # 대화형 (FR-P1-3)
  4. (NO_MATCH) Agent가 허용 read-only 대안을 탐색·선택·코드작성·실행 → content 획득 (FR-P1-4)
  5. result = compute_ols_forecast(content);  wv = verify_work_result(result, facts)   # FR-P1-5
  6. 후보 분기(중복 방지):
       - reused & 새 절차 없음  → candidate 생성 안 함
       - NO_MATCH & 새 절차 발견 → candidate = build_candidate_procedure(alt)  # 환경 절차만
  7. return WorkReport{reused, work_verification: wv} (+candidate 있으면 PROPOSED로 S3 이관)
```

### FR-P1-5 업무 검증 규칙 (확정)
- **기준월**: "다음 달" = **데이터에 포함된 마지막 완료 월 + 1**(실행 시점 아님).
- **예측**: 이전 3개 완료 월의 **월별 총생산량 3점**을 시간순 `x=1,2,3`으로 두고 **단순 OLS 선형 추세** 적합 → `x=4`를 예상값.
  - OLS 폐형식: 기울기 `b = Σ(xᵢ-x̄)(yᵢ-ȳ) / Σ(xᵢ-x̄)²`, 절편 `a = ȳ - b·x̄`, 예측 `ŷ = a + 4b`.
- **음수 clamp**: 예상값 < 0 → **0**.
- **표시**: 결과에 **실제 3개월 + 예상 1개월 구분**, 예측 대상 월·단위·예상값 명확 표시.
- **경계**: 이 계산은 **업무 결과 검증용**. 새 Skill 후보에는 **계산식·생산량 값·차트 로직 미포함**(환경 접근 절차만, FR-P1-6, NFR-SEC-1).

### 후보화 규칙 (FR-P1-6 / US-P1-3)
- candidate descriptor는 **환경 접근 절차만** 담는다(계산식·생산량·차트·업무 원문·인증정보 제외).
- C1(`make_descriptor`)로 생성 → digest는 불변 content에 대해서만. 기존 등록 절차와 **digest dedup** → 동일하면 새 후보 만들지 않음.

### 책임 구분
- `verify_work_result`(S2) = **P1 업무 결과 검증**(FR-P1-5 충족). S1.verify(파일접근 성공 여부)와 구분. 재사용 성공해도 업무 결과까지 완료·검증.

### 검색·재사용 계약 의존 — CJ 검토 반영(C-c, 개정)
- **NO_MATCH는 실제 구현된 검색이 수행된 뒤에만 판정**한다. **미구현 검색을 NO_MATCH로 간주하지 않는다**(CJ 결정 3).
- `SkillSearchMatcher.search`(A)는 **P1 검색 입력 규격뿐 아니라 파일접근 Skill의 적용·검증 계약(S1 파일접근 유형)까지 A와 함께 확정**된다. → **A 계약 대기**.
- 초안의 "U2가 store를 직접 조회해 NO_MATCH로 진행" **우회안은 제거**한다. A 계약 확정 전까지 검색·파일접근 재사용 분기는 **`NOT_RUN`**으로 기록하고, S2는 계약이 서면 그 계약으로 연결한다.

---

## 3. S3 — PublishPipeline (`publish_pipeline.py`) : 검토·독립 Replay·게시 게이트

### 상태머신 (로컬 확정 ≠ 원격 게시 완료)
```
PROPOSED → UNDER_REVIEW → (APPROVED | REJECTED)
        → REPLAYED(PASS | FAIL | NOT_RUN)
        → (LOCALLY_APPROVED[=SHAREABLE] | BLOCKED)
        → (PUBLISHED | PUBLISH_PENDING)
```
- **LOCALLY_APPROVED(SHAREABLE)**: 게이트 충족 + 로컬 저장 완료. 아직 원격 게시 아님.
- **PUBLISHED**: 원격 push **성공 확인**까지 완료.
- **PUBLISH_PENDING**: 게이트 충족했으나 원격 push 실패/불가(D-3) → 로컬 상태·재시도 근거 보존, PUBLISHED 미보고.
- **BLOCKED**: 게이트 미충족(거절 / FAIL / NOT_RUN / 미완료).

### 게이트 판정 (FR-P1-7 / US-P1-4 AC-2~4)
```
review(candidate, decision):   # PER-2 — approval/rejection을 EXACT candidate {id,version,digest}에 바인딩
replay(candidate):             r = ReplayVerifier.replay(candidate, env)   # C6, 실제 결과
publish(candidate):
   gate 모두 충족해야 진행:
     (a) approved_ref{id,ver,digest} == replayed_ref == candidate 현재 ref (digest 동일성)
     (b) 해당 exact candidate에 사람 승인 존재
     (c) ReplayResult.verdict == PASS
     (d) verdict in {FAIL, NOT_RUN} / 미완료 → BLOCKED
     (e) 승인 후 내용/version/digest 변경 → 기존 승인 무승계, 재검토·재Replay 대상
   if not gate: state=BLOCKED; return
   store.put(candidate)                       # C2, 무결성/dedup. 성공 시 state=LOCALLY_APPROVED(=SHAREABLE)
   res = GitSyncAdapter.push_descriptors(export SHAREABLE)   # D-2 미러, D-3 처리
   state = PUBLISHED if res.ok else PUBLISH_PENDING           # ok=False면 PUBLISHED 미보고
```

### 읽기전용 상태 조회 계약 (계약 #7 — U2 소유, U3가 소비)
```
query_lifecycle_state(candidate_ref{id,version,digest}) -> LifecycleState   # 읽기 전용
list_lifecycle_states(filter) -> list[LifecycleState]                        # 읽기 전용
# LifecycleState = {ref, state, local_review_evidence, remote_publish_evidence}
```
- U3(C10)는 이 계약으로만 상태를 조회한다. **상태 추정·게이트 재구현 금지**(AD-Q4).
- **원격 게시본 구분**: import로 받은 게시본은 `remote_publish_evidence`(원격 근거)와 `local_review_evidence`(수신 환경 검토)를 **분리**한다. 로컬 검토 없으면 "원격 게시(타 환경 근거)"로만 표시, **수신 환경의 승인·Replay 기록을 만들지 않는다**.
- **영속: D-1(개정)** — lifecycle 저장은 **CJ의 `SkillStore` lifecycle-state 계약**에 위임(대기). **상태 전이 판단·게이트·읽기전용 조회는 S3(U2) 단독 유지**. store lifecycle 저장/조회 계약 확정 전까지 영속 연동은 **`NOT_RUN`**이며, S3는 자체 파일 저장으로 우회하지 않고 계약 확정 시 호출만 연결한다.

---

## 4. C6 — ReplayVerifier (`replay.py`) : 독립 Replay

```
replay(candidate: Descriptor, env: EnvContext) -> ReplayResult
# ReplayResult = {verdict: PASS|FAIL|NOT_RUN, candidate_ref:{id,version,digest}, evidence: dict}
```
- **독립 실행**: candidate의 **환경 접근 절차**를 EnvHarness가 준비한 P1 합성 환경에 **독립적으로 재적용**해 실제 효과(파일 내용 획득 = ACCESS_EFFECT)를 확인 → verdict 산출.
- verdict는 화면 문구가 아닌 **실제 효과** 기반(NFR-TEST-2). `candidate_ref.digest`는 게이트 동일성 확인에 사용.
- 계약 5(ReplayResult + 게이트 입력 규격)는 U0 프리즈가 없으므로 **U2가 `replay.py`에서 정의**하고 S3가 소비.

---

## 5. C4 — GitSyncAdapter (`gitsync.py`) : 전송 전담 (B 단일 수정자)

### 대상·구조 (D-2, D-4)
- 대상: 동일 저장소 `THEGREATCJPark/ddthon`의 **`team-skill-store` branch**. **전용 로컬 미러 dir**에서만 조작.
- **최초 초기화(D-4)**: team-skill-store branch 준비는 **B 담당**. `main`과 분리된 전용 경로에서 공유 데이터 전용으로 초기화.
- 전송 내용: **공유 가능한 descriptor + 비민감 재사용 이벤트 레코드**만. **로컬 DB 파일(store.json/usage.json 등) 자체는 전송하지 않는다**(FR-SYNC-5).
- bundle은 미러 작업트리에 **파일로 직렬화**(descriptor JSON / 이벤트 JSON) 후 commit·push.

### 계약 시그니처
```
pull() -> SyncResult
    # 원격 branch → 로컬. descriptor는 store.import_bundle, 이벤트는 usage.import_shared_usage 경유(검증·dedup 위임).
push_descriptors(bundle) -> SyncResult
    # 로컬 → 원격. store.export_bundle(SHAREABLE) 결과만. S3.publish가 사용.
push_shared_usage(usage_bundle) -> SyncResult
    # 로컬 → 원격. usage.export_shared_usage(VERIFIED_REUSE) 결과만. ★ 게시와 독립 경로.
last_sync() -> SyncMeta        # {synced_at, branch_revision, queryable_range} (FR-ORG-5)
status() -> SyncStatus
# SyncResult = {ok, retryable, error}
```
- **경계**: 무결성·CONFLICT·dedup·저장은 **store**(CJ), 공유 이벤트 규격·검증·event_id dedup·저장은 **usage.py**(CJ)에 위임. gitsync는 **전송만**. 승인·게시 lifecycle 미구현(S3 책임). 원격 상태 문자열만으로 로컬 승인/Replay/실적 생성 안 함(AD-Q4).
- **D-3**: `push_*`가 `ok=False`면 로컬 상태 미변경, `retryable`/`error` 보존. S3는 PUBLISH_PENDING 유지. 실제 원격 push 인증 불가 시 push 검증 **NOT_RUN**.
- **게시 vs 이벤트 공유 독립**: `push_descriptors`(SHAREABLE descriptor)와 `push_shared_usage`(VERIFIED_REUSE 이벤트)는 별개 경로. 새 Skill을 게시하지 않아도 실적 이벤트 공유 가능.
- **계약 대기·병행 개발 규칙(CJ 검토 반영, C-b/C-d)**: **U2는 자체 저장·무결성·CONFLICT 처리로 우회하지 않는다**(CJ 결정 2). `store.export_bundle/import_bundle`(C-b)와 `usage.export/import_shared_usage`(C-d)는 **CJ가 우선 제공**한다. gitsync의 **전송 로직은 확정 계약에 맞춘 테스트 대역(stub)으로 병행 개발**하되, **실제 import/pull 검증과는 명확히 구분**하고 미실행분은 **`NOT_RUN`**으로 기록한다. 이벤트 규격·검증·dedup·저장=CJ, **Git 전송 경계만 B 유지**(CJ 결정 4).

---

## 6. CJ/A 조율 계약 대기 (CJ 검토 반영 — 우회안 제거)

> **CJ FD 검토(2026-09-08) 반영**: 초안의 U2 자체 우회안(자체 lifecycle 저장 / 자체 bundle 직렬화·CONFLICT / 자체 store 조회 NO_MATCH)을 **모두 제거**한다. 해당 계약은 소유자(CJ/A)가 제공하며, U2는 계약에 맞춰 **호출 연결 + 테스트 대역(stub) 병행 개발**만 한다. 미실행 실검증은 **`NOT_RUN`**.

| # | 계약 대기 | 소유 | U2 처리(우회 없음) | NOT_RUN 항목 |
|---|---|---|---|---|
| C-a | S3 lifecycle **저장** 정합화 | **CJ(SkillStore)** | 상태 판단·게이트·읽기전용 조회는 **S3(U2) 유지**. 저장은 CJ 계약에 **호출만 연결**(자체 파일 저장 금지) | lifecycle 영속 연동 |
| C-b | `store.export_bundle(SHAREABLE)` / `import_bundle` | **CJ(store.py) — 우선 제공** | 자체 저장·무결성·CONFLICT **우회 금지**. gitsync 전송은 **계약 stub로 병행 개발**, 실제 import/pull 검증과 구분 | pull import·CONFLICT 실검증 |
| C-c | `match.search` P1 입력 **+ 파일접근 Skill 적용·검증 계약** | **A(조율 중)** | **미구현 검색을 NO_MATCH로 간주 금지**. store 직접 조회 우회 **제거**. A 계약 대기 | 검색·파일접근 재사용 분기 |
| C-d | 공유 이벤트 규격·검증·dedup·**저장** | **CJ(usage.py)** | **Git 전송 경계만 B 유지**. 전송 stub 병행 가능 | 이벤트 공유 왕복 실검증 |

**이미 확보**: 계약 1(descriptor digest/serialize) ✅, 계약 3 카운트(record_actual_reuse/build_evidence/new_execution_id) ✅. 계약 5(ReplayResult)는 U2 정의.
**병행 개발 가능(계약 확정 전, stub 기준)**: gitsync 전송 골격(push_descriptors/push_shared_usage/pull/last_sync 인터페이스), S3 상태머신·게이트·읽기전용 조회 계약(#7) 정의, C6 Replay, C7-P1 환경 harness, S2 OLS·후보화(계산·표시 로직).

---

## 7. 확장 규칙 준수 요약 (이 단계)

| 확장 | 상태 | 이 단계 적용 |
|---|---|---|
| Security Baseline | Disabled(전체) | NFR-SEC-1(secret·원본 미포함)·SEC-2(read-only)·SEC-3(digest 검증)·SEC-4(자동 실행 금지) 반영. candidate·bundle에 계산결과·원본 배제 |
| Resiliency Baseline | Disabled(전체) | NFR-RES-1(dedup)·RES-2(CONFLICT는 store 위임)·RES-3(sync 실패 로컬 보존)·RES-4(재시작 보존) 반영 |
| Property-Based Testing | Enabled(Partial) | 대상 식별: OLS 계산 불변식(단조·clamp), candidate 후보 digest 불변, lifecycle 게이트 불변식. 구체 PBT는 Code Plan에서 |

---

## 8. 추적성 (U2 스토리 → 컴포넌트/계약)

| Story | 컴포넌트 | 핵심 FR |
|---|---|---|
| US-P1-1 (직접 실패 관찰 + 검색 NO_MATCH 구분) | C7-P1, S2, C5(계약, 우회 C-c) | FR-P1-1/2, FR-MATCH, NFR-SEC-2 |
| US-P1-2 (환경 사실·대안 탐색 + OLS 완료·검증) | S2, C7-P1, S1(호출) | FR-P1-3/4/5, NFR-SEC-2 |
| US-P1-3 (새 절차만 후보화) | S2, C1(호출) | FR-P1-6, FR-SKILL, NFR-SEC-1/3, NFR-RES-1 |
| US-P1-4 (검토·독립 Replay·게시, PUBLISHED=push 성공) | S3, C6, C4, C2(호출, 우회 C-b) | FR-P1-7, FR-SYNC-1~5, NFR-RES-2/3, NFR-SEC-4 |

---

## 9. 미해결·NOT_RUN 예정 항목 (정직 기록 — CJ 검토 반영)
- 실제 원격 push 인증 불가 시 PUBLISHED 도달은 **NOT_RUN**(D-3).
- CJ `store.export_bundle`/`import_bundle`(C-b) 확정 전 **pull import·CONFLICT 실검증은 NOT_RUN**(자체 저장·CONFLICT 우회 금지).
- CJ `store` lifecycle-state 저장/조회 계약(C-a) 확정 전 **lifecycle 영속 연동은 NOT_RUN**(자체 파일 저장 금지, 판단·게이트는 S3 유지).
- CJ `usage.export/import_shared_usage`(C-d) 확정 전 **이벤트 공유 왕복 실검증은 NOT_RUN**(Git 전송 경계만 B).
- A `match.search` P1 입력 + 파일접근 적용·검증 계약(C-c) 확정 전 **검색·파일접근 재사용 분기는 NOT_RUN**(미구현 검색을 NO_MATCH로 간주 금지).
