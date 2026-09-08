# U2 공통 의존성 계약 — 검토 요청 (최소 설계·Code Plan 보완)

**단계**: CONSTRUCTION / (U2 착수 전 공통 의존성 정렬)
**작성일**: 2026-09-08
**작성자**: CJ (U0/U3 소유 파일 계약 제공)
**상태**: **승인됨(2026-09-08)** — C-a/C-b/C-d 계약·책임·제공 순서 확정. CJ 공통 의존성 **구현 진행**. 이 승인은 위 CJ 공통 의존성의 계약·구현에 한정하며 **B의 U2 전체 설계/Code Plan 승인은 포함하지 않는다.** (최초 작성 시 상태: 검토 요청)
**목적**: B(U2)가 착수하려면 CJ 소유 파일(`store.py`=C2, `usage.py`=C3)에 아직 없는 **export/import 계약과 공유 이벤트 영속화**가 선행되어야 한다. Inception·전체 범위 재분석 없이, 승인된 Application Design(`services.md`·`component-methods.md`·`component-dependency.md`·`unit-of-work.md`)과 **현재 코드**만 근거로 계약·담당자·제공 순서를 확정하기 위한 최소 보완이다.

> **범위 경계**: 이 문서는 **계약(인터페이스·규격·가드)** 확정을 위한 검토 요청이다. 승인 시에만 CJ가 해당 코드를 구현한다. B는 이 계약을 **호출**로만 사용하며 별도 저장·검증·직렬화를 재구현하지 않는다(우회 금지).

---

## 0. 현재 코드 격차 (사실 확인)

| 파일 | 소유 | 현재 상태 | U2가 필요로 하는 것 |
|---|---|---|---|
| `skillloop/store.py` (C2) | CJ(U0) | `get/list/put`(DEDUP/CONFLICT)만. **`export_bundle`/`import_bundle` 없음** | 승인 후보 descriptor 공유 export/import |
| `skillloop/usage.py` (C3) | CJ(**단일**, U3) | `record_actual_reuse` + `{counts, seen_run_ids}`만. **공유 이벤트 저장·`export_shared_usage`/`import_shared_usage` 없음** | 성공 근거를 실은 재사용 이벤트 export/import |
| `skillloop/publish_pipeline.py` (S3) | B(U2) | 미착수 | lifecycle **상태 판단·전이**(단일 writer) + 읽기전용 조회 계약 |

> **핵심**: 현재 `usage.py`는 `counts`(집계 수)와 `seen_run_ids`(실행 dedup)만 영속한다. **과거 카운트에서 이벤트나 성공 근거를 역산해 만들 수 없다** — 공유 이벤트는 **이 계약 도입 이후의 실제 성공에서만** 생성된다.

---

## C-a. Lifecycle 저장 책임 단일화 (S3 상태, B 제안 lifecycle.json 조정)

### 쟁점
- 승인 `services.md`/`component-dependency.md`: **S3(PublishPipeline)가 상태를 소유·판단**하고, **SkillStore(C2)의 lifecycle 저장 계약으로 영속**한다. C10은 **S3 읽기전용 조회 계약으로만** 상태를 읽는다.
- B의 U2 제안: **자체 `lifecycle.json`** 을 두어 상태를 저장.
- 충돌: 두 저장 소유자(별도 `lifecycle.json` vs C2 store)가 생기면 승인 설계와 어긋나고, 공통 상태의 이중 소유가 발생한다.

### 최소안 (권고 결정)
1. **단일 상태 판단·writer = S3** (`publish_pipeline.py`, **B 단일 수정자**). lifecycle 상태 전이(`PROPOSED→UNDER_REVIEW→(APPROVED|REJECTED)→REPLAYED(PASS|FAIL|NOT_RUN)→(LOCALLY_APPROVED|BLOCKED)→(PUBLISHED|PUBLISH_PENDING)`)를 **판단·기록하는 유일 주체.** — 유지.
2. **단일 저장 구현자 = C2(`store.py`, CJ).** S3는 **자체 `lifecycle.json`을 만들지 않고**, CJ가 제공하는 lifecycle 저장 계약을 **호출**해 영속한다. → B 제안 `lifecycle.json`은 **채택하지 않음**(두 번째 저장 소유자 생성·승인 설계 이탈 방지).
3. **소비자 격리**: C10/U3는 상태 파일을 직접 읽지 않고 **S3 읽기전용 조회 계약**(`query_lifecycle_state`/`list_lifecycle_states`, `remote_publish_evidence`/`local_review_evidence` 분리)으로만 읽는다. → **물리적 저장 위치는 S3 뒤에 은닉**되므로 소비자에게 투명하다.
4. **동시 수정 회피**: lifecycle 상태는 descriptor 저장과 **분리된 store 섹션/키스페이스**로 둔다(C2가 원자적 저장·단일 writer 유지). descriptor 쓰기(C2.put)와 lifecycle 쓰기(S3 경유)가 같은 JSON 객체를 교대 갱신하지 않도록 한다.

### 계약 (CJ가 `store.py`에 제공, 승인 후 구현)
```
# C2 (store.py) — lifecycle 저장 계약 (S3 전용 호출; C2는 상태를 판단하지 않음)
save_lifecycle_state(skill_ref: {id, version}, state: str, evidence: dict) -> None
    # S3가 판정한 상태를 그대로 영속만 한다. C2는 전이 규칙을 재구현/검증하지 않는다.
load_lifecycle_state(skill_ref: {id, version}) -> {state, evidence, updated_at} | None
list_lifecycle_records() -> list[...]   # S3가 조회 계약 구현에 사용(원자적 읽기)
```
- **가드**: C2는 lifecycle 전이 규칙·게이트를 **판단하지 않는다**(저장만). 상태 판단·게이트는 **S3 단독.** C10 등은 이 저수준 계약을 직접 호출하지 않고 **S3 조회 계약**만 사용.

### 담당자·순서
- **CJ**: `store.py`에 `save/load_lifecycle_state` 저장 계약 제공(C-b와 함께).
- **B(S3)**: 상태 판단·전이 + 위 계약 호출로 영속 + `query_lifecycle_state`/`list_lifecycle_states` 읽기전용 조회 제공. **자체 lifecycle.json 미도입.**

---

## C-b. Store descriptor export/import (SHAREABLE 전달·가드)

### 계약 (CJ가 `store.py`=C2에 제공, 승인 후 구현 — `component-methods.md` 준수)
```
export_bundle(refs: list[{id, version, digest}]) -> bytes
    # refs = S3가 SHAREABLE로 판정한 정확한 후보 목록(정확한 digest 포함).
    # 각 ref에 대해 로컬 저장본을 조회, content 재직렬화 시 digest 재계산해
    # 선언 digest와 일치할 때만 포함. content(불변부)만 내보낸다(usage/카운트 제외).
import_bundle(blob: bytes) -> list[PutResult]
    # content만 역직렬화 → digest 재계산·검증 → C2.put 규칙 재사용
    # (동일 id/version + 동일 digest = DEDUP no-op / 다른 digest = CONFLICT 거부).
```

### 공유 자격 전달 방식 (명확화)
- **SHAREABLE 판정 = S3 소유**(승인 + Replay PASS + digest 동일성). **C2는 공유 자격을 스스로 판정하지 않는다.**
- 흐름: **S3가 SHAREABLE로 판정한 정확한 후보 refs(`{id,version,digest}`)** 를 C2.export_bundle에 **전달** → C2는 그 refs에 해당하는 로컬 content만 내보낸다.
- C2는 "미승인 후보"를 알 필요 없이, **전달받지 않은 것은 내보내지 않는다**(허용 목록 방식). S3가 미승인 후보를 refs에 넣지 않으면 export 불가 → **미승인 export 금지**가 구조적으로 보장.

### 가드 (모두 유지)
- **미승인 후보 export 금지**: export 대상은 S3가 넘긴 SHAREABLE refs로 한정(허용 목록).
- **digest 재계산 검증**: export/import 양측 모두 content로 digest 재계산 → 선언값과 불일치 시 제외/거부.
- **동일 id/version**: DEDUP(동일 digest, no-op) / CONFLICT(다른 digest, 거부) — 기존 `put` 규칙 그대로.
- **content만 import**: usage·카운트·실적은 절대 bundle에 포함하지 않음(그건 C-d 경로).
- **원격 문자열로 로컬 승인/Replay 생성 금지**: import는 저장만. 수신 환경의 승인·LOCALLY_APPROVED·Replay 기록을 **만들지 않는다**(그건 수신자 S3의 독립 판단).
- **B 우회 금지**: B는 별도 descriptor 직렬화·store·CONFLICT를 재구현하지 않고 이 계약을 호출.

### 담당자·순서
- **CJ**: `store.py`에 `export_bundle`/`import_bundle` 구현(승인 후). **C-a·C-b는 같은 파일(store.py)이므로 한 번에 제공** — B 착수 선행 1순위.
- **B(S3)**: SHAREABLE refs 판정 → export_bundle 호출; pull 수신 시 import_bundle 호출(로컬 승인/Replay는 별도 S3 판단).

---

## C-d. 공유 usage 이벤트 최소 규격·호출 계약 (VERIFIED_REUSE)

### 격차
현재 `usage.py`는 `counts`/`seen_run_ids`만 영속 → **성공 근거를 export할 수 없다.** 공유하려면 **이벤트 영속화**가 선행돼야 한다. **기존 카운트에서 과거 이벤트·근거를 만들어내지 않는다**(도입 이후 실제 성공만 이벤트화).

### 이벤트 최소 규격 (usage.py=C3, CJ 단일 수정자; 승인 후 구현)
```
SharedReuseEvent = {
    event_id:     str,     # 결정적 파생(예: sha256(skill_ref+run_id+reuser_alias)) → 왕복 dedup 키
    skill_ref:    {id, version, digest},   # 정확한 Skill 참조(digest 포함)
    reuser_alias: str,     # 재사용 주체 별칭(비민감; secret/원본 데이터 아님)
    evidence:     {is_real_success: true, verification: {...}},  # 실제 성공 근거 요약(비민감)
    demo_seed:    false,   # 비-DEMO만
    timestamp:    str,
}
```
- **VERIFIED_REUSE 자격**(export 대상): ① 정확한 Skill 참조(`{id,version,digest}`)가 **로컬에 존재** + ② **실제 성공 근거**(is_real_success=True) + ③ **비-DEMO**(demo_seed=False). — **SHAREABLE(게시 게이트)와 별개.**

### 영속화 변경 (record_actual_reuse 확장)
```
record_actual_reuse(evidence)  # 기존: counts +1(dedup) — 유지
    # 확장: is_real_success & !demo_seed & (신규 run_id)일 때
    #        SharedReuseEvent를 함께 영속(events 리스트). 카운트되지 않으면 이벤트도 생성 안 함.
```
- **영속 구조**: `{counts, seen_run_ids, events}`로 확장(기존 필드 보존·하위호환).
- **역산 금지**: 도입 전 카운트에는 이벤트가 없다 → 그 카운트는 export 불가(정직한 실적만 공유).

### export/import 계약 (component-methods.md 준수)
```
export_shared_usage(scope=VERIFIED_REUSE) -> bytes
    # 자격(①②③) 통과한 events만 직렬화. counts 원본·seen_run_ids·로컬 DB 파일은 전송 안 함(FR-SYNC-5).
import_shared_usage(blob) -> list[...]
    # 각 event: 자격 재검증(로컬에 skill_ref 존재 + is_real_success + 비-DEMO)
    #  → event_id dedup(이미 반영된 event_id는 no-op) → 통과분만 조직 실적 1회 반영.
```
- **가드**: 검증·dedup은 **C3 단독**(C4는 전송만, 재구현 금지). 동일 이벤트 왕복(A→B→A) 시 `event_id`로 **1회만** 반영.

### 담당자·순서
- **CJ**: `usage.py`에 이벤트 영속화 + `export_shared_usage`/`import_shared_usage` 구현(승인 후). U3 범위.
- **B(C4=`gitsync.py`)**: `push_shared_usage`/`pull`로 **전송만**. 검증·dedup 호출은 C3.

---

## P1. A·B 검색·파일접근 Skill 적용·검증 조율안 (짧게 — P0 인계 비지연)

> P0(pip-install 흐름)은 A 인계 대기 중이며 **이 조율로 지연시키지 않는다.** 아래는 P1(파일접근) 착수 시 A·B가 맞춰야 할 최소 계약이다.

1. **검색(C5=`match.search`, A 소유)은 signal 비의존**: applicability 매칭은 신호 문자열에 무관하게 동작. P0=`"pip-install-fail:<pkg>"`, **P1 파일접근=`"file-access-fail:<유형/경로>"`** 명명 규약을 A·B가 공유. `SearchOutcome` 상태 집합(MATCH/NO_MATCH/ERROR/TIMEOUT/NOT_INVOKED) 동일. → B(S2)는 NO_MATCH 판정에 **동일 C5 계약**을 호출(재구현 금지).
2. **적용·검증(S1=`reuse_service.apply_and_verify`, A 소유)은 시나리오 비의존**: `selected.procedure.action`으로 분기(P0=`pip-install`, P1=파일접근 유형). B(S2)는 파일접근 유형 재사용 시 **S1을 호출**(재구현 금지, `unit-of-work.md` U2 경계).
3. **환경 분리**: `envharness_p0.py`(CJ)=이중 mock index, `envharness_p1.py`(B)=보호 XLSX. `apply_and_verify(selected, obs, env, run_id)`의 `env`는 **harness 비의존 EnvCtx**로 받음 → P1은 B의 P1 harness가 만든 env를 전달. **A·B 합의 필요 지점**: 파일접근 "효과 검증" 단계 구현 위치(S1 내부 분기 vs P1 harness 제공 verify 헬퍼 호출) — A가 S1 분기 골격, B가 P1 harness의 접근효과 검증 사실 제공.
4. **카운트 경로 동일**: 파일접근 재사용의 실제 성공도 **C3.record_actual_reuse 단일 경로**로만 카운트(P0와 동일 계약). 새 절차 발견 시에만 S2가 C1 후보 생성 → S3 게이트.

---

## 제공 순서 (B에게)

1. **[선행·최우선] C-a + C-b (`store.py`, CJ)**: lifecycle 저장 계약 + descriptor export/import. → B의 S3 상태 영속·공유가 여기에 의존.
2. **[다음] C-d (`usage.py`, CJ)**: 공유 이벤트 영속화 + export/import. → B의 gitsync 공유 usage 전송이 여기에 의존.
3. **[병행] P1 조율(1~4)**: A·B가 signal 규약·S1 호출 경계·env 전달·검증 위치 합의. P0 인계와 독립.

> **선행 조건**: 위 C-a/C-b/C-d는 **미구현 공유 기능**이었다. 본 문서 **승인(2026-09-08)** 에 따라 CJ가 `store.py`/`usage.py`/`cli.py`에 구현한다. B는 계약 시그니처에 맞춰 S3/gitsync 설계를 진행하되 CJ 소유 파일은 수정하지 않는다(호출만).

---

## 승인 반영 조건 (2026-09-08 사용자 승인 시 확정)

- **C-a**: S3(B)가 lifecycle 상태 전이를 **판단**, C2(CJ)는 전달받은 상태의 **저장·로드만** 수행(전이 규칙 미판단). 상태·근거는 **정확한 candidate의 `id`/`version`/`digest`** 에 연결(키에 digest 포함). 외부 소비자 상태 조회는 **S3 계약 유지**(C2 저수준 계약 직접 호출 금지).
- **C-b**: export는 **S3가 공유 가능하다고 판정한 정확한 candidate refs만** 대상(허용목록). **단순 SHAREABLE 문자열/bool로 전체 저장 항목을 내보내지 않음** → API는 `scope` 플래그가 아니라 **명시적 refs 목록**을 받는다. 판정 대상과 export 대상의 `id`/`version`/`digest` **일치 확인**. **최초 게시·실패 후 재시도 가능**, **PUBLISHED를 export 전제로 삼지 않음.** import는 digest 재계산·DEDUP/CONFLICT를 거쳐 **content만** 반영, **원격 문자열로 로컬 승인·Replay 기록 미생성.**
- **C-d**: 같은 실제 재사용 이벤트는 export/import/재전송 시 **`event_id` 유지**(결정적 파생). 로컬에서 이미 집계한 이벤트가 다른 환경을 거쳐 돌아와도 **추가 집계 금지**(event_id dedup). **기존 counts에서 이벤트·성공 근거 역산 금지.** 새 이벤트 생성에 필요한 **exact Skill 참조(`{id,version,digest}`)와 `reuser_alias`는 호출자(cli/S1 경로)가 제공** — C3는 전달받아 이벤트 생성. 필요한 **CJ 소유 CLI 연결 포함**(run-p0 이벤트 생성 배선 + `share-export`/`share-import` 얇은 서브커맨드). **기존 P0 호출·run_id dedup 불변**(카운트 로직 미변경, 이벤트 생성은 counted=True일 때만).

---

## 최소 Code Plan — 변경 파일·검증·제공 순서

### 1단계: C-a + C-b (`skillloop/store.py`, CJ 단일 수정자)
**변경 파일**
- `skillloop/store.py`: 저장 스키마 `{skills}` → `{skills, lifecycle}`(하위호환 load). 추가 메서드:
  - `save_lifecycle_state(skill_ref{id,version,digest}, state, evidence)` / `load_lifecycle_state(skill_ref)` / `list_lifecycle_records()` — 저장만, 전이 미판단.
  - `export_bundle(refs: list[{id,version,digest}]) -> bytes` — 허용목록·digest 재계산·불일치 제외·content만.
  - `import_bundle(blob) -> list[PutResult]` — digest 재계산·불일치 거부·`put` 규칙(DEDUP/CONFLICT)·content만·승인/Replay 미생성.
- `tests/test_store.py`: lifecycle 저장·로드(digest 키), export 허용목록·digest 불일치 제외, import DEDUP/CONFLICT·digest 위조 거부·content만 반영 테스트 추가.

**검증**: `pytest -q` 전체 그린(기존 19 PASS + 신규 store 테스트). 기존 P0 5 테스트 불변.

### 2단계: C-d (`skillloop/usage.py` + `skillloop/cli.py`, CJ 단일 수정자)
**변경 파일**
- `skillloop/usage.py`: 저장 스키마 `{counts, seen_run_ids}` → `{counts, seen_run_ids, events}`(하위호환 load). `ReuseEvidence`에 `reuser_alias` 추가. `build_evidence(..., reuser_alias="local")`. `compute_event_id(skill_ref, run_id, reuser_alias)`(결정적 sha256). `record_actual_reuse`: counted=True & skill_ref에 digest 존재 시 이벤트 생성(카운트 로직·run_id dedup 불변). `export_shared_usage() -> bytes` / `import_shared_usage(blob, local_ref_exists) -> list` (VERIFIED_REUSE 재검증·event_id dedup·로컬 존재 확인; **counts 미변경**, 조직 실적은 events).
- `skillloop/cli.py`: run-p0가 `build_evidence`에 `digest=selected.digest`, `reuser_alias`(env `SKILLLOOP_ALIAS`, 기본 "local") 전달. `share-export`/`share-import` 서브커맨드 추가(C3 export/import 호출, 로컬 존재 확인=기본 store).
- `tests/test_usage.py`: 이벤트 생성(counted 시)·event_id 결정성·재전송 dedup·기존 카운트 역산 없음(digest 없는 evidence는 이벤트 미생성)·import 로컬 존재 가드 테스트 추가.

**검증**: `pytest -q` 전체 그린. 기존 usage 7 테스트 불변(run_id dedup 유지). run-p0는 A 인계 전까지 `match.search`에서 정지(NOT_RUN 유지) — C-d 배선은 단위 테스트로 검증.

### 제공 순서 (각 단계: 계약·구현 → 검증 → commit/push → B에게 SHA 보고)
1. **C-a/C-b** (`store.py`) → 검증 → commit/push → **SHA 보고**
2. **C-d** (`usage.py`+`cli.py`) → 검증 → commit/push → **SHA 보고**
