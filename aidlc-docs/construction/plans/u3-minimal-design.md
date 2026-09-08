# U3 최소 설계 — 조직 집계·상태줄·읽기전용 대시보드 (CJ)

- **상태**: **구현·검증 완료(2026-09-08)** — Code Plan 승인 후 §4 순서대로 구현. 검증: U3 단위 21 passed + 전체 63 passed(회귀 없음), `skillloop status` 실데이터(reuse=3) 확인, 대시보드 실 HTTP(127.0.0.1) GET 200·정의외 404·POST 405. lifecycle/last_sync 실데이터·조직 시연 = 계약7·C4 연결 후 **NOT_RUN**. 하단 상태줄 연결 = 사용자 settings 필요(실제 확인 전 연결완료 미보고).
- **작성일**: 2026-09-08
- **소유(단일 수정자)**: CJ — `org_aggregator.py`(C10)·`statusline.py`(C11)·`dashboard.py`(C12)·`cli.py`(서브커맨드 추가). 전송 `gitsync.py`는 **B 소유 → U3 미수정**.
- **근거**: 승인된 FR-UI-1/2/3, FR-ORG-1~5, FR-USAGE-3/4, Application Design C10/C11/C12(component-methods.md), 계약 6·7·8, unit-of-work.md U3 항목. **외부 사전 구현 Reference 미사용.**
- **성격**: C10~C12 **집계·표현은 읽기전용**(쓰기·승인·게시 없음). C3 공유 이벤트 import(쓰기)는 U3 범위가 아니라 usage.py(C-d) 소유이며 여기서 재구현하지 않는다.

> 이 문서는 **확정된 요구사항·결정을 재질문하지 않는다.**

---

## 1. 범위 경계 (확정)

| 확정 사항 | 근거 |
|---|---|
| UI·조직 집계는 **승인된 필수 범위**(P0 비블로킹 ≠ 선택 기능) | unit-of-work.md U3 |
| C10~C12 **읽기전용**(소유 상태 미수정, usage 쓰기 없음) | FR-UI-2, NFR-SEC-2 |
| 상태줄·대시보드 **동일 단일 OrgSnapshot** 소비, 실제 실적/`DEMO_SEED` 구분 | FR-UI-3, FR-USAGE-3/4 |
| dedup: 서로 다른 Skill = digest·`(id,version)` 기준 | FR-ORG-1 |
| 조직 재사용 집계 = **event_id dedup된 VERIFIED_REUSE 이벤트**(C3 소유 dedup 재사용) | FR-USAGE-4, FR-ORG-3 |
| 로컬 후보/검토/게시대기 vs 원격 게시완료(PUBLISHED) **구분** | FR-ORG-4 |
| 상태는 **S3 읽기전용 조회 계약(계약7)으로만** — C10은 게이트·전이 재구현·추정 안 함 | AD Request Changes, 계약7 |
| 원격 게시본은 `remote_publish_evidence`/`local_review_evidence` **분리 표시**, 수신 환경 승인·Replay 기록 미생성 | AD-Q4 |
| 대시보드 = **localhost(127.0.0.1) 읽기전용** 시연 표면(외부 노출·인증·멀티유저·호스팅 범위 외) — **승인된 로컬 UI 범위** | FR-UI-2, NFR-SEC-2, AD-Q5 예외 |
| secret·원본 업무 데이터·procedure 내부 미포함(합성만) | NFR-SEC-1 |

### 1.1 확정된 열린 결정 (재질문 대상 아님)

- **결정1 — lifecycle 상태 읽기 소스 = 보류형(계약7 대기)**: C10은 `LifecycleView`(계약7 형태) provider에만 의존한다. **계약7(B의 `S3.list_lifecycle_states`) 미연결 시 상태 = "상태 조회 미연결"로 표시하고 0건·특정 상태로 추정하지 않는다.** **실제 제품 경로에서 `store`를 직접 읽는 임시 우회를 만들지 않는다**(`store.list_lifecycle_records()`는 C-a 저장 API로 남되 C10이 직접 읽지 않음). B 제공 시 provider만 연결. **이 결정으로 나머지 U3(Skill·재사용·기여 집계, 상태줄, 대시보드)를 대기시키지 않는다.** 상태 UI·테스트는 계약7 형태의 **명시적 test 대역(fake)**으로 준비.
- **결정2 — 대시보드 수단 = Python stdlib `http.server`**: 127.0.0.1 바인딩, **대시보드에 필요한 GET 경로만** 제공, **프로젝트 디렉터리·로컬 파일 임의 노출 금지**. 표준 라이브러리 선택 이유는 구현·설치 부담 절감(외부 Reference 금지와 외부 라이브러리 금지는 별개 조건). localhost HTTP는 승인된 로컬 UI 범위.

---

## 2. Functional Design (최소 깊이)

### 2.1 C10 — OrgAggregator (`org_aggregator.py`, 읽기전용)

**계약**: `build_snapshot(store, usage, lifecycle_view, sync_meta) -> OrgSnapshot`

**읽는 소스**:
- Skill 목록: `store.list()` → `{id, version, digest, origin, applicability}`(불변 content; **procedure는 스냅샷 미포함**).
- 로컬 실제 재사용: `usage.current_count(id, version)`.
- 조직 재사용(공유): `usage.shared_reuse_count(id, version)` / `usage.list_shared_events()`(이미 event_id dedup·VERIFIED_REUSE·비-DEMO).
- lifecycle 상태: **`LifecycleView` provider(주입)** — 계약7 형태. **미연결(provider=None)이면 상태 = "상태 조회 미연결"**(0·추정 금지). **store 직접 읽기 우회 없음.**
- last_sync: **`SyncMeta` provider(주입)** — C4(gitsync.py, B 소유). 미연결 시 `queryable_range="local-only, 동기화 이력 없음"`.

**provider 프로토콜(계약7·C4 형태, U3가 정의·주입; 실구현은 B)**:
```
class LifecycleView(Protocol):                 # 계약7 형태
    def list_lifecycle_states(self) -> list[dict]: ...
    # 각 항목: { ref{id,version,digest}, lifecycle_state,
    #           local_review_evidence, remote_publish_evidence }
class SyncMeta(Protocol):                       # C4 last_sync 형태
    def last_sync(self) -> dict | None: ...     # { synced_at, branch_revision }
```

**OrgSnapshot 규격(계약8)**:
```
OrgSnapshot = {
  summary:  { published_skills, distinct_skills, verified_reuses,
              reuser_aliases, contributor_aliases },        # FR-ORG-1
  skills:   [ { id, version, digest, applicability,
                local_reuse_count, org_reuse_count } ],     # dedup·버전 구분(digest)
  people:   [ { alias, role: author|reuser,
                contributions, cross_reuse } ],             # FR-ORG-2
  states:   "상태 조회 미연결"  |  [ { ref, lifecycle_state,       # provider 미연결 시 문자열 그대로
                local_review_evidence, remote_publish_evidence } ],  # 연결 시 값 그대로(추정 아님) FR-ORG-4/AD-Q4
  ranking:  [ ... ],   # 실제 검증 재사용 내림차순, 동점 시 id 오름차순(match.py 동일 결정성)
  activity: [ ... ],   # 최근 이벤트(list_shared_events 시간순)
  last_sync:  { synced_at, branch_revision, queryable_range },  # FR-ORG-5(미연결 시 local-only 표기)
  accounting: { actual_reuses, demo_seed_reuses }               # FR-USAGE-3 구분
}
```

**identity 규칙(FR-ORG-2)**: 작성자 = `origin.author`, 재사용자 = `reuser_alias`(C-d 이벤트 alias, 기본 "local"). `cross_reuse` = 자신이 작성하지 않은 Skill 재사용 이벤트 수.

**불변식**: (a) 소유 상태 무쓰기, (b) 상태는 provider 값 그대로(전이·게이트 재구현·추정 금지; 미연결=명시 문자열), (c) `local_review_evidence` 없으면 "원격 게시(다른 환경 근거)"로만 표시, (d) `demo_seed`는 `actual_reuses`에 미합산.

### 2.2 C11 — StatuslineRenderer (`statusline.py`)

**계약**: `render_statusline(snapshot) -> str` — 순수 함수(I/O 없음).
- 표시: 조직 Skill 수 · 내 기여 · 인기 Skill · 재사용 현황. 실제/`DEMO_SEED` 구분. lifecycle 미연결이면 상태 자리에 "상태 조회 미연결".
- "내" = env `SKILLLOOP_ALIAS`(C-d 동일 소스, 기본 "local"). 상태 변경 없음.

### 2.3 C12 — DashboardServer (`dashboard.py`, localhost 읽기전용)

**계약**: `serve_readonly(snapshot_provider, host="127.0.0.1", port=…) -> None`
- 127.0.0.1 바인딩. **정의된 GET 경로만 처리**(`/`, `/skills`, `/skill?id=&version=`, `/people`, `/activity`; 검색 `/skills?q=` 서버측 필터). **정적 파일 서빙·디렉터리 리스팅 없음**(프로젝트 파일 임의 노출 금지). 정의 외 경로 → 404, 비-GET → 405.
- 쓰기·승인·게시 엔드포인트 없음(NFR-SEC-2). 스냅샷 = C11과 **동일 OrgSnapshot**.
- 화면(FR-UI-2): 조직 요약 · Skill 목록/검색/상세 · 기여·실제 재사용 · lifecycle 상태(연결 시)/미연결 표시 · 최근 활동 · **last_sync·queryable_range 함께 표시**(FR-UI-3).

---

## 3. NFR (minimal)

| NFR | U3 반영 |
|---|---|
| NFR-SEC-1 | 스냅샷·화면에 secret·원본 데이터·procedure 내부 미노출(합성만). |
| NFR-SEC-2 | C10~C12 무쓰기. 대시보드 127.0.0.1·정의된 GET 경로만·비-GET 405·정적파일/디렉터리 리스팅 없음. |
| FR-UI-3 | 상태줄·대시보드 동일 OrgSnapshot, 둘 다 last_sync·queryable_range·실적/DEMO 구분·lifecycle 미연결 표시. |
| FR-USAGE-3/4 | actual vs demo_seed 분리(accounting), 조직 재사용 = event_id dedup(C3 재사용). |
| 계약7 미연결 | lifecycle 상태 = "상태 조회 미연결"(추정 금지). test 대역으로 연결형 동작도 검증. |
| 테스트 | pytest — 합성 store/usage fixture + **계약7 형태 LifecycleView test 대역**으로 집계·dedup·구분·상태(연결/미연결) 검증; renderer 문자열 검증; 대시보드 GET=스냅샷 파생 HTML·정의외 404·비-GET 405·무변경·파일 미노출 검증. 외부 네트워크 미의존. |
| NOT_RUN | 실데이터·조직 시연은 U2 게시·pull + 계약7(S3 조회)·C4(last_sync) 실연결 후 — 그 전 NOT_RUN 명시. |

**NFR Design·Infrastructure Design 생략**: 신규 NFR 패턴·클라우드 자원 없음(로컬 stdlib·읽기전용). SKIP-BOUNDARY 준수(위 표 반영).

---

## 4. Code Plan (변경 파일 · 실행 명령 · 검증 · 제공 순서)

**단일 수정자 = CJ. B 소유 파일(gitsync.py 등) 미수정. match.py/reuse_service.py(A) 미수정.** P1(A·B)과 독립 병렬.

| 순서 | 파일 | 내용 | 검증(테스트) |
|---|---|---|---|
| 1 | `skillloop/org_aggregator.py`(신규) | `LifecycleView`/`SyncMeta` protocol + OrgSnapshot 규격 + `build_snapshot`. 읽기 전용. 미연결 시 "상태 조회 미연결". store 직접 lifecycle 읽기 없음. | `tests/test_org_aggregator.py`: dedup·버전 구분·identity·actual/demo 분리·상태(대역 연결/미연결)·무쓰기 |
| 2 | `skillloop/statusline.py`(신규) | `render_statusline(snapshot)` 순수 함수 | `tests/test_statusline.py`: 실적/DEMO 구분·내 기여(alias)·미연결 표기 |
| 3 | `skillloop/dashboard.py`(신규) | `serve_readonly` stdlib `http.server`, 127.0.0.1, 정의된 GET 경로만, 파일 미노출 | `tests/test_dashboard.py`: GET=HTML·정의외 404·비-GET 405·무변경·secret/파일 미노출 |
| 4 | `skillloop/cli.py`(수정, CJ) | `status`(상태줄 출력)·`dashboard`(로컬 서버 기동) 서브커맨드. P0 경로·run_id dedup **불변**. `_ensure_utf8_stdout` 재사용 | 기존 pytest 회귀 없음(현재 42 passed 유지) |

**실행 명령(구현 후)**:
- `python -m pytest tests/test_org_aggregator.py tests/test_statusline.py tests/test_dashboard.py -q` (U3 단위 검증)
- `python -m pytest -q` (전체 회귀 — 기존 42 passed 유지 확인)
- `python -m skillloop status` (상태줄 1줄 출력, 로컬 스냅샷 기준)
- `python -m skillloop dashboard` (127.0.0.1 읽기전용 서버 기동; 수동 확인은 로컬 브라우저)

**제공 순서**: 1→2→3→4 각 단계 구현·검증·commit → 완료 SHA 기록. lifecycle/last_sync 실데이터 연결·조직 시연은 계약7·C4 제공 후(그 전 NOT_RUN). **Code Plan 승인 후 착수.**

## 승인된 하단 표현 보완
u3-statusline-followup-plan.md 사용자 승인 후 C11을 네 줄로 변경하고 status의 명시 경로/표시 옵션, 프로젝트 statusLine 설정을 연결한다. C10 집계·S3/C4 상태 근거·읽기전용·DEMO/actual 분리는 유지한다. 잘못된 별도 match 호출을 유도한 C9 안내는 기존 P0 호출 계약으로 정합화한다.
