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

### C-c · `match.py` — P1 검색 query 미지원 + 스텁
- **현재**: `search(obs: FailureObservation, store) -> SearchOutcome`가 **pip 전용 형태**(target_pkg/error_signature/exit_code)이고 본문은 `raise NotImplementedError("S7")`. `check_applicability` 없음.
- **U2 영향**: FR-P1-2(실제 검색 후에만 NO_MATCH 판정)를 A 계약으로 수행하려면 P1 problem 컨텍스트(파일접근 유형)를 받는 검색이 필요.
- **요청(계약 #4 일반화, 착수 여유 시)**:
  - `search`가 P1 problem 컨텍스트(예: `ProblemContext{kind:"file-access", signals:[...]}`)를 받거나, 시나리오 비의존 query 규격으로 일반화.
  - `check_applicability(candidate, problem) -> {applicable, matched_keywords, matched_conditions}`.
- **U2 처리(CJ 결정 3, 우회 없음)**: **미구현 검색을 NO_MATCH로 간주 금지**. store 직접 조회로 검색을 대체하는 **우회 제거**. A의 P1 검색 + 파일접근 적용·검증 계약이 서면 그 계약으로 연결. 확정 전 검색·파일접근 재사용 분기 **`NOT_RUN`**.
- **우선순위**: 중(P1 재사용 분기 정합). **A의 P0(S7/S8) 완성이 선행 우선순위임을 존중** — P1 일반화는 그 이후.

---

## 요약 (CJ 공통 의존성 구현 제공됨 반영 — 우회 없음)
| gap | 소유 / 상태 | U2 처리(우회 없음) | 통합 검증 전 NOT_RUN 항목 |
|---|---|---|---|
| C-a lifecycle 저장·로드 | CJ store — **구현 제공됨** (`ef03b3a`) | 판단·변경 요청·조회는 S3 단독, 저장·로드는 `save/load_lifecycle_state`·`list_lifecycle_records` 호출만(자체 lifecycle.json 미구현), 상태 exact ref 연결 | lifecycle 실제 영속(저장→재시작 로드) 연동 |
| C-b descriptor export/import | CJ store — **구현 제공됨** (`ef03b3a`) | digest 검증·DEDUP/CONFLICT는 store 처리, S3는 `export_bundle([exact ref])`만, gitsync는 blob 전송만 | 실제 import/pull·CONFLICT 왕복 검증 |
| C-c match P1 검색 + 파일접근 적용·검증 | A — **대기**(조율 중) | 미구현 검색 NO_MATCH 금지, 직접 조회 우회 제거 | 검색·파일접근 재사용 분기 |
| C-d usage 공유 이벤트 | CJ — **구현 제공됨** (`cfc62e9`) | 저장·검증·dedup=CJ, Git 전송·pull·last-sync 경계만 B, event_id 재발급 금지, `local_ref_exists` 연결 | 이벤트 공유 왕복 실검증 |

**공통**: C-a/C-b/C-d는 **실제 구현 제공됨**(main `ef03b3a`/`cfc62e9`, 병합 반영). **"구현 SHA 대기" 해소.** 단 **실제 연동 통합 검증 전**의 실제 저장·검증·공유 성공은 **NOT_RUN으로 정직 기록**(테스트 대역과 구분). C-c는 **A 대기 유지**. U2는 확보된 계약(1·3·5-자체정의) + 실제 API(bytes blob) 정합 독립 골격(gitsync 전송·S3 상태머신·exact 후보 `export_bundle`·`save_lifecycle_state` 영속·C6·C7-P1·S2 OLS) 위에서 승인 Code Plan 범위로만 착수한다. **자체 저장·무결성·CONFLICT·NO_MATCH 우회는 하지 않는다. CJ 공통 계약 승인 ≠ U2 전체 구현 승인.**
