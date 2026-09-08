# P0 통합 준비 체크리스트 — A(S7/S8) 코드 수신 후

**단계**: CONSTRUCTION / Code Generation / Part 2 / 통합
**작성일**: 2026-09-08
**목적**: A의 `match.py`(C5)·`reuse_service.py`(S1) 수신 시 결정적으로 통합·검증. **파일 존재만으로 완료 처리 금지** — 실제 설치·검증·카운트 결과를 확인한다.

## 현재 상태(A 인계 전)
- CJ P0 모듈(C1/C2/C3/C7 + cli 오케스트레이션) 구현·검증 완료: **19 PASS**.
- `python -m skillloop run-p0`: clean venv + failing index 실제 pip 실패 관찰(exit=1)까지 동작 → `match.search`(A 스텁)에서 정지.
- e2e 본문(`tests/test_run_p0_e2e.py`, CJ 단일 수정자) 준비 완료, **SKIP 유지**.
- 부분 검증: **19 PASS / 8 SKIP**(match 3 · reuse_service 2 · e2e 3).

## A가 채워야 할 계약(변경 불가 시그니처)
- `match.search(obs, store) -> SearchOutcome`
  - 유효 후보 = `applicability.signals`가 `obs.error_signature`와 결정적 매칭.
  - 데모 신호: `"pip-install-fail:skillloop-demo-pkg"` (cli가 생성하는 `error_signature`).
  - 다수 후보 → 안정 정렬+동점규칙으로 단일 MATCH+근거. 0건 → NO_MATCH. 내부오류/시간초과/미호출은 ERROR/TIMEOUT/NOT_INVOKED.
- `reuse_service.apply_and_verify(selected, obs, env, run_id) -> ApplicationResult`
  - `run_id` 재발급 금지(전달만). `assert envharness_p0.is_clean(env, obs.target_pkg)`.
  - `cfg = selected.procedure` → `index=cfg["index"]`("allow"), `target=cfg["target"]`.
  - `index_dir = envharness_p0.resolve_index(cfg["index"])` → `env.python_exe -m pip install --no-index --find-links <index_dir> <target>`.
  - 검증(모두 참이어야 `is_real_success=True`): pip exit0 & 설치 확인 & 요구버전(1.0.0) & `env.python_exe -c "import skillloop_demo_pkg"` 성공.
  - `index_source` = 실제 사용한 index dir. **성공 index 선택 자체는 성공 근거 아님** — 위 검증으로만 판정.

## 통합·검증 절차(수신 후 순서대로)
1. A의 `skillloop/match.py`·`skillloop/reuse_service.py`를 수신(merge). **CJ는 A 파일 본문을 수정하지 않음**(계약 위반 시에만 의견 제시).
2. A 소유 테스트 skip 해제: `tests/test_match.py`, `tests/test_reuse_service.py`의 `pytestmark` 제거.
3. `tests/test_run_p0_e2e.py`(CJ)의 `pytestmark` 제거.
4. 실행: `pip install -r requirements-dev.txt` → `pytest -q`.
   - **완료 기준**: match(V5·V6)·reuse_service(V7·V8)·e2e(V12) 실제 PASS. 27 PASS 기대(현 19 + 8 unskip).
5. 실제 데모: `python -m skillloop run-p0` 2회.
   - 1회차: `pip install 실패 관찰` → `MATCH ...` → `reuse=1 (counted=True, reason=ok)`.
   - 2회차(새 실행): `reuse=2`.
   - (동일 run_id 재시작은 e2e가 카운트 불변 확인.)
6. 실제 출력·`pytest` 요약을 증거로 기록(스크린샷/로그). 미검증 항목은 계속 `NOT_RUN`.

## 완료 처리 금지 조건(실제 결과 확인 전)
- 파일이 존재하지만 `is_real_success`가 검증되지 않으면 V7/V12 = NOT_RUN 유지.
- `pip exit0`만으로 성공 처리 금지(설치·버전·import까지 확인).
- e2e가 SKIP이거나 count assert 미확인이면 V12 = NOT_RUN 유지.
