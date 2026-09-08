# Code Generation Plan (Part 1) — P0 경로 (U0 P0 필수 + U1)

**단계**: CONSTRUCTION / Code Generation / Part 1 (Planning)
**작성일**: 2026-09-08
**상태**: **승인됨(2026-09-08, 정정 3건 반영)**. 이 계획이 Code Generation의 단일 기준. 승인된 문서·계약 스텁 커밋 및 origin/main push 승인됨.

> **승인 시 정정(반영 완료)**: (1) **S6를 앞으로 이동** — 기준 커밋 → S1 골격+최소 스텁 → **즉시 S6 커밋·push·공통 SHA 확정** → CJ S2~S5 / A S7~S8 **병렬** → S9. 스텁은 실제 구현·테스트 PASS로 기록하지 않음. (2) **run_id 전달 경로 계약화** — 새 논리 실행 시작 시 1회 발급한 run_id를 cli→S1→검증→C3까지 **전달**(S1 내부 재발급 금지, 재시도 시 기존 run_id 수신). (3) **커밋·소유 범위** — 최초 기준 커밋은 승인된 `aidlc-docs/`만 명시 stage(README·EVALUATION 자동 포함 금지), 스텁 커밋 전체 SHA·작업 경로를 A에게 전달 형태로 출력, `test_run_p0_e2e.py`=CJ 단일 수정자(A는 의견), A 인계 파일은 CJ 동시 수정 금지, 팀원 기존 미추적 자료 보존.
**목표**: 9/8 17:30 실제 샘플 실행(`run-p0`). Greenfield 단일 패키지.
**테스트**: pytest + Hypothesis(의존성 명시). **"네트워크 미의존" = 외부 인터넷 미의존**(로컬 파일 index만 사용).

> 추상 설명 최소화, **파일·호출 계약·명령** 우선. 기존 승인 결정은 재질문하지 않음.

---

## 프로젝트 구조 (Greenfield 단일 유닛, 워크스페이스 루트)
```
skillloop/                      # 애플리케이션 코드 (루트)
  __init__.py
  descriptor.py                 # C1  — CJ
  store.py                      # C2  — CJ
  usage.py                      # C3  — CJ  (카운트 쓰기 유일 주체)
  envharness_p0.py              # C7 P0 — CJ
  cli.py                        # C8  — CJ  (run-p0 오케스트레이션)
  match.py                      # C5  — A
  reuse_service.py              # S1  — A
tests/
  test_descriptor_pbt.py        # CJ (Hypothesis: V1,V2)
  test_store.py                 # CJ (V3,V4)
  test_usage.py                 # CJ (V9,V10,V11)
  test_match.py                 # A  (V5,V6)
  test_reuse_service.py         # A  (V7,V8)
  test_run_p0_e2e.py            # CJ+A (V12)
  fixtures/
    synthetic_pkg/              # 합성 배포 패키지 소스(빌드 대상) — CJ
    indexes/failing/            # 실패 index(대상 패키지 없음) — CJ
    indexes/allow/              # 허용 index(합성 패키지 wheel/sdist 존재) — CJ
pyproject.toml                  # 패키지 메타 + 콘솔 스크립트 `skillloop` — CJ
requirements-dev.txt            # pytest, hypothesis — CJ
README.md                       # 실행 방법·증거 링크(기존 파일 갱신)
```
- **단일 수정자 준수**: 위 소유자 외 편집 금지. 타 유닛은 호출 계약으로만 접근.

---

## 1. 생성·수정 파일 및 호출 계약 (CJ/U0 · A/U1)

### CJ / U0 (선행·공통)
**`descriptor.py` (C1)**
```python
@dataclass(frozen=True)
class Descriptor:
    id: str; version: str; digest: str
    origin: dict; applicability: dict; procedure: dict     # 불변 content
    actual_reuse: int = 0; demo_seed: bool = False          # 가변 usage
def canonical_json(content_wo_digest: dict) -> bytes         # 키정렬·정규화
def compute_digest(content_wo_digest: dict) -> str           # sha256 hex (digest·usage 제외)
def serialize(d: Descriptor) -> bytes                        # canonical
def deserialize(b: bytes) -> Descriptor                      # round-trip 동일 digest
```
**`store.py` (C2)** — *카운트 미기록*
```python
def get(id: str, version: str) -> Descriptor | None
def list() -> list[Descriptor]
def put(d: Descriptor) -> PutResult      # result: "STORED"|"DEDUP"|"CONFLICT", reason
# DEDUP은 usage 병합·actual_reuse 변경 없음. CONFLICT=동일(id,version)+다른 digest.
```
**`usage.py` (C3)** — *실제 재사용 기록의 유일한 쓰기 주체*
```python
def new_execution_id() -> str                    # 새 논리적 실행 시작 시 cli가 1회 호출(발급 지점)
def build_evidence(skill_ref, verification, run_id, demo_seed) -> ReuseEvidence
def record_actual_reuse(evidence) -> RecordResult
    # counted=True ⟺ is_real_success & !demo_seed & run_id 미기록(새 실행)
    # 동일 run_id 재기록(재검증/재시작) → counted=False, reason="same-execution"
def current_count(id: str, version: str) -> int
# 저장: 로컬 JSON. seen_run_ids(set) 영속화로 실행 단위 dedup.
# run_id 발급은 여기(new_execution_id)뿐. S1/검증은 발급하지 않고 전달만 받는다.
```
**`envharness_p0.py` (C7)**
```python
def prepare() -> None                 # failing/allow 두 index 준비(정답 강제 아님)
def setup_failing() -> EnvCtx         # 대상 패키지 없는 index
def setup_allow() -> EnvCtx           # 합성 패키지 있는 index (적용은 descriptor.procedure가 결정)
def make_clean_venv() -> EnvCtx       # 격리 venv 생성
def is_clean(env: EnvCtx, target_pkg: str) -> bool
```
**`cli.py` (C8)** — 진입점 `skillloop run-p0`
```python
def run_p0() -> int
    # run_id = usage.new_execution_id()               # 발급 지점(실행 시작 1회)
    # prepare → setup_failing → 실제 pip 실패 관찰 → match.search
    #  → MATCH: reuse_service.apply_and_verify(selected, obs, env, run_id)
    #     → 성공: usage.record_actual_reuse(build_evidence(..., run_id, ...)) → "reuse=N" 출력
    #  → NO_MATCH/ERROR/TIMEOUT/검증실패: 상태 출력(카운트 없음)
```

### A / U1 (병렬)
**`match.py` (C5)**
```python
@dataclass
class FailureObservation: command: str; target_pkg: str; error_signature: str; exit_code: int
def search(obs: FailureObservation, store) -> SearchOutcome
    # 유효 후보 = applicability.signals 만족. 다수면 안정정렬(적합도↓,version↓,id↑)+동점규칙→단일 MATCH+근거.
    # 유효 0건 → NO_MATCH. 내부오류/시간초과/미호출 → ERROR/TIMEOUT/NOT_INVOKED.
```
**`reuse_service.py` (S1)**
```python
@dataclass
class ApplicationResult: pip_exit_code:int; installed_check:bool; version_check:bool; import_check:bool; index_source:str; is_real_success:bool; run_id:str
def apply_and_verify(selected: Descriptor, obs, env, run_id: str) -> ApplicationResult
    # run_id는 호출자(cli)가 발급해 전달 — S1 내부 재발급 금지(재시도 시 동일 run_id 수신)
    # assert is_clean(env, obs.target_pkg)          # 오판 방지
    # cfg = selected.procedure                       # 적용 설정(index/옵션)은 절차에서 취득
    # execute pip install (cfg)  → 검증: exit0 & 설치 & 요구버전 & (합성)import
    # return ApplicationResult(..., run_id=run_id)   # 수신한 run_id 그대로 반영
```
**호출 계약 방향**: cli(CJ) → match/reuse_service(A) → usage/store/envharness(CJ). A는 CJ 계약을 **호출만**.

---

## 2. 합성 패키지 · mock index · 격리 Python 환경

- **합성 패키지**: `tests/fixtures/synthetic_pkg/` 에 무해한 배포 패키지(예: `skillloop_demo_pkg`, 단일 모듈 `import skillloop_demo_pkg`). 빌드 산출물(wheel/sdist)을 `indexes/allow/` 에만 배치.
- **mock index (외부 인터넷 미의존)**: 로컬 디렉터리 2개.
  - `indexes/failing/` : 대상 패키지 **없음** → `pip install` 실패 재현.
  - `indexes/allow/` : 합성 패키지 **있음** → 성공 가능.
  - pip 호출은 `--no-index --find-links <dir>` (또는 `file://` index-url)로 **로컬만** 사용, 외부 PyPI 접근 없음.
- **격리 Python**: 실행마다 `python -m venv <temp>` 로 clean venv 생성 → `is_clean`(대상 패키지 미설치) 확인 후 설치. 전역/기존 설치로 인한 오판 배제. **성공 index 선택 자체는 성공 근거 아님** — 실제 설치·버전·import로만 판정.
- 세부(정확한 pip 인자·venv 위치·빌드 방식)는 구현 시 이 계약 내에서 확정.

---

## 3. run_id 생성·재사용·저장 + C3 단독 카운트 경로

- **발급 지점 단일화**: 새 논리적 실행 시작 시 **cli(run_p0)가 `usage.new_execution_id()`를 1회 호출**해 발급. **S1·검증은 발급하지 않고 전달만 받는다**(모순 제거 — 정정 2).
- **전달 경로**: `run_p0(run_id)` → `apply_and_verify(..., run_id)` → `build_evidence(..., run_id, ...)` → `record_actual_reuse`.
- **재사용**: 동일 실행의 재검증·재시도·재시작은 **같은 run_id를 호출자가 전달**(새로 만들지 않음).
- **다른 환경 재사용**: 같은 문제라도 새 실행이므로 **새 run_id → 각각 +1**(입력 기반 dedup 금지).
- **저장·dedup**: `usage.py`가 로컬 JSON에 `seen_run_ids` 영속화. `record_actual_reuse`가 run_id 존재 여부로 실행 단위 dedup.
- **단독 카운트 경로**: 카운트 증가는 **오직 `usage.record_actual_reuse`**. `store.put`(C2)은 절대 usage/카운트 변경 없음. cli/reuse_service는 카운트를 직접 쓰지 않고 C3만 호출.

---

## 4. 샘플 실행 명령 · 예상 결과 · 필수 검증

**명령**
```bash
# 설치(개발)
pip install -e .
pip install -r requirements-dev.txt
# 샘플 실행 (P0 데모)
skillloop run-p0            # 또는: python -m skillloop run-p0
# 테스트
pytest -q                  # Hypothesis 포함
```
**예상 결과(run-p0)**
1. failing index로 `pip install <target>` → **실패 관찰**(비영점 종료코드).
2. `search` → **MATCH**(선택 근거 출력).
3. `apply_and_verify` → descriptor.procedure 기준 설치 → 검증(exit0 + 설치 + 요구버전 + 합성 import) → **is_real_success=true**.
4. `record_actual_reuse` → **`reuse=1`** 출력.
5. **동일 run_id 재검증 → 카운트 불변(reuse=1)**; **새 실행 재구동 → reuse=2**(idempotent 확인).

**필수 검증(진입 판단 기준, NFR V1~V12 매핑)**
- V1/V2 round-trip·digest 불변(Hypothesis), V3/V4 CONFLICT·DEDUP 카운트 무변경, V5/V6 검색 결정성·다중후보·오류 구분, V7/V8 실제 성공 정의·index 비강제, V9 카운트 C3 단독, V10 run_id 실행 dedup, V11 사전적재 실적 반영, **V12 run-p0 e2e 실제 샘플(17:30)**.
- 실행 증거(스크린샷·로그)는 Build and Test/제출 증거로 보존. 미검증 항목은 `NOT_RUN`.

---

## 5. 공통 기준 SHA · 팀원별 작업 경로 · 병렬 착수 순서

- **현재 HEAD**: `8308a65` (branch `main`). **⚠️ 그러나 `aidlc-docs/` 전체가 아직 미커밋(untracked)** — 승인된 설계·계약·본 계획이 baseline에 없음.
- **선행 조건(착수 전 필수)**: 승인된 aidlc-docs(합성·비민감)를 **커밋하여 공통 기준 커밋 생성** → 그 SHA를 팀 baseline으로 공유. (커밋/푸시는 **사용자 승인 후** 수행 — 자동 실행 안 함.)
- **작업 경로(단일 저장소, 단일 수정자)**:
  - CJ: `skillloop/{descriptor,store,usage,envharness_p0,cli}.py`, `tests/{test_descriptor_pbt,test_store,test_usage}.py`, `tests/fixtures/**`, `pyproject.toml`, `requirements-dev.txt`, **`tests/test_run_p0_e2e.py`(CJ 단일 수정자, A는 의견만)**.
  - A: `skillloop/{match,reuse_service}.py`, `tests/{test_match,test_reuse_service}.py`. **인계 후 CJ는 A 파일을 동시 수정하지 않음**.
- **병렬 착수 순서(정정 1 — S6 앞으로 이동)**
  1. **승인 문서 기준 커밋**: 승인된 `aidlc-docs/`만 명시 stage(README·EVALUATION 자동 포함 금지).
  2. **S1 골격 + 최소 타입·시그니처 스텁**(descriptor/store/usage/envharness_p0/match/reuse_service/cli의 dataclass·시그니처, 미구현부는 `NotImplementedError`).
  3. **즉시 S6 커밋·push(origin/main)·공통 SHA 확정** → 전체 SHA·작업 경로를 A에게 전달 형태로 출력. **이 시점이 U1 병렬 개시 게이트**. 스텁은 실제 구현·테스트 PASS로 기록하지 않음.
  4. **병렬**: CJ = S2~S5(직렬화·저장·카운트·envharness 실제 구현+테스트), A = S7~S8(match/reuse_service 실제 구현+테스트).
  5. 계약 안정 → S9 `run-p0` 통합·e2e → 17:30 샘플 실행 증거.
- 팀원 기존 미추적 자료 보존(기준 커밋에 무관한 파일 자동 stage 금지).

---

## Part 2 실행 단계 (승인 후 실행, 체크박스 — 정정 1 순서 반영)
- [ ] **S0. 승인 문서 기준 커밋**: `git add aidlc-docs/`(명시) → commit (README·EVALUATION 제외)
- [ ] **S1. 프로젝트 구조·의존성 + 최소 스텁** (CJ): `skillloop/` 골격, dataclass·시그니처 스텁(미구현부 NotImplementedError), `pyproject.toml`(콘솔 스크립트 `skillloop`), `requirements-dev.txt`(pytest, hypothesis), `tests/` 스캐폴딩
- [ ] **S6. 스텁 커밋·push·공통 SHA 확정(=U1 병렬 게이트)** (CJ): commit + `git push origin main` → 전체 SHA·작업 경로 A에게 전달 형태 출력. *(스텁=미구현, PASS 아님)*
- [ ] **S2. C1 descriptor.py + PBT** (CJ, 병렬) — V1,V2 · US-P0-1
- [ ] **S3. C2 store.py + tests** (CJ, 병렬) — V3,V4 · US-P0-1
- [ ] **S4. C3 usage.py + tests** (CJ, 병렬) — V9,V10,V11 · FR-USAGE-1·2
- [ ] **S5. envharness_p0 + 합성 패키지 + mock index + 격리 venv + tests** (CJ, 병렬) — V7 전제
- [ ] **S7. C5 match.py + tests** (A, 병렬) — V5,V6 · FR-MATCH
- [ ] **S8. S1 reuse_service.py + tests** (A, 병렬) — V7,V8 · FR-P0
- [ ] **S9. cli.py run-p0 오케스트레이션 + e2e(test_run_p0_e2e.py=CJ)** (CJ 주도, A 의견) — V12 · US-P0-1
- [ ] **S10. 코드 요약 문서** `aidlc-docs/construction/{U0-P0,U1}/code/` (markdown) + README 실행법·증거 링크
- [ ] 스토리(US-P0-1) 구현 완료 시 [x] 표기

**순서**: S0 기준 커밋 → S1 스텁 → **S6 즉시 커밋·push·SHA 확정(U1 게이트)** → CJ(S2~S5) ∥ A(S7~S8) 병렬 → S9 통합·17:30 실행 → S10 문서.

> 코드 작성은 **본 Code Plan 승인 + 공통 기준 커밋 SHA·작업 경로 확인** 후에만 시작.
