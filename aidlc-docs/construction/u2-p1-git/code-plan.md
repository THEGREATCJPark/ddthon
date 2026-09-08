# U2 최소 Code Plan (P1·후보화·게시·Git 전송)

**단계**: CONSTRUCTION / Code Generation Part 1 (Plan) — Unit **U2** (담당: B 한석훈)
**작성일**: 2026-09-08
**전제**: FD/NFR 개정본(P1 실패 모델 확정 = Office 암호화 + 실행 중 Excel attach, D-5) 승인. CJ 공통 계약 구현 제공됨(`ef03b3a`/`cfc62e9`). C-c(A)는 대기.
**진행 순서 준수**: FD 확인 → NFR 확인 → **본 Code Plan 승인** → 구현. 승인 전 코드 미작성.

---

## 1. 파일·소유 (단일 수정자 = B)
| 파일 | 컴포넌트 | 역할 |
|---|---|---|
| `skillloop/envharness_p1.py` | C7-P1 | 암호화 합성 파일 생성(COM) + 실행 중 Excel 준비 + `attempt_direct_access` 관찰 |
| `skillloop/experience_service.py` | S2 | run_p1 흐름·OLS(FR-P1-5)·후보화(FR-P1-6) |
| `skillloop/replay.py` | C6 | 독립 Replay(`run_file_access_procedure` 별도 재수행) |
| `skillloop/publish_pipeline.py` | S3 | 상태머신·게이트·lifecycle 영속·읽기전용 조회 계약(#7) |
| `skillloop/gitsync.py` | C4 | team-skill-store 전용 미러 pull/push (blob 전송만) |
| `tests/test_*_u2.py` | — | 아래 검증 |

**호출만(수정 금지)**: `store.py`/`usage.py`/`cli.py`/`descriptor.py`(CJ), `match.py`/`reuse_service.py`(A).

## 2. 호출 계약 (확정 API 기준)
- **CJ store (`ef03b3a`)**: `save_lifecycle_state(ref, state, evidence)`/`load_lifecycle_state(ref)`/`list_lifecycle_records()`; `export_bundle(refs: list[dict]) -> bytes`; `import_bundle(blob) -> list[PutResult]`.
- **CJ usage (`cfc62e9`)**: `export_shared_usage() -> bytes`; `import_shared_usage(blob, local_ref_exists) -> list[dict]`; `compute_event_id(...)`.
- **A (대기, C-c)**: `SkillSearchMatcher.search(problem)`, `S1.apply_and_verify` → 확정 전 검색·파일접근 재사용 분기 `NOT_RUN`.
- **A 전달 계약(신규)**: `run_file_access_procedure(procedure, env) -> AccessResult{ok, content, method, evidence}` (coordination-blockers §C-c, FD §1).
- **U2 정의**: `replay(candidate, env) -> ReplayResult{verdict, candidate_ref, evidence}`; gitsync `pull/push_descriptors(bytes)/push_shared_usage(bytes)/last_sync/status`; S3 `query_lifecycle_state`/`list_lifecycle_states`.

## 3. P1 실패 모델 구현 (D-5 확정)
- `setup_encrypted_open_xlsx_env(data_rows, password)`: win32com로 3개월 데이터 워크북 생성 → `SaveAs(FileFormat=51, Password=…)`(OLE-CFB) → 사용자 열람 상태(실행 중 Excel) 준비. password는 사전조건 소유(Agent/후보 미전달).
- `attempt_direct_access(path)`: 표준 zip 리더 실제 실행 → 암호화본 `BadZipFile` 관찰(`ok=False`, 강제 raise 아님).
- 허용 대안(Agent 탐색): `win32com.GetActiveObject("Excel.Application")` → 워크북 매칭 → 셀 read-only 읽기(Save 미호출) → `run_file_access_procedure` 계약으로 반환.
- Excel 미설치/미열림 → 해당 경로 `NOT_RUN`.

## 4. 실행 명령
- `python -m skillloop.cli run-p1 [--run-id ID]` (직접실패→(검색 대기)→대안→OLS→후보→검토·Replay·게시 시도).
- gitsync 초기화(D-4): `python -m skillloop.cli store-init`(team-skill-store 미러) — 미러 경로는 Code Plan 승인 후 확정.
- `pytest tests/ -q` (U2 추가분 + 기존 P0 불변).

## 5. 검증 방법 (U2-V1~V14 대응)
- **unit/property**: OLS 불변식(기준월·3점·음수 clamp), 후보 digest dedup, 게이트(승인+동일성+PASS), 상태 구분, event_id 보존.
- **integration(Excel 있을 때)**: 암호화 직접실패 관찰 + attach 대안 획득 + 원본 mtime/hash 무변경 + Save 미호출; C6 독립 Replay가 최초 artifact 미재사용.
- **NOT_RUN 유지**: 실제 원격 pull/import·CONFLICT 왕복(C-b), 이벤트 공유 왕복(C-d), lifecycle 재시작 영속(C-a), 검색·파일접근 재사용(C-c/A 대기), Excel 미설치 P1 경로.
- **실패 실행 근거 ≠ NOT_RUN**: 403 push는 실패 실행 근거로 보존.

## 6. 작업 순서
1. `envharness_p1.py`(암호화 생성·attach 관찰) + unit — **직접실패/대안 획득 실증 재현**.
2. `replay.py`(`run_file_access_procedure` 기반 독립 Replay) + unit.
3. `experience_service.py`(OLS·후보화; 검색·재사용은 A 계약 자리만·NOT_RUN) + property/unit.
4. `publish_pipeline.py`(상태머신·게이트·`save_lifecycle_state`·`export_bundle([ref])`·조회 계약#7) + unit.
5. `gitsync.py`(미러 pull/push blob 전송·`local_ref_exists` 연결·D-3) + unit.
6. 통합(run-p1 e2e, Excel 있을 때) — **독립 Replay 실검증은 구현 후 실제 수행**. 원격 왕복·A 분기는 NOT_RUN 유지.

> **미검증 독립 Replay는 구현 후 실제 검증**한다(현재 미구현 → NOT_RUN). CJ 공통 계약 승인 ≠ U2 전체 구현 승인 — 본 Code Plan 승인 범위로만 착수.
