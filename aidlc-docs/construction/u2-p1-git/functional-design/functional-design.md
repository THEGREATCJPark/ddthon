# Functional Design (minimal) — U2 P1·후보화·게시·Git 전송

**단계**: CONSTRUCTION / Functional Design (per-unit) — Unit **U2** (담당: B 한석훈)
**깊이**: 최소(minimal)
**작성일**: 2026-09-08 (기준 커밋 `7cbc856`)
**근거**: 승인된 `requirements.md`, `stories.md`, `components.md`, `component-methods.md`, `services.md`, `unit-of-work*.md` + 사용자 결정 3종(2026-09-08T08:43:25Z)
**소유 파일**: `experience_service.py`(S2), `publish_pipeline.py`(S3), `replay.py`(C6), `envharness_p1.py`(C7-P1), `gitsync.py`(C4) + 대응 U2 테스트

> 이 문서는 U2의 **비즈니스 규칙·상태머신·계약 시그니처·검증 알고리즘**을 확정한다. 코드 파일·실행 명령·작업 순서는 후속 **Code Plan**에서 확정한다. HOW 중 UI/집계(U3)·재사용 검증 카운트(usage.py, CJ)는 범위 밖(호출만).

---

## 0. 확정된 진행 파라미터

> **개정 이력**: (1) 초안 D-1(U2 자체 lifecycle.json)은 **CJ FD 검토(2026-09-08)로 철회**되고 아래로 대체됨. D-2·D-3 유지. CJ 결정 5(team-skill-store 초기화=B) 추가. (2) **CJ 공통 의존성 방향 확정(2026-09-08 2차)** — C-a/C-b/C-d의 **호출 계약이 확정**되어 대기 표현을 "확정 계약 기준 연결 + 검증 commit SHA 대기"로 갱신. 제공 순서 **① lifecycle 저장 + descriptor import/export, ② 공유 usage 이벤트**. 이벤트 전송 시 **event_id 재발급 금지**(C-d). **C-c(P1 검색·파일접근 Skill 적용)는 A와 별도 조율 중 — 대기 유지**. CJ 공통 계약 승인 ≠ U2 전체 구현 승인.

- **D-1 (S3 lifecycle 영속) — CJ 구현 제공됨(SHA `ef03b3a`) 반영**: 이전 "U2 자체 `lifecycle.json` 영속" 결정은 **철회**된 상태를 유지한다. **구현 제공됨(C-a, main `ef03b3a`)**: 저장·로드는 CJ `store` API로 제공 — `save_lifecycle_state(skill_ref{id,version,digest}, state, evidence)` / `load_lifecycle_state(skill_ref)` / `list_lifecycle_records()`(저장만, 전이 미판단). **상태 전이 판단·변경 요청·조회 책임은 U2(S3)가 단독 유지**하고, **U2 자체 `lifecycle.json` 저장은 구현하지 않는다.** 상태·근거는 **정확한 `id`/`version`/`digest`에 연결**한다(store lifecycle 키=`id\x1fversion\x1fdigest`). → S3는 위 API에 연결한다. **"구현 SHA 대기"는 해소.** 단, **실제 연동(저장→재시작 로드→상태 정합) 통합 검증 전까지 영속 실검증은 `NOT_RUN`**으로 기록한다.
- **D-2 (Git 전송 구조)**: `gitsync.py`는 **team-skill-store 전용 로컬 미러 디렉터리**에서만 pull/push 한다. 현재 dev worktree·작업 브랜치(`work/u2-p1-git`)를 절대 오염시키지 않는다.
- **D-3 (push 불가 시)**: 실제 원격 push 인증이 불가하면 로컬 **SHAREABLE(LOCALLY_APPROVED)** 상태를 보존하고 **PUBLISH_PENDING**으로 둔다. 원격 push 검증은 **NOT_RUN**으로 정직 기록하며 **PUBLISHED로 보고하지 않는다**(FR-P1-7 / CON honesty).
- **D-4 (team-skill-store 초기화) — CJ 결정 5**: **team-skill-store branch 최초 초기화는 B(U2) 담당**이다. `main`과 **분리된 작업 경로**(D-2 전용 로컬 미러)에서 **공유 데이터 전용**으로 준비한다(합성·비민감 descriptor + 이벤트만; DB 파일·원본·secret 제외, FR-SYNC-5/NFR-SEC-1).
- **D-5 (P1 실패 모델 확정) — CJ 결정(2026-09-08, (가)안 수정 채택)**: **Office 암호화 합성 파일 + 실행 중 Excel read-only attach**로 확정(§1 상세). 사전조건=Excel 설치·실행 + 사용자 열람 + `pywin32`; **NFR-RUN-1의 P1 Excel 경로 한정 예외 승인**(P0·기타 범위 확대 금지). Excel 미설치 → `NOT_RUN`. **다른 제약 모델 탐색 종료**, 실증(암호화 실패/평문 성공/attach 읽기)을 설계 근거로 사용하고 반복하지 않는다. FR-P1-7 독립 Replay·게시 게이트는 **불변**.

---

## 1. C7-P1 — EnvHarness (`envharness_p1.py`) : 합성 환경 준비만

### 합성 실패 모델 (핵심 설계 결정 — **CJ 확정(2026-09-08), 실증 근거 반영**)

> **확정 모델**: "**Office 암호화 합성 파일 + 실행 중인 Excel에 대한 허용 read-only attach**". (가)안 수정 채택. 이전 후보(텍스트/비-ZIP 파서 교정, 쓰기 금지 read-only 표면)는 모두 **폐기**된다. 아래 실증으로 성립을 확인했고 **동일 실증을 반복하지 않는다.**
>
> **실증 근거(설계 기반)**: 암호화본 3종(openpyxl/pandas/zipfile) 직접 접근 **자연 실패**(openpyxl/zipfile=`BadZipFile: File is not a zip file`, 강제 raise 아님) / **평문 대조군 동일 호출 전부 성공**(⇒ 실패 원인=API가 아니라 환경) / **실행 중 Excel attach로 셀 값 획득**(원본과 일치, 원본 mtime·hash 무변경, Save 미호출).

**모델 구성**
- **합성 제약(암호화)**: 정상 데이터를 담은 워크북을 **Excel open password로 암호화 저장**한다(FileFormat=51, Password=…). 결과 바이트는 **OLE-CFB 암호화 컨테이너**(`D0 CF 11 E0 …`)이며 **OOXML zip이 아니다**. 제약은 "환경이 만든 암호화 상태"이며 파일 손상이 아니다.
- **환경 사실(사전조건)**: Excel **설치·실행** + **사용자가 그 파일을 (암호로) 열어둔 상태**. **암호는 사용자만 안다**(harness·Agent·후보 절차에 평문 암호를 넣지 않는다).
- **직접 접근이 실패하는 이유**: 표준 XLSX 리더(openpyxl/pandas/zipfile)는 파일을 **zip으로 해석**한다. 암호화본은 zip이 아니므로 리더가 **스스로 `BadZipFile`을 낸다**(잘못된 API 선택·강제 raise 아님).
- **허용 대안이 가능한 이유**: 파일 바이트를 직접 열지 않고, 사용자가 **이미 열어 둔 실행 중 Excel 인스턴스에 attach**(`GetActiveObject`)해 **셀 값만 read-only로** 읽는다. 애플리케이션이 이미 복호화한 문서를 매개하므로 성공한다. 어느 대안이 허용되는지는 harness가 알려주지 않으며 **Agent가 탐색·선택·실행**한다(제품 흐름에서 자동 정답 선택 없음).

**필요 의존성·경계 (FD/NFR 확정 — Code Plan 이월 아님)**
- **의존성**: `pywin32`(win32com) + **Excel 설치·실행**. **NFR-RUN-1의 P1 Excel 경로 한정 예외 승인됨**(P0·그 외 범위 확대 금지). `msoffcrypto-tool`·`xlwings`는 현재 미설치(대안 아님).
- **Excel 미설치 → 이 P1 경로 `NOT_RUN`**(무결성·게시 게이트 불변, FR-P1-7).
- **읽기 전용**: attach 경로는 **Save 계열 호출을 하지 않고** 원본 파일을 수정하지 않는다(NFR-SEC-2). DRM 실제 우회 없음 — 사용자가 정당하게 열어둔 세션을 통해 값만 읽는다.
- Code Plan은 구현 세부(attach 재시도·워크북 매칭·셀 범위 읽기 정확한 호출)만 확정한다.

### 계약 시그니처
```
setup_encrypted_open_xlsx_env(data_rows, password) -> XlsxEnv
    # 정상 데이터를 Excel(COM)로 암호화 저장 + 사용자 열람 상태(실행 중 Excel)를 "준비"만 한다.
    # 정답 대안(attach) 미공급. password는 사전조건 소유자(사용자) 것이며 Agent/후보에 넘기지 않는다.
    # XlsxEnv = {xlsx_path, app_running: bool, present_facts{file_state:"office-encrypted", app_open:true}}
teardown() -> None      # 열어둔 Excel/워크북 정리, 원본 미변경 확인

# C7↔Agent 관찰 계약 (강제 raise 아님 — 표준 리더를 실제 실행하고 결과만 관찰)
attempt_direct_access(path) -> DirectAccessObservation
    # 표준 XLSX 리더(zip 기반)를 실제 실행. 암호화본이라 리더가 스스로 실패.
    # DirectAccessObservation = {ran: bool, ok: bool, error: str|None, evidence: dict}
    # 실증: ok=False, error="BadZipFile: File is not a zip file" (관찰된 환경 실패, FR-P1-1).
```
- **경계 규칙**: `attempt_direct_access`는 표준 리더를 실제 실행하고 결과만 관찰한다(대안 미제시). 대안 탐색·attach 코드 작성·실행은 harness 책임 아님(Agent 책임). 평문 업무 내용을 성공 결과로 미리 주지 않는다. 합성·비민감 데이터만(CON-1), 승인 세션을 통한 read-only만(NFR-SEC-2).

### ★ A 전달용 — procedure 실행 함수 계약 (파일접근 유형 재사용, C-c 일부)
> S1(A 소유)이 파일접근 유형 후보 절차를 실행·검증할 때의 입출력·성공 기준. Replay(C6)도 동일 계약으로 재수행한다.
```
run_file_access_procedure(procedure: dict, env: EnvContext) -> AccessResult
    # 입력:
    #   procedure = 후보 descriptor.procedure (서술적 환경 접근 절차만; 스크립트·업무 계산·암호 미포함)
    #   env       = {xlsx_path, app_open: bool}  (harness가 준비한 사전조건 사실; 정답 대안 아님)
    # 출력:
    #   AccessResult = {ok: bool, content: <획득 셀 값/행들>|None, method: str, evidence: dict}
    # 접근 성공 기준(ok=True):
    #   (1) 원본 파일 바이트를 직접 파싱하지 않고(직접 접근 실패 대상), 허용 경로로 content를 획득
    #   (2) content가 대상 3개 완료월 (month,total_output) 행을 포함
    #   (3) 원본 파일 mtime·sha256 무변경 & Save 계열 호출 없음(read-only 증거)
    #   실패/미충족 → ok=False (강제 raise로 성공/실패를 연출하지 않음)
```
- Replay는 이 함수를 **별도 실행 문맥에서 새로 호출**하고, **최초 실행의 content/판정을 재사용하지 않는다**(§4 C6). `evidence`에 method·mtime/hash 비교·Save 미호출을 남긴다.

---

## 2. S2 — ExperienceService (`experience_service.py`) : P1 업무 완료 + 후보화

### 흐름 (services.md run_p1 정합)
```
run_p1(xlsx):
  1. obs = EnvHarness.attempt_direct_access(xlsx)        # 표준 zip 리더 실제 실행 → 암호화본 BadZipFile 실패 관찰 (FR-P1-1)
  2. outcome = SkillSearchMatcher.search(problem)        # 실제 검색·범위/질의/결과 기록 (FR-P1-2)
       - status in {ERROR, TIMEOUT, NOT_INVOKED} → 별도 오류 상태(≠ NO_MATCH)  (FR-P1-2)
       - applicable 파일접근 후보 존재:
            r = S1.apply_and_verify(match, problem)       # ★ 파일접근 유형 재사용(pip 흐름 아님, A 계약 호출만)
            if r.is_real_success: usage.record_actual_reuse(build_evidence(..., run_id, ...))  # C3 경유
            content = 재사용으로 획득한 파일 내용;  reused = True
       - else NO_MATCH → 3~4 Agent 탐색
  3. facts = ask_environment_facts(user)                 # 대화형 (FR-P1-3)
  4. (NO_MATCH) Agent가 허용 read-only 대안 탐색·선택·실행 → 실행 중 Excel attach로 content 획득 (FR-P1-4, run_file_access_procedure)
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
   if not gate: state=BLOCKED; store.save_lifecycle_state(ref, "BLOCKED", evidence); return
   store.put(candidate)                       # C2, 무결성/dedup. 성공 시 state=LOCALLY_APPROVED(=SHAREABLE)
   store.save_lifecycle_state(ref, "LOCALLY_APPROVED", evidence)   # C-a: S3 판정 상태 영속(저장만)
   bundle = store.export_bundle([ref])        # ★ C-b: exact refs 목록(scope 문자열 아님) — S3가 공유 자격 판정한 정확한 후보만
   res = GitSyncAdapter.push_descriptors(bundle)   # D-2 미러, D-3 처리
   state = PUBLISHED if res.ok else PUBLISH_PENDING           # ok=False면 PUBLISHED 미보고
   store.save_lifecycle_state(ref, state, {**evidence, "remote": res})   # 원격 결과 반영
```

### 읽기전용 상태 조회 계약 (계약 #7 — U2 소유, U3가 소비)
```
query_lifecycle_state(candidate_ref{id,version,digest}) -> LifecycleState   # 읽기 전용
list_lifecycle_states(filter) -> list[LifecycleState]                        # 읽기 전용
# LifecycleState = {ref, state, local_review_evidence, remote_publish_evidence}
```
- U3(C10)는 이 계약으로만 상태를 조회한다. **상태 추정·게이트 재구현 금지**(AD-Q4).
- **원격 게시본 구분**: import로 받은 게시본은 `remote_publish_evidence`(원격 근거)와 `local_review_evidence`(수신 환경 검토)를 **분리**한다. 로컬 검토 없으면 "원격 게시(타 환경 근거)"로만 표시, **수신 환경의 승인·Replay 기록을 만들지 않는다**.
- **영속: D-1(구현 제공됨, `ef03b3a`)** — lifecycle 저장·로드는 CJ `store` API(`save_lifecycle_state`/`load_lifecycle_state`/`list_lifecycle_records`, 저장만·전이 미판단). **상태 전이 판단·변경 요청·읽기전용 조회는 S3(U2) 단독 유지**(자체 파일 저장 없음, 상태는 exact `id/version/digest` 연결). 읽기전용 조회 계약(#7)은 `load_lifecycle_state`/`list_lifecycle_records`를 감싸 원격/로컬 근거를 분리 반환한다. **"구현 SHA 대기" 해소 — 실제 연동 통합 검증 전까지 영속 실검증은 `NOT_RUN`.**

---

## 4. C6 — ReplayVerifier (`replay.py`) : 독립 Replay

```
replay(candidate: Descriptor, env: EnvContext) -> ReplayResult
# ReplayResult = {verdict: PASS|FAIL|NOT_RUN, candidate_ref:{id,version,digest}, evidence: dict}
```
- **독립 실행**: candidate의 **환경 접근 절차**를 EnvHarness가 준비한 P1 합성 환경(암호화 파일 + 실행 중 Excel)에 **별도 실행 문맥에서 `run_file_access_procedure`로 새로 재수행**해 실제 효과(셀 내용 획득 = ACCESS_EFFECT)를 확인 → verdict 산출. **최초 실행의 artifact·획득 값·성공 판정을 재사용하지 않는다.** 사용자가 파일을 열어두는 것은 **환경 준비**이며 Replay 대상이 아니다.
- **환경 미준비(Excel 미설치/미열림) → `NOT_RUN`**(게시 금지). verdict는 화면 문구가 아닌 **실제 효과** 기반(NFR-TEST-2). `candidate_ref.digest`는 게이트 동일성 확인에 사용.
- 계약 5(ReplayResult + 게이트 입력 규격)는 U0 프리즈가 없으므로 **U2가 `replay.py`에서 정의**하고 S3가 소비.

---

## 5. C4 — GitSyncAdapter (`gitsync.py`) : 전송 전담 (B 단일 수정자)

### 대상·구조 (D-2, D-4)
- 대상: 동일 저장소 `THEGREATCJPark/ddthon`의 **`team-skill-store` branch**. **전용 로컬 미러 dir**에서만 조작.
- **최초 초기화(D-4)**: team-skill-store branch 준비는 **B 담당**. `main`과 분리된 전용 경로에서 공유 데이터 전용으로 초기화.
- 전송 내용: **공유 가능한 descriptor + 비민감 재사용 이벤트 레코드**만. **로컬 DB 파일(store.json/usage.json 등) 자체는 전송하지 않는다**(FR-SYNC-5).
- bundle은 미러 작업트리에 **파일로 직렬화**(descriptor JSON / 이벤트 JSON) 후 commit·push.

### 계약 시그니처
> 실제 CJ API 정합(main `ef03b3a`/`cfc62e9`): `store.export_bundle(refs: list[dict]) -> bytes`, `store.import_bundle(blob: bytes) -> list[PutResult]`, `usage.export_shared_usage() -> bytes`, `usage.import_shared_usage(blob: bytes, local_ref_exists) -> list[dict]`. **모두 bytes(blob) 전송** — gitsync는 이 blob을 미러 파일로 쓰고 commit·push/pull만 한다.
```
pull() -> SyncResult
    # 원격 branch → 로컬 미러. descriptor blob은 store.import_bundle(blob),
    # 이벤트 blob은 usage.import_shared_usage(blob, local_ref_exists) 경유(검증·dedup·존재확인 위임).
    #   local_ref_exists(ref{id,version,digest}) := (store.get(id,version)가 존재 & digest 일치)  ← 정확한 로컬 Skill 존재 확인 연결
push_descriptors(bundle: bytes) -> SyncResult
    # 로컬 → 원격. bundle = store.export_bundle([exact refs]) 결과(bytes). S3.publish가 사용.
push_shared_usage(usage_bundle: bytes) -> SyncResult
    # 로컬 → 원격. usage_bundle = usage.export_shared_usage() 결과(bytes, VERIFIED_REUSE만). ★ 게시와 독립 경로.
last_sync() -> SyncMeta        # {synced_at, branch_revision, queryable_range} (FR-ORG-5)
status() -> SyncStatus
# SyncResult = {ok, retryable, error}
```
- **경계**: 무결성·CONFLICT·dedup·저장은 **store**(CJ), 공유 이벤트 규격·검증·event_id dedup·저장은 **usage.py**(CJ)에 위임. gitsync는 **전송만**. 승인·게시 lifecycle 미구현(S3 책임). 원격 상태 문자열만으로 로컬 승인/Replay/실적 생성 안 함(AD-Q4).
- **export 대상 한정(C-b 확정)**: descriptor export/import는 **CJ 제공**. digest 검증·DEDUP/CONFLICT는 **store에서 처리**하므로 U2에서 별도 구현하지 않는다. **S3는 공유 자격(SHAREABLE)을 판단한 정확한 후보만** `export`하도록 연결한다(게이트 통과 exact `{id,version,digest}`만).
- **event_id 보존(C-d 확정)**: 이벤트 전송 시 gitsync는 **`event_id`를 새로 발급하지 않는다**. usage.py(CJ)가 발급·검증·dedup한 이벤트 레코드를 **그대로 전송**만 한다. Git 전송·`pull`·`last_sync` 경계는 U2 유지.
- **D-3**: `push_*`가 `ok=False`면 로컬 상태 미변경, `retryable`/`error` 보존. S3는 PUBLISH_PENDING 유지. 실제 원격 push 인증 불가 시 push 검증 **NOT_RUN**.
- **게시 vs 이벤트 공유 독립**: `push_descriptors`(SHAREABLE descriptor)와 `push_shared_usage`(VERIFIED_REUSE 이벤트)는 별개 경로. 새 Skill을 게시하지 않아도 실적 이벤트 공유 가능.
- **구현 제공됨 기준 개발 규칙(CJ C-b/C-d, main `ef03b3a`/`cfc62e9`)**: `store` export/import(C-b)와 `usage` 공유 이벤트(C-d)의 **실제 구현이 main에 제공**되었다(제공 ① `ef03b3a` lifecycle 저장+descriptor export/import, 제공 ② `cfc62e9` 공유 usage 이벤트). U2는 **실제 API 시그니처(bytes blob)에 gitsync를 정합**하고 **승인된 Code Plan 범위의 독립 구현 + 테스트 대역(stub)**만 진행한다. **U2는 자체 저장·무결성·CONFLICT·dedup으로 우회하지 않는다**(모두 store/usage 위임). **"구현 SHA 대기" 해소.** 테스트 대역은 **실제 공유 성공과 명확히 구분**하며, **실제 원격 pull/import·이벤트 공유 왕복 통합 검증 전까지 실검증은 `NOT_RUN`**. **CJ 공통 계약 승인 ≠ U2 전체 구현 승인.**

---

## 6. CJ/A 조율 계약 대기 (CJ 검토 반영 — 우회안 제거)

> **CJ 공통 의존성 구현 제공됨(2026-09-08, main `ef03b3a`+`cfc62e9`) 반영**: C-a/C-b/C-d의 **실제 구현이 main에 병합·제공**되었다(work/u2-p1-git에 병합 반영). U2는 **실제 API 시그니처에 gitsync/S3를 정합**하고 **승인 Code Plan 범위 독립 구현 + 테스트 대역(stub)**만 진행한다. **"구현 SHA 대기" 해소.** 단 실제 저장·검증·공유 성공은 **실제 연동 통합 검증 후**에만 인정(미실행 **`NOT_RUN`**, 대역과 구분). **C-c(A)는 별도 조율 중 — 대기 유지.** **CJ 공통 계약 승인 ≠ U2 전체 구현 승인.**

| # | 계약 | 소유 / 상태 | U2 처리(우회 없음) | 통합 검증 전 NOT_RUN 항목 |
|---|---|---|---|---|
| C-a | lifecycle **저장·로드** | **CJ store — 구현 제공됨** (`ef03b3a`) | 상태 판단·변경 요청·읽기전용 조회는 **S3(U2) 단독**. 저장·로드는 `save/load_lifecycle_state`·`list_lifecycle_records` 호출만(자체 lifecycle.json 미구현). 상태는 exact `id/version/digest`에 연결 | lifecycle 실제 영속(저장→재시작 로드) 연동 |
| C-b | descriptor **export/import** | **CJ store — 구현 제공됨** (`ef03b3a`) | digest 검증·DEDUP/CONFLICT는 **store 처리**(U2 미구현). S3는 `export_bundle([exact refs])`로 **공유 자격 판단한 정확한 후보만** 전달. gitsync는 blob 전송만 | 실제 import/pull·CONFLICT 검증 |
| C-c | `match.search` P1 입력 **+ 파일접근 Skill 적용·검증** | **A — 조율 중(대기)** | **미구현 검색을 NO_MATCH로 간주 금지**. store 직접 조회 우회 **제거**. A 계약 대기 | 검색·파일접근 재사용 분기 |
| C-d | 공유 이벤트 규격·검증·dedup·**저장** | **CJ usage — 구현 제공됨** (`cfc62e9`) | 저장·검증·dedup=CJ(`export_shared_usage`/`import_shared_usage(blob, local_ref_exists)`). **Git 전송·pull·last-sync 경계만 B**, **event_id 재발급 금지**(그대로 전송), pull 시 **정확한 로컬 Skill 존재 확인 연결** | 이벤트 공유 왕복 실검증 |

**이미 확보**: 계약 1(descriptor digest/serialize) ✅, 계약 3 카운트(record_actual_reuse/build_evidence/new_execution_id) ✅. 계약 5(ReplayResult)는 U2 정의. **C-a/C-b/C-d 구현 제공됨** ✅(통합 실검증 대기).
**독립 구현 가능(통합 실검증 전, 실제 API·stub 기준)**: gitsync 전송 골격(push_descriptors/push_shared_usage/pull/last_sync, blob 전송·event_id 보존·local_ref_exists 연결), S3 상태머신·게이트·읽기전용 조회 계약(#7)·exact 후보 `export_bundle` 연결·`save_lifecycle_state` 영속, C6 Replay, C7-P1 read-only 제약 harness, S2 OLS·후보화(계산·표시 로직). **C-c 관련 검색·파일접근 재사용 분기는 제외(A 대기).**

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

## 9. 미해결·NOT_RUN 예정 항목 (정직 기록 — CJ 구현 제공됨 + P1 모델 확정 반영)
- **P1 실패 모델 실증 근거(≠ NOT_RUN, 설계 확정 근거)**: 암호화본 직접 접근 자연 실패 / 평문 대조군 성공 / Excel attach 읽기·원본 무변경을 **실증 완료**(2026-09-08). 이는 확정 모델의 설계 근거로 사용한다.
- **P1 Excel 경로 NOT_RUN 조건**: **Excel 미설치/미열림 환경**에서는 직접실패→attach 대안·OLS 완료·후보·Replay 경로를 **`NOT_RUN`**으로 표시(NFR-RUN-1 P1 한정 예외, 게시 게이트 불변).
- **독립 Replay 실검증 NOT_RUN**: `run_file_access_procedure` 기반 C6 독립 Replay는 **구현 후 실제 검증** 예정(현재 미구현 → NOT_RUN).
- **실패 실행 근거(≠ NOT_RUN)**: 최초 `git push`(작업 브랜치)는 **403으로 실제 실패** → 이는 시도한 실패의 실행 근거로 보존한다. 이후 권한 해결로 push 성공. 이와 별개로 **제품 원격 게시(team-skill-store) 성공 도달 + pull 왕복**은 아직 **NOT_RUN**(D-3).
- C-a/C-b/C-d는 **구현 제공됨**(main `ef03b3a`/`cfc62e9`, 병합 반영). "구현 SHA 대기" 해소. 단 **실제 연동 통합 검증 전까지** 아래는 **NOT_RUN**(테스트 대역과 실제 성공 구분):
  - **C-a**: lifecycle 실제 저장→재시작 로드→상태 정합 영속 통합(자체 lifecycle.json 미구현, 판단·전이는 S3 유지).
  - **C-b**: descriptor 실제 원격 import/pull·CONFLICT 왕복 검증(digest·DEDUP/CONFLICT는 store 처리, S3는 `export_bundle([exact refs])`만).
  - **C-d**: 이벤트 공유 왕복 실검증(event_id 재발급 없이 전송, pull 시 정확한 로컬 Skill 존재 확인 연결, 저장·검증·dedup=CJ).
- **C-c(A 대기 유지)**: `match.search` P1 입력 + 파일접근 적용·검증 계약 확정 전 **검색·파일접근 재사용 분기는 NOT_RUN**(미구현 검색을 NO_MATCH로 간주 금지).
- **CJ 공통 계약 승인 ≠ U2 전체 구현 승인** — U2 구현은 승인된 Code Plan 범위로 한정.

## Current contract correction — scenario continuation
The approved `construction/plans/p1-scenario-correction-plan.md` supersedes earlier task-specific access schema in this document. Shared procedure contains only action=file-access and method=excel-com-attach. C7/S1/C6 validate workbook accessibility and read-only evidence (workbook_readable), independent of production rows. C7 returns a local workbook snapshot preserving sheet names and UsedRange origins. S2 receives a separate local task mapping, interprets current columns/rows, verifies OLS and creates the actual3+forecast1 PNG. No task schema, chart or content is shared. S3 owns reuse eligibility as well as publication state; explicit execution confirmation does not replace integrity or lifecycle eligibility. CJ now integrates A/B completed handoffs; original authors and prior validation are preserved.

## Approved implementation alignment — operator/org Cold

See construction/plans/operator-open-org-cold-code-generation-plan.md, approved 2026-09-09. Operator open/activate uses public fixture password outside Agent workspace; exact full path identifies the workbook across Excel instances. Preparation never counts as discovery or Replay. Git context binds explicit remote/branch/mirror, preserving legacy default; new live branch starts P0-only. C6 supports action-specific pip install/version/import evidence and file read-only evidence; S3 retains exact review+fresh Replay+confirmed push gates. Claude Code conversational review records the actual user response and exact candidate; no native GUI or automatic yes; candidate completion invites user approval proactively. Technical prerequisites remain Windows Excel/pywin32, Python venv/pip and authenticated Git for remote transport. Local workflow remains offline except Git sync. PBT partial scope and existing security/resiliency requirements unchanged.
