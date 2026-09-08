# U2 조율 요청 (계약 gap 통지) — B → CJ / A

**작성일**: 2026-09-08 (기준 커밋 `7cbc856`)
**작성자**: B(한석훈, U2)
**상태**: **CJ 공통 의존성 구현 제공됨·반영(2026-09-08 3차, main `ef03b3a`+`cfc62e9` → work/u2-p1-git 병합)** — C-a/C-b/C-d의 **실제 구현이 main에 제공**되었다(제공 ① `ef03b3a` lifecycle 저장+descriptor export/import, 제공 ② `cfc62e9` 공유 usage 이벤트). **"구현 SHA 대기" 해소.** U2는 **실제 API 시그니처(bytes blob)에 gitsync/S3 정합** + 승인 Code Plan 범위 독립 구현 + stub만 진행, 실제 성공은 **실제 연동 통합 검증 후** 인정(미실행 **`NOT_RUN`**, 대역과 구분). **C-c(A)는 별도 조율 중 — 대기 유지.** **CJ 공통 계약 승인 ≠ U2 전체 구현 승인.**
**원칙**: 단일 수정자 준수 — 아래 파일은 소유자만 수정한다. U2는 **호출 계약**만 요청하며 직접 수정하지 않는다.

## CJ 공통 의존성 구현 제공됨(2026-09-08 3차 수신 — main `ef03b3a`+`cfc62e9`)
- **제공됨**: **① `ef03b3a` lifecycle 저장 + descriptor import/export**, **② `cfc62e9` 공유 usage 이벤트**. work/u2-p1-git에 병합 반영. **"구현 SHA 대기" 해소.**
1. **C-a(구현 제공됨 `ef03b3a`)**: S3의 상태 판단·변경 요청·조회는 **U2**, 실제 **저장·로드는 CJ `store` API** — `save_lifecycle_state(skill_ref{id,version,digest}, state, evidence)`/`load_lifecycle_state`/`list_lifecycle_records`(저장만·전이 미판단). U2 자체 lifecycle.json 저장 **미구현**. 상태는 정확한 `id/version/digest`에 연결.
2. **C-b(구현 제공됨 `ef03b3a`)**: `store.export_bundle(refs: list[dict]) -> bytes`(**exact refs 목록, scope 문자열 아님**)/`import_bundle(blob) -> list[PutResult]`. digest 검증·DEDUP/CONFLICT는 **store 처리**(U2 미구현). S3는 **공유 자격 판단한 정확한 후보만** `export_bundle([ref])` 연결.
3. **C-c(대기)**: A와 조율 중 — P1 검색 입력 **+ 파일접근 Skill 적용·검증 계약** 동반 확정 필요. **미구현 검색을 NO_MATCH로 간주 금지**, store 직접 조회 우회 **제거**. → **A 계약 대기**.
4. **C-d(구현 제공됨 `cfc62e9`)**: `usage.export_shared_usage() -> bytes`/`import_shared_usage(blob, local_ref_exists) -> list[dict]`. 저장·검증·dedup = **CJ**, **Git 전송·pull·last-sync 경계만 B**. 전송 시 **event_id 재발급 금지**(그대로 전송), pull 시 **정확한 로컬 Skill 존재 확인**(`local_ref_exists`) 연결.
5. **team-skill-store 최초 초기화 = B**(D-4). `main`과 분리된 공유 데이터 전용 경로.
- **진행 방침**: 실제 API(bytes blob) 시그니처에 S3/gitsync 정합 갱신, 승인 Code Plan 범위 독립 구현만. 테스트 대역 사용 가능하되 실제 공유 성공과 명확히 구분. **실제 연동 통합 검증 전까지 영속·공유 검증은 NOT_RUN.**

---

## → CJ 통지 (2건) — **구현 제공됨으로 해소**(main `ef03b3a`/`cfc62e9`)

### C-b · `store.py` — descriptor bundle 계약 **구현 제공됨** (`ef03b3a`)
- **현재(해소됨)**: `store.export_bundle(refs: list[dict]) -> bytes` / `import_bundle(blob: bytes) -> list[PutResult]` **구현 제공됨**. export는 **exact refs 허용목록**(scope 문자열 아님)으로 content만·3자 digest 일치 시만 포함, import는 digest 재계산·위조 거부·DEDUP/CONFLICT·content만(원격 문자열로 승인/Replay 미생성, AD-Q4).
- **U2 처리(우회 없음)**: 자체 저장·무결성·CONFLICT **우회 금지**. gitsync는 blob 전송만·S3는 `export_bundle([exact ref])` 연결. 실제 API(bytes)에 정합 완료. **실제 원격 import/pull·CONFLICT 왕복 실검증은 통합 검증까지 `NOT_RUN`**.

### C-d · `usage.py` — 공유 재사용 이벤트 계약 **구현 제공됨** (`cfc62e9`)
- **현재(해소됨)**: `usage.export_shared_usage() -> bytes`(VERIFIED_REUSE만) / `import_shared_usage(blob, local_ref_exists) -> list[dict]`(재검증·event_id dedup·로컬 존재 확인, counts 미변경) **구현 제공됨**. `compute_event_id`로 재전송 dedup 키 제공.
- **U2 처리(우회 없음)**: 이벤트 규격·검증·dedup·저장 = CJ. **Git 전송·pull·last-sync 경계만 B**, **event_id 재발급 금지**(그대로 전송), pull 시 `local_ref_exists`(store.get+digest 일치) 연결. **이벤트 공유 왕복 실검증은 통합 검증까지 `NOT_RUN`**.

---

## → A(최호길) 통지 (1건)

### C-c · `match.py` / `reuse_service.py` — P1 검색·적용 입력 일반화 (구현됨, 스텁 아님)
- **현재(정정, main `7256272`/`9dea075` 통합·실검증 완료)**: `search(obs: FailureObservation, store, budget_s=None) -> SearchOutcome`는 **결정적 매칭이 실구현**되어 있다(MATCH/NO_MATCH/ERROR/TIMEOUT/NOT_INVOKED 구분, `raise NotImplementedError` **아님** — 과거 "S7 스텁" 문구는 폐기). `reuse_service.apply_and_verify(selected, obs, env, run_id) -> ApplicationResult`도 실구현(pip 실제 설치·검증). **단 입력·검증이 P0(pip) 특화**: `FailureObservation{command,target_pkg,error_signature,exit_code}`, 검증은 `harness.TARGET_VERSION/TARGET_IMPORT` 기준(코드 주석 RU4=P1 확장 지점 명시).
- **U2 영향**: FR-P1-2(실제 검색 후에만 NO_MATCH 판정)를 A 계약으로 수행하려면 P1 problem 컨텍스트(파일접근 유형)를 받는 검색 입력 **일반화**가 필요(신규 구현이 아니라 기존 구현의 입력 규격 확장).
- **요청(계약 #4 일반화, 착수 여유 시)**:
  - `search`가 P1 problem 컨텍스트(예: `ProblemContext{kind:"file-access", signals:[...]}`)를 받거나, 시나리오 비의존 query 규격으로 일반화.
  - `check_applicability(candidate, problem) -> {applicable, matched_keywords, matched_conditions}`.
- **★ P1 파일접근 procedure 실행 함수 계약 — 모듈 경로·시그니처 확정(항목 1)**:
  - **모듈 경로**: `skillloop.envharness_p1.run_file_access_procedure` (**B 소유** `envharness_p1.py`에 배치·구현). 근거: Excel attach·mtime/sha256/Save 미호출 증거 수집은 P1 환경 도메인(B) 책임이며, A(S1 파일접근 분기)·B(C6 Replay)가 **동일 함수를 호출**한다. A는 이 계약으로 **호출부와 테스트를 병행 구현**한다(함수 본문은 B 제공).
  - **정확한 시그니처(파이썬 타입 확정)**:
    ```python
    # skillloop/envharness_p1.py (B 소유)
    @dataclass
    class EnvContext:
        xlsx_path: str
        app_open: bool          # 사용자가 암호로 열어둔 실행 중 Excel 존재 여부(harness 준비 사실)

    @dataclass
    class AccessResult:
        ok: bool                # 접근 성공 판정(강제 raise 아님)
        content: list | None    # 획득 행: [(month:str, total_output:int|float), ...] | 실패 시 None
        method: str             # 사용한 접근 방식 라벨(예: "excel-com-attach"|"direct-zip"|"none")
        evidence: dict          # {ran, mtime_before, mtime_after, sha256_before, sha256_after,
                                #  save_called: bool, error: str|None, app_open: bool, ...}

    def run_file_access_procedure(procedure: dict, env: EnvContext) -> AccessResult: ...
    ```
    - **입력**: `procedure` = 후보 `descriptor.procedure`(서술적 환경 접근 절차만; 스크립트·업무 계산·평문 암호 미포함), `env` = `EnvContext{xlsx_path, app_open}`(harness 준비 사실; 정답 대안 아님).
    - **접근 성공(ok=True) 기준**: (1) 원본 바이트 직접 파싱 아님·허용 경로로 `content` 획득, (2) `content`가 3개 완료월 `(month, total_output)` 포함, (3) 원본 `mtime`·`sha256` 무변경 & `Save` 계열 미호출(evidence로 입증). 실패/미충족 → `ok=False`(강제 raise 아님). Excel 미설치/미열림(`app_open=False`) → `ok=False, method="none"`(상위에서 `NOT_RUN` 매핑).
  - 확정 모델: 직접 접근=표준 zip 리더가 암호화본에서 `BadZipFile` 자연 실패, 허용 대안=실행 중 Excel attach 셀 읽기(§FD 1).
  - **Replay(C6) 공용**: `replay.py`는 이 함수를 **별도 실행 문맥에서 새로 호출**하고 최초 실행 결과를 재사용하지 않는다(§FD 4).
- **U2 처리(CJ 결정 3, 우회 없음)**: **미구현 검색을 NO_MATCH로 간주 금지**. store 직접 조회로 검색을 대체하는 **우회 제거**. A의 P1 검색 + 파일접근 적용·검증 계약이 서면 그 계약으로 연결. 확정 전 검색·파일접근 재사용 분기 **`NOT_RUN`**.
- **우선순위**: 중(P1 재사용 분기 정합). **A의 P0(S7/S8) 완성이 선행 우선순위임을 존중** — P1 일반화는 그 이후.

---

## → CJ 통지 — CLI 진입점 서비스 명세 (항목 2, `cli.py`=CJ 소유)

> `cli.py`는 **CJ 단일 수정자**다. U2는 `run-p1`/`store-init` 서브커맨드를 **직접 추가하지 않는다**. 대신 CJ가 연결할 **서비스 진입점(함수 경로)·인자 규격**을 아래로 확정한다(run-p0 배선과 대칭). B는 이 함수들을 소유 모듈에 실구현·테스트하고, CJ는 argparse 서브커맨드에서 호출만 하면 된다.

- **run-p1 오케스트레이션 진입점**
  ```python
  skillloop.experience_service.run_p1(
      xlsx_path: str | None = None,   # None이면 harness 합성 암호화본 준비 경로 사용
      store_path: str | None = None,  # None → run-p0와 동일 기본(.skillloop_demo/store.json)
      usage_path: str | None = None,  # None → 동일 기본(.skillloop_demo/usage.json)
      run_id: str | None = None,      # None이면 usage.new_execution_id()로 1회 발급(재시도 시 전달)
  ) -> int                            # 종료코드(run-p0와 동일 규약)
  ```
  흐름: 직접 접근 실패 관찰 → (검색: A 계약 대기 → NOT_RUN) → 환경 사실 → 허용 대안 attach → OLS 완료·검증 → 후보화 → 검토·독립 Replay·게시 시도. run-p0와 동일하게 `run_id`는 cli 발급·전달만.
- **team-skill-store 초기화 진입점(D-4)**
  ```python
  skillloop.gitsync.init_team_store(mirror_path: str | None = None) -> int
  # team-skill-store 전용 로컬 미러 준비(main 미오염). mirror_path None이면 기본 미러 경로.
  ```
- **(선택) 게시 파이프라인 세분 진입점** — CJ가 별도 서브커맨드를 원할 때만:
  ```python
  skillloop.publish_pipeline.review(candidate_ref: dict, decision: dict, store, ...) 
  skillloop.publish_pipeline.replay(candidate_ref: dict, env, store, ...) 
  skillloop.publish_pipeline.publish(candidate_ref: dict, store, gitsync, ...) 
  ```
  기본 데모는 `run_p1` 하나로 end-to-end 수행하므로 세분 진입점 배선은 필수 아님.
- **인자 규격 원칙**: 모든 경로 인자는 `None` 허용(run-p0 기본과 동일 디렉터리 규약). 반환은 종료코드(int). CLI 문자열·헬프 텍스트는 CJ 재량.

---

## 요약 (CJ 공통 의존성 구현 제공됨 반영 — 우회 없음)
| gap | 소유 / 상태 | U2 처리(우회 없음) | 통합 검증 전 NOT_RUN 항목 |
|---|---|---|---|
| C-a lifecycle 저장·로드 | CJ store — **구현 제공됨** (`ef03b3a`) | 판단·변경 요청·조회는 S3 단독, 저장·로드는 `save/load_lifecycle_state`·`list_lifecycle_records` 호출만(자체 lifecycle.json 미구현), 상태 exact ref 연결 | lifecycle 실제 영속(저장→재시작 로드) 연동 |
| C-b descriptor export/import | CJ store — **구현 제공됨** (`ef03b3a`) | digest 검증·DEDUP/CONFLICT는 store 처리, S3는 `export_bundle([exact ref])`만, gitsync는 blob 전송만 | 실제 import/pull·CONFLICT 왕복 검증 |
| C-c match P1 검색 + 파일접근 적용·검증 | A — **대기**(조율 중) | 미구현 검색 NO_MATCH 금지, 직접 조회 우회 제거 | 검색·파일접근 재사용 분기 |
| C-d usage 공유 이벤트 | CJ — **구현 제공됨** (`cfc62e9`) | 저장·검증·dedup=CJ, Git 전송·pull·last-sync 경계만 B, event_id 재발급 금지, `local_ref_exists` 연결 | 이벤트 공유 왕복 실검증 |

**공통**: C-a/C-b/C-d는 **실제 구현 제공됨**(main `ef03b3a`/`cfc62e9`, 병합 반영). **"구현 SHA 대기" 해소.** 단 **실제 연동 통합 검증 전**의 실제 저장·검증·공유 성공은 **NOT_RUN으로 정직 기록**(테스트 대역과 구분). C-c는 **A 대기 유지**. U2는 확보된 계약(1·3·5-자체정의) + 실제 API(bytes blob) 정합 독립 골격(gitsync 전송·S3 상태머신·exact 후보 `export_bundle`·`save_lifecycle_state` 영속·C6·C7-P1·S2 OLS) 위에서 승인 Code Plan 범위로만 착수한다. **자체 저장·무결성·CONFLICT·NO_MATCH 우회는 하지 않는다. CJ 공통 계약 승인 ≠ U2 전체 구현 승인.**
