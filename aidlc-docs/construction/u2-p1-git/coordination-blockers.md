# U2 조율 요청 (계약 gap 통지) — B → CJ / A

**작성일**: 2026-09-08 (기준 커밋 `7cbc856`)
**작성자**: B(한석훈, U2)
**상태**: **CJ FD 검토 답변 수신·반영(2026-09-08)** — 초안의 U2 자체 우회안은 **모두 제거**. 계약은 소유자(CJ/A)가 제공하고, U2는 계약에 맞춰 **호출 연결 + 테스트 대역(stub) 병행 개발**만 한다. 미실행 실검증은 **`NOT_RUN`**.
**원칙**: 단일 수정자 준수 — 아래 파일은 소유자만 수정한다. U2는 **호출 계약**만 요청하며 직접 수정하지 않는다.

## CJ 결정 요약(2026-09-08 수신)
1. **C-a**: lifecycle 저장 책임은 CJ가 `SkillStore`로 정합화. S3의 상태 판단·게이트·읽기전용 조회는 U2 유지. → **CJ 계약 대기**(자체 파일 저장 우회 금지).
2. **C-b**: CJ가 import/export **우선 제공**. U2 자체 저장·무결성·CONFLICT **우회 금지**. gitsync 전송은 계약 stub로 병행, 실제 import/pull 검증과 구분(미실행 NOT_RUN).
3. **C-c**: A와 조율 중 — P1 검색 입력 **+ 파일접근 Skill 적용·검증 계약** 동반 확정. **미구현 검색을 NO_MATCH로 간주 금지**, store 직접 조회 우회 **제거**. → **A 계약 대기**.
4. **C-d**: 이벤트 규격·검증·dedup·저장 = CJ, **Git 전송 경계만 B**. 전송 개발 병행 가능.
5. **team-skill-store 최초 초기화 = B**(D-4). `main`과 분리된 공유 데이터 전용 경로.

---

## → CJ 통지 (2건)

### C-b · `store.py` — descriptor bundle 계약 부재
- **현재**: `store.py`에 `get/list/put`(STORED/DEDUP/CONFLICT)만 존재. `export_bundle(scope=SHAREABLE)` / `import_bundle(bundle)` **없음**.
- **U2 영향**: S3.publish의 원격 게시(push_descriptors)와 pull import·CONFLICT 위임 경로가 계약 없이는 정식 연결 불가.
- **요청(계약 #2 보완)**:
  - `export_bundle(scope="SHAREABLE") -> Bundle` — 게이트 충족 descriptor만.
  - `import_bundle(bundle) -> ImportResult{applied, skipped_dedup, conflicts, errors}` — 무결성·dedup·CONFLICT 판정, 자동 overwrite 금지, 원격 상태 문자열로 로컬 승인·Replay 생성 금지(AD-Q4).
- **U2 처리(CJ 결정 2, 우회 없음)**: 자체 저장·무결성·CONFLICT **우회 금지**. gitsync 전송은 확정 계약 stub로 **병행 개발**하되 실제 import/pull 실검증과 명확히 구분. **pull import·CONFLICT 실검증은 계약 확정까지 `NOT_RUN`**.
- **우선순위**: CJ 우선 제공.

### C-d · `usage.py` — 공유 재사용 이벤트 계약 부재 (계약 #6)
- **현재**: 카운트 경로(`record_actual_reuse/build_evidence/new_execution_id`)는 있음. `export_shared_usage(VERIFIED_REUSE)` / `import_shared_usage`(event_id 검증·dedup) **없음**.
- **U2 영향**: `gitsync.push_shared_usage`가 전송할 `SharedUsageBundle` shape 미확정. 재사용 이벤트 공유(게시와 독립 경로) 왕복 불가.
- **요청(계약 #6)**:
  - `export_shared_usage(scope="VERIFIED_REUSE") -> SharedUsageBundle` — 이벤트 레코드(event_id, skill_ref{id,version,digest}, reuser_alias, evidence_ref), 비민감·합성만.
  - `import_shared_usage(bundle) -> UsageImportResult{applied, skipped_dedup, rejected_unverified, errors}` — 정확한 Skill 참조 + 실제 성공 근거 검증, **event_id 기준 dedup**.
- **U2 처리(CJ 결정 4, 우회 없음)**: 이벤트 규격·검증·dedup·저장 = CJ. **Git 전송 경계만 B**. gitsync는 확정 계약 stub로 **전송만 병행 개발**하고, bundle 생성·검증·dedup은 usage.py(CJ) 확정 시 연결. 이벤트 공유 왕복 실검증은 확정까지 **`NOT_RUN`**.
- **우선순위**: 하(게시와 독립, 조직 집계 완결용).

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

## 요약 (CJ 결정 반영 — 우회 없음)
| gap | 소유 | U2 처리(우회 없음) | 계약 확정 전 NOT_RUN 항목 |
|---|---|---|---|
| C-a lifecycle 저장 | CJ(SkillStore) | 판단·게이트·조회는 S3 유지, 저장은 계약 호출만 | lifecycle 영속 연동 |
| C-b store bundle | CJ(우선 제공) | 자체 저장·CONFLICT 우회 금지, 전송 stub 병행 | pull import·CONFLICT 실검증 |
| C-c match P1 검색 + 파일접근 적용·검증 | A(조율 중) | 미구현 검색 NO_MATCH 금지, 직접 조회 우회 제거 | 검색·파일접근 재사용 분기 |
| C-d usage 공유 이벤트 | CJ(규격·검증·dedup·저장) | Git 전송 경계만 B, 전송 stub 병행 | 이벤트 공유 왕복 실검증 |

**공통**: 계약 미확정 항목은 시연에서 **NOT_RUN으로 정직 기록**하고, U2는 확보된 계약(1·3·5-자체정의) + 병행 가능 골격(gitsync 전송 stub·S3 상태머신·C6·C7-P1·S2 OLS) 위에서 착수한다. **자체 저장·무결성·CONFLICT·NO_MATCH 우회는 하지 않는다.**
