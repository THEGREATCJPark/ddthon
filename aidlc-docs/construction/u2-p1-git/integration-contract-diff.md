# U2 통합 계약 차이 기록 (판단 요청)

> **성격**: 이 문서는 **수정 제안이 아니라 판단 요청**입니다. 코드·주석·테스트는 변경하지 않았습니다.
> U2 원 계약과 통합본 사이의 차이를 코드 근거와 함께 정리하고, 각 지점이 **의도된 설계 변경**인지
> **통합 중 유실**인지 소유자(CJ)의 판단을 요청합니다.
>
> **QA §9 준수** — 신규 기능 없음, 코드 무변경, 문서만 추가.

## 조사 대상

- 검토 기준 커밋: `main` = `0041d87`
- 계약 변형이 일어난 커밋: `7100f0a`  *(feat: integrate reproducible P0 and P1 environment capability loop …)*
- U2 원 커밋: `8c7999a` → `711466f` → `2886a63`
- 확인: `7100f0a` 이후 최근 커밋들은 `skillloop/envharness_p1.py`, `skillloop/replay.py`를 건드리지 않음
  (`git log --oneline -10 -- skillloop/envharness_p1.py skillloop/replay.py` 기준 마지막 변경이 `7100f0a`).
  → 계약 변형은 전부 통합 시점에 발생.

시그니처 자체는 유지됩니다:

| 계약 | 유지 | 근거 |
| --- | --- | --- |
| `run_file_access_procedure(procedure, env) -> AccessResult` | 시그니처 유지 | `skillloop/envharness_p1.py:290` |
| `replay(candidate, env) -> ReplayResult` | 시그니처·필드 유지 | `skillloop/replay.py:52`, `35-40` |

아래 4가지는 시그니처 아래에서 실제 데이터/동작이 달라진 지점입니다.

---

## 달라진 지점 4가지

### 1) `AccessResult.content`: `list[(month, total)]` → dict workbook snapshot

- **U2 원본** (`711466f`): `content = [(month:str, total_output:int|float), ...]`
- **통합본**: `content: dict | None` — workbook snapshot
  `{'sheets': [{'name', 'first_row', 'first_col', 'values'}]}`

근거:
- `skillloop/envharness_p1.py:65-70` — `AccessResult.content` 주석이 `list | None` → `dict | None`으로 변경
- `skillloop/envharness_p1.py:159-172` — `_snapshot_workbook`가 dict snapshot 생성
- 연쇄 변경: `skillloop/replay.py:97-99` — `replay_obtained_rows` → `replay_obtained_sheets`

### 2) procedure 인자가 읽기 위치 결정에 미반영 (전체 UsedRange snapshot)

- **U2 원본** (`711466f`): `_procedure_read_spec(procedure)`로 procedure에서
  `sheet / month_col / total_col`을 뽑아 **실제 읽기 위치**를 결정.
- **통합본**: procedure는 형태 게이트로만 쓰이고, 읽기는 procedure와 무관하게
  **전체 UsedRange를 통째로 snapshot**.

근거:
- `skillloop/envharness_p1.py:292` — procedure가 정확히
  `{'action':'file-access','method':'excel-com-attach'}`가 아니면 `invalid-procedure` 반환
- `skillloop/envharness_p1.py:159-172` — `_snapshot_workbook`가 procedure 참조 없이 모든 시트의 UsedRange를 읽음
- `skillloop/envharness_p1.py:191-208` — `_read_via_excel_attach`에 procedure의 시트·열 반영 로직 없음
  (원 `_procedure_read_spec` 제거됨)

### 3) `test_replay_uses_candidate_procedure` — monkeypatch 경로만 검증, 검증 공백

- 테스트(`tests/test_replay.py:80-94`)와 그 주석은
  "전달받은 candidate.procedure가 실제 접근 실행에 사용됨(read_spec에 반영)"이라고 서술.
- 그러나 이 테스트는 **monkeypatch한 가짜 리더**가 `proc` 인자를 받는 것만 확인합니다
  (`_reader(e, proc)`가 `seen["proc"] = proc`).
- **실제 코드경로** `_read_via_excel_attach`(`skillloop/envharness_p1.py:191-208`)는
  procedure를 무시하고 전체 UsedRange를 읽으므로, "procedure가 읽기에 반영된다"는
  성질은 **실제 경로에서 검증되지 않습니다** → 검증 공백.

근거:
- `tests/test_replay.py:80-94` (테스트·주석)
- `skillloop/envharness_p1.py:191-208` (procedure 무시)

### 4) 접근 성공 기준: "3개 완료월 행" → "구조 형태만"

- **U2 원본**: `_looks_like_completed_month_rows` — content가
  3개 완료월 `(month:str, total:int|float)` 행을 포함하는지 검사.
- **통합본**: `_valid_snapshot` — snapshot의 **구조 형태만** 검증
  (시트 존재, 값 행렬 사각형 여부 등). 값의 개수·타입 업무 기준 없음.

근거:
- `skillloop/envharness_p1.py:175-188` — `_valid_snapshot`
- `git show 711466f`에 있던 `_looks_like_completed_month_rows`가 통합본에서 삭제됨
- `skillloop/envharness_p1.py:313-314` — `workbook_readable = _valid_snapshot(content)`로 성공 판정

---

## U2 오더 원문과의 대조

- U2 오더/원 커밋 의도: **전달받은 procedure와 대상 env를 실제로 사용**해야 한다.
  - `711466f` 커밋 메시지: *"procedure 인자 실사용 — `_read_via_excel_attach`가 procedure 지정 시트·열 읽기 + read_spec evidence"*
  - `aidlc-docs/construction/u2-p1-git/code-plan.md:26` — A 전달 계약
    `run_file_access_procedure(procedure, env) -> AccessResult{ok, content, method, evidence}`
- 통합본은 시그니처상 procedure를 받지만 **읽기 위치 결정에는 사용하지 않습니다**(위 2, 3).
  → 오더의 "procedure 실사용" 의도와 통합본 동작 사이에 간극이 있습니다.

---

## CJ 판단 요청

각 지점이 아래 중 어느 쪽인지 판단을 요청합니다.

- **(a) 의도된 설계 변경**: 환경 능력(attach 가능 여부·read-only 무변경)만 검증하도록
  범위를 좁히고, 시트·열 해석은 상위(제품/Agent)로 이관한 결정.
- **(b) 통합 중 유실**: `711466f`의 procedure 실사용이 통합 병합 과정에서 의도치 않게 되돌려진 것.

## 각 경우의 후속 조치 계획

- **(a) 의도된 설계 변경으로 확정 시**
  - 코드는 그대로 두고, `replay.py`/`envharness_p1.py`의 docstring과
    `tests/test_replay.py:80-94`의 테스트명·주석을 실제 동작(procedure는 형태 게이트,
    읽기 위치는 procedure 무관)에 맞게 정정 (별도 후보 PR, B 소유 파일).
  - U2 계약 문서(FD §1, code-plan §26)에 "procedure는 형태 게이트로만 사용"을 명시.
- **(b) 통합 중 유실로 확정 시**
  - `711466f`의 `_procedure_read_spec` 기반 읽기 위치 결정을 복원할지 CJ가 결정.
  - 복원 시 content 형태(dict snapshot ↔ row list)와의 정합을 함께 검토.

> 어느 경우든 **이 문서는 판단 요청까지**이며, 실제 코드·주석·테스트 수정은
> CJ 판단 이후 별도 PR로 진행합니다.
