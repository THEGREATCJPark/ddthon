# Component Methods — Agent SkillLoop

**단계**: INCEPTION / Application Design — Part 2
**작성일**: 2026-09-08
**근거**: `components.md`, `application-design-plan.md`(AD-Q1~Q6)

> **메서드 시그니처와 입출력의 고수준 정의**입니다. **상세 비즈니스 규칙·검증 로직·알고리즘은 Functional Design(per-unit, CONSTRUCTION)** 에서 확정합니다(예: OLS 계산식, 매칭 스코어, CONFLICT 세부 규칙). 시그니처는 **제안**이며 확정 아닙니다. 타입은 개념적 표기(Python 힌트 유사)입니다.
> **공통 규약(AD-Q5)**: 각 메서드는 입력·출력·오류·상태 변경 책임이 명확해야 하며, **소유하지 않은 상태를 직접 수정하지 않는다.**

---

## C1 — SkillDescriptor
```
class SkillDescriptor:
    # 직렬화 round-trip (PBT-02 대상)
    to_dict() -> dict                      # content + usage 를 구조화 표현
    from_dict(data: dict) -> SkillDescriptor

    content_view() -> ContentIdentity      # 불변: id, version, digest, origin, applicability, procedure
    usage_view() -> UsageStats             # 가변: actual_reuse, demo_seed (읽기)

    compute_digest() -> str                # 불변 content에 대해서만 (usage 제외) — FR-SKILL-4
    verify_digest() -> bool                # 저장된 digest == compute_digest()
```
- **불변식(PBT)**: `from_dict(to_dict(x)) == x`(round-trip), `compute_digest`는 usage 변경에 불변.

## C2 — SkillStore
```
class SkillStore:
    save(desc: SkillDescriptor) -> SaveResult      # dedup 적용, 소유 상태 유일 writer
    get(id: str, version: str) -> SkillDescriptor | None
    list(filter: dict | None) -> list[SkillDescriptor]

    detect_conflict(incoming: SkillDescriptor) -> ConflictReport
        # CONFLICT = 동일 (id, version) & 상이 digest 만 (FR-SYNC-3/NFR-RES-2)
        # 다른 version 은 conflict 아님

    export_bundle(scope=SHAREABLE) -> Bundle
        # GitSyncAdapter 가 사용하는 export 계약.
        # ★ SHAREABLE = 정확한 후보에 대한 사람 승인 + 독립 Replay PASS + digest 동일성 충족.
        #   "원격 전송 완료(PUBLISHED)"가 아니라 게이트 충족 여부로 판정 → 최초 게시 순환 조건 없음.
        #   미승인/미Replay/미충족 후보는 export 안 함.
    import_bundle(bundle: Bundle) -> ImportResult
        # 무결성·dedup·CONFLICT 판정 후 content 만 반영, CONFLICT 는 자동 overwrite/파괴적 병합 금지
        # ★ 원격 상태 문자열만으로 로컬 승인·Replay 기록을 생성하지 않는다(AD-Q4).
        #   로컬의 approval/replay 상태는 로컬 근거로만 만들어진다.
```
- `SaveResult`/`ImportResult`: `{applied, skipped_dedup, conflicts: list, errors: list}`.

## C3 — UsageTracker
```
class UsageTracker:
    record_actual_reuse(id: str, version: str, evidence: ReuseEvidence) -> UsageStats
        # 검증된 실제 성공(evidence)일 때만 +1 (FR-USAGE-1)
        # 동일 성공 재기록·retry·sync·restart 는 중복 집계 안 함 (FR-USAGE-2, AD-Q5)
    get_usage(id: str, version: str) -> UsageStats     # actual_reuse 와 demo_seed 구분 포함
    is_demo_seed(...) -> bool                          # FR-USAGE-3 구분 표시

    # --- 범위 변경: 공유 재사용 이력 (FR-USAGE-4, FR-ORG-3) ---
    export_shared_usage(scope=VERIFIED_REUSE) -> SharedUsageBundle
        # ★ 재사용 이벤트 공유 자격 = VERIFIED_REUSE ≠ Skill 게시 자격(SHAREABLE).
        #   VERIFIED_REUSE = (a) 정확한 Skill 참조 {id,version,digest} 가 로컬에 존재
        #                  + (b) 실제 적용·검증 성공 근거(is_real_success, S1.verify evidence)
        #                  + (c) DEMO_SEED 아님.
        #   ★ 해당 Skill 의 로컬 승인·독립 Replay(=게시 게이트)를 요구하지 않는다.
        #     → 남의 게시 Skill 을 import 해 실제 재사용만 한 환경도 자기 실적을 공유할 수 있다.
        # 비민감·합성 재사용 이벤트 레코드만 (event_id, skill_ref{id,version,digest}, reuser_alias, evidence_ref)
        # 원본 업무 데이터·secret 미포함 (NFR-SEC-1).
    import_shared_usage(bundle: SharedUsageBundle) -> UsageImportResult
        # ★ C3 가 검증·중복 제거 담당:
        #   (1) 각 이벤트가 정확한 Skill 참조 + 실제 성공 근거를 가졌는지 검증(미충족 이벤트는 reject),
        #   (2) event_id 기준 dedup → 재동기화/재시작/왕복 시 동일 이벤트 중복 +1 금지 (FR-USAGE-2/4).
        # → A게시 → B import → B 실제 적용·검증 성공 → B가 이벤트 공유 → A가 import 시 조직 실적에 "한 번만" 반영.
        # {applied, skipped_dedup, rejected_unverified, errors}
```
- `ReuseEvidence`: 실제 적용·검증 성공을 식별하는 근거(예: 검증 통과 토큰/실행 id). **digest 를 바꾸지 않는다.**
- **자격 구분(명확화)**: **신규 Skill 게시 게이트(SHAREABLE=사람 승인+독립 Replay PASS+digest 동일성)는 그대로 유지**된다(C2.export_bundle). 재사용 이벤트 공유(VERIFIED_REUSE)는 이와 **별개**이며, 이벤트를 공유하기 위해 그 Skill 을 **다시 후보화·승인·Replay 하도록 요구하지 않는다.** 이벤트는 정확한 Skill 참조 + 실제 성공 근거에만 연결된다.
- **소유 경계**: 공유 usage 이벤트의 저장·검증·dedup은 C3만 쓰기. C4는 전송만, C10은 읽기만.

## C4 — GitSyncAdapter (대상: `team-skill-store` branch — 범위 변경)
```
class GitSyncAdapter:
    # target = 동일 저장소 team-skill-store branch (별도 저장소도 동일 의미로 허용). 실제 경로는 미결정.
    pull() -> SyncResult                   # 원격 branch → 로컬 (store.import_bundle + usage.import_shared_usage 경유)
    push_descriptors(bundle: Bundle) -> SyncResult
        # 로컬 → 원격 branch. descriptor(store.export_bundle(SHAREABLE))만. S3.publish 가 사용.
    push_shared_usage(usage: SharedUsageBundle) -> SyncResult
        # 로컬 → 원격 branch. 비민감 재사용 이벤트(usage.export_shared_usage(VERIFIED_REUSE))만.
        # ★ Skill 게시와 독립적인 sync 경로 — 새 Skill 을 게시하지 않아도 실적 이벤트를 공유할 수 있다.
        # ★ 두 push 모두 로컬 DB 파일 자체는 전송하지 않는다 (FR-SYNC-5).
    last_sync() -> SyncMeta                # {synced_at, branch_revision, queryable_range} (FR-ORG-5)
    status() -> SyncStatus                 # 재시도 가능 여부 등
```
- `SyncResult{ok, retryable, error}`. **push 성공(ok=True) 시에만** 원격 게시 완료로 간주(PublishPipeline가 PUBLISHED 로 전이). **ok=False 이면 로컬 상태 미변경(NFR-RES-3) + 재시도 근거 보존**, PublishPipeline는 `PUBLISH_PENDING` 유지(PUBLISHED 아님).
- 무결성/CONFLICT 판정은 **store 에 위임**, 공유 usage 이벤트 dedup은 **UsageTracker 에 위임**. **승인/게시 lifecycle 미구현**(PublishPipeline 책임). 원격 상태 문자열만으로 로컬 승인/Replay/실적 생성 안 함(AD-Q4).

## C5 — SkillSearchMatcher
```
class SkillSearchMatcher:
    search(query: SearchQuery) -> SearchOutcome
        # SearchOutcome = {status: MATCHED|NO_MATCH|ERROR|NOT_INVOKED|TIMEOUT,
        #                  candidates: list[Match], scope, executed_query}
    check_applicability(candidate: SkillDescriptor, problem: ProblemContext) -> Applicability
        # {applicable: bool, matched_keywords, matched_conditions}  (근거 제시 FR-MATCH-3)
```
- **경계**: `NO_MATCH` 는 **검색이 실제 수행되고 적용 가능 후보가 없을 때만**. 미호출/오류/timeout 은 별도 status(FR-P1-2).

## C6 — ReplayVerifier
```
class ReplayVerifier:
    replay(candidate: SkillDescriptor, env: EnvContext) -> ReplayResult
        # ReplayResult = {verdict: PASS|FAIL|NOT_RUN,
        #                 candidate_ref: {id, version, digest}, evidence}
```
- verdict 는 **실제 효과** 기반(NFR-TEST-2). `candidate_ref.digest` 는 게시 게이트의 동일성 확인에 사용.

## C7 — EnvHarness (합성 환경 **준비만**; 정답 절차 공급 금지)
```
class EnvHarness:
    # P0
    setup_pip_env() -> PipEnv               # 공개 index(대상 없음)+허용 사내 index(무해 wheel)
    # P1 — 통제된 합성 환경을 "구성"할 뿐, 직접 실패를 강제 raise 하지 않는다
    setup_protected_xlsx_env(path) -> XlsxEnv
        # 보호 속성을 가진 합성 XLSX + Windows read-only 표면을 배치.
        # 어떤 접근이 실패/성공하는지는 "환경 사실"이며, 실제 parser 실행이 그 사실을 드러낸다.
    teardown() -> None
```
- **경계(변경)**: EnvHarness는 **합성 환경 준비**만 담당한다. **직접 접근 실패를 강제로 발생시키는 구현(force-raise)이나, 정답 대안 절차 목록을 공급해 Agent가 선택만 하게 하는 구조를 두지 않는다.** 실패/성공은 환경 사실이며 **실제 parser 실행 결과를 관찰**해 드러난다(아래 관찰 계약 참조).
- 실제 회사 데이터·DRM 없음(CON-1), 승인 대상만 read-only(NFR-SEC-2).

### C7↔Agent 관찰/탐색 경계 (계약)
- `attempt_direct_parse(path) -> DirectParseObservation` — **실제 parser를 실행하고 그 결과를 관찰**하는 계약. 보호된 합성 XLSX에서는 실제 실행이 실패를 반환한다(강제 raise가 아니라 관찰된 실패, FR-P1-1). `{ran: bool, ok: bool, error: str|None, evidence}`.
- **허용 대안의 탐색·선택·코드 작성·실행은 EnvHarness가 아니라 실제 업무 Agent의 책임**이다(FR-P1-4). EnvHarness는 무엇이 환경에 존재/허용되는지의 **사실만** 제공하고, 어떤 절차가 정답인지 판단·구성하지 않는다.

## C8 — CLI (명령 → 서비스 위임)
```
# 명령 동사 최종 집합은 Functional Design 확정. 각 명령은 S1~S3 서비스 호출.
skillloop search   <query>              -> S1/S2 검색 표시
skillloop apply    <skill> <problem>    -> S1 ReuseService (적용+검증+카운트)
skillloop run-p0   <requirements.txt>   -> S1 P0 종단
skillloop run-p1   <xlsx>               -> S2 P1 업무 종단(대안 탐색·OLS·후보화)
skillloop propose  <candidate>          -> S2 후보 등록
skillloop review   <candidate> --approve|--reject   -> S3 사람 검토
skillloop replay   <candidate>          -> S3→C6 독립 Replay
skillloop publish  <candidate>          -> S3 게시 게이트(모든 조건 충족 시만)
skillloop sync     --pull|--push        -> C4. push=이미 SHAREABLE 인 descriptor + VERIFIED_REUSE 이벤트(게시와 독립), pull=둘 다 import(C3가 검증·dedup)
```
- **경계**: 판단·카운트·게이트를 CLI 에 재구현하지 않고 서비스 위임. 게시 게이트 우회 금지.

## C9 — AgentSkillWrapper
```
handle_natural_language(request: str) -> CliInvocation   # 의도 → CLI 명령 매핑만
```
- **제품 로직(검증·카운트·게시 판단·매칭 규칙)** 중복 없음. 실행은 명시적 CLI 호출(원격 자동 실행 금지 NFR-SEC-4).
- **경계(명확화)**: "얇은 wrapper"는 **제품 로직 중복 금지**를 뜻하며, **실제 업무 Agent의 탐색 역할을 제거하지 않는다.** P1에서 **환경 관찰·허용 대안 선택·코드 작성·실행**은 Agent가 수행하고, 그 실행을 CLI 명령(`run-p1` 등)에 **연결**한다. 즉 Agent = 탐색·실행 주체, CLI/서비스 = 재현 가능한 제품 로직·검증·상태 관리, Wrapper = 자연어→CLI 연결.

## C10 — OrgAggregator (집계 read-model — 읽기 전용 파생, 범위 변경)
```
class OrgAggregator:
    build_snapshot() -> OrgSnapshot        # 두 표면 공용 단일 스냅샷 (FR-UI-3)
    # OrgSnapshot = {
    #   summary: {published_skills, verified_reuses, reuser_aliases, contributor_aliases},  # FR-ORG-1
    #   skills: [{id, version, digest, applicability, evidence, reuse_count, ...}],          # dedup·버전 구분
    #   people: [{alias, role: author|reviewer|reuser, contributions, cross_reuse}],         # FR-ORG-2
    #   states: [{ref, lifecycle_state,                    # ★ S3.query 로 받은 값 그대로 (추정 아님)
    #             local_review_evidence, remote_publish_evidence}],                          # FR-ORG-4
    #   ranking: [...],                        # 실제 검증 재사용 기준 (FR-ORG)
    #   activity: [...],                       # 최근 활동
    #   last_sync: {synced_at, branch_revision, queryable_range},                            # FR-ORG-5
    #   accounting: {actual vs demo_seed 구분}                                               # FR-USAGE-3
    # }
```
- **읽기 전용 · 상태는 S3 조회 계약으로만**: C2(공유 게시 content)·C3(get_usage/공유 import 결과)·C4.last_sync 를 읽고, **후보/검토/Replay/게시 상태는 S3 의 읽기전용 계약(`S3.list_lifecycle_states`/`query_lifecycle_state`)으로만 조회**한다. **C10 은 상태를 추정하거나 게시 판단(게이트)을 재구현하지 않는다.** 소유 상태 미수정, usage 쓰기 없음. secret·원본 데이터 미포함(NFR-SEC-1).
- **원격 게시본 구분(AD-Q4)**: import 로 받은 게시본은 `remote_publish_evidence`(원격 게시 근거)와 `local_review_evidence`(수신 환경 검토 상태)를 **분리 표시**한다. 로컬 검토 기록이 없으면 "원격 게시(다른 환경 근거)"로만 표시하며 **수신 환경의 승인·Replay 기록을 만들어내지 않는다.**
- **identity 기준**: 작성자=`origin`, 재사용자=alias(정의는 Functional Design). 랭킹 동점 규칙·집계 schema 상세도 Functional Design.

## C11 — StatuslineRenderer (범위 변경)
```
render_statusline(snapshot: OrgSnapshot) -> str   # 조직 Skill 수·내 기여·인기·재사용, 실적/DEMO 구분 (FR-UI-1)
```
- 표시 전용, 상태 변경 없음. C10 스냅샷만 소비.

## C12 — DashboardServer (로컬 읽기전용, 범위 변경)
```
serve_readonly(snapshot_provider: () -> OrgSnapshot, host="127.0.0.1") -> None
    # localhost 읽기전용 화면. 쓰기/승인/게시 엔드포인트 없음 (FR-UI-2, NFR-SEC-2)
```
- 화면 구성의 근거: 사용자 승인 FR-UI/FR-ORG. 특정 외부 구현 코드·backend 구조에 의존하지 않는다. **UI 프레임워크·갱신 방식·표시 방식 미결정**(Code Generation).

---

## 서비스 오케스트레이션 메서드
S1~S3 서비스의 메서드·흐름은 `services.md` 참조. C10~C12(집계·표현)는 읽기전용 파생으로 서비스 오케스트레이션 밖에서 스냅샷을 소비한다.

## Current contract correction — scenario continuation
The approved `construction/plans/p1-scenario-correction-plan.md` supersedes earlier task-specific access schema in this document. Shared procedure contains only action=file-access and method=excel-com-attach. C7/S1/C6 validate workbook accessibility and read-only evidence (workbook_readable), independent of production rows. C7 returns a local workbook snapshot preserving sheet names and UsedRange origins. S2 receives a separate local task mapping, interprets current columns/rows, verifies OLS and creates the actual3+forecast1 PNG. No task schema, chart or content is shared. S3 owns reuse eligibility as well as publication state; explicit execution confirmation does not replace integrity or lifecycle eligibility. CJ now integrates A/B completed handoffs; original authors and prior validation are preserved.
