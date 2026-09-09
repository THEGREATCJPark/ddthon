# U2 (P1·후보화·게시·Git 전송) — NFR Requirements (minimal)

**단계**: CONSTRUCTION / NFR Requirements / Unit **U2** (담당: B 한석훈)
**깊이**: 최소(minimal)
**작성일**: 2026-09-08 (기준 커밋 `7cbc856`)
**범위**: US-P1-1~4 경로(S2/S3/C6/C7-P1/C4). NFR Design·Infrastructure Design은 SKIP(승인). 본 문서는 **의존성·실행 환경·tech-stack 결정·필수 검증 항목**만 간결히 기술.

> 승인된 핵심 NFR(NFR-SEC-1~4, NFR-RES-1~4, NFR-RUN-1/2, NFR-INT-1)과 PBT partial을 설계·테스트에 반영. **신규 NFR을 추가하지 않는다.**

---

## 1. 의존성 (U2 착수 전 확정)

**계약 의존 (확보/gap)**
- ✅ 계약 1 (descriptor digest·직렬화): `descriptor.make_descriptor/compute_digest/serialize/deserialize` — 확보.
- ✅ 계약 3 카운트 경로: `usage.record_actual_reuse/build_evidence/new_execution_id/current_count` — 확보(파일접근 재사용 성공 카운트에 사용).
- 계약 5 (ReplayResult + 게이트 입력): U0 프리즈 없음 → **U2가 `replay.py`에서 정의**(blocker 아님).

**계약 구현 제공됨 (CJ 공통 의존성 — main `ef03b3a`+`cfc62e9`, work/u2-p1-git 병합 반영)**
> 제공: **① `ef03b3a` lifecycle 저장 + descriptor export/import, ② `cfc62e9` 공유 usage 이벤트**. **"구현 SHA 대기" 해소.** U2는 실제 API(bytes blob) 기준 gitsync/S3 정합 + 승인 Code Plan 범위 독립 구현만 진행하고, 실제 성공은 **실제 연동 통합 검증 후** 인정(미실행 NOT_RUN, 대역과 구분). **CJ 공통 계약 승인 ≠ U2 전체 구현 승인.**
- ✅구현 C-a: `store.save_lifecycle_state(skill_ref, state, evidence)`/`load_lifecycle_state`/`list_lifecycle_records`(저장만·전이 미판단). 상태 판단·변경 요청·읽기전용 조회는 S3(U2) 단독, 자체 lifecycle.json **미구현**, 상태는 exact `id/version/digest`에 연결. **실제 영속(저장→재시작 로드) 통합 검증 전 NOT_RUN**.
- ✅구현 C-b: `store.export_bundle(refs: list[dict]) -> bytes`(**exact refs 목록, scope 문자열 아님**)/`import_bundle(blob) -> list[PutResult]`. digest 검증·DEDUP/CONFLICT는 **store 처리**(U2 미구현). S3는 **공유 자격 판단한 정확한 후보만** `export_bundle([ref])` 연결. **실제 원격 import/pull·CONFLICT 왕복 검증 전 NOT_RUN**.
- ⚠대기 C-c: `match.search` P1 입력 **+ 파일접근 Skill 적용·검증 계약** — **A 조율 중(대기)**. 미구현 검색을 NO_MATCH로 간주 금지, store 직접 조회 우회 **제거**. 확정 전 **검색·파일접근 재사용 분기 NOT_RUN**.
- ✅구현 C-d: `usage.export_shared_usage() -> bytes`/`import_shared_usage(blob, local_ref_exists) -> list[dict]`. 저장·검증·dedup=CJ. **Git 전송·pull·last-sync 경계만 B**, 전송 시 **event_id 재발급 금지**, pull 시 **정확한 로컬 Skill 존재 확인**(`local_ref_exists`=store.get+digest 일치) 연결. **이벤트 공유 왕복 실검증 전 NOT_RUN**.

**외부 의존**
- Python 3, 표준 라이브러리: `json`, `hashlib`, `zipfile`, `subprocess`, `uuid`, `tempfile`, `csv`.
- **`pywin32`(win32com) + Excel 설치·실행**(P1 Excel 경로): 암호화 합성 파일 생성(COM SaveAs Password)·실행 중 Excel attach(`GetActiveObject`) 셀 읽기. **NFR-RUN-1 P1 한정 예외**(선언된 사전조건, P0·기타 확대 금지). Excel 미설치→해당 P1 경로 `NOT_RUN`.
- **Git CLI**(`git`): gitsync가 `subprocess`로 호출(별도 서버 없음, FR-SYNC-2). 실제 원격 push는 **인증 필요** — 불가 시 D-3(PUBLISH_PENDING + NOT_RUN).
- 테스트: `pytest` + `Hypothesis`(PBT partial).
- **네트워크 경계 구분**: "외부 인터넷 미의존"은 **로컬 P1 업무·테스트 실행 범위로 한정**한다(사내 데이터·secret 미의존, NFR-RUN-1/NFR-SEC-1). **GitHub 원격 sync(gitsync pull/push)는 네트워크와 인증이 필요**하며 이는 로컬 실행 미의존과 구분되는 별개 요구다.

**파일 소유(단일 수정자)**: `experience_service.py`/`publish_pipeline.py`/`replay.py`/`envharness_p1.py`/`gitsync.py` = **B**. descriptor/store/usage/cli/envharness_p0 = CJ, match/reuse_service = A → **호출만**.

---

## 2. Tech-Stack 결정 (minimal)

| 항목 | 결정 | 근거 |
|---|---|---|
| **P1 실패 모델** | **Office 암호화 합성 파일 + 실행 중 Excel read-only attach** 확정(CJ, (가)안, FD §1/D-5) | 암호화본 바이트=OLE-CFB(zip 아님). 실증: 암호화 직접접근 실패/평문 성공/attach 읽기·원본 무변경. 폐기: read-only 표면·naive 파서 모델 |
| **직접(정상) 접근** | 표준 XLSX 리더(openpyxl/pandas/zipfile) | 암호화본은 zip이 아니라 리더가 **스스로 `BadZipFile`** → 자연 실패(강제 raise·잘못된 API 아님, 평문 대조군 성공 ⇒ 원인=환경, FR-P1-1) |
| **허용 대안** | 실행 중 Excel 인스턴스에 attach(`win32com.GetActiveObject`) → 셀 값 read-only 읽기 | 애플리케이션이 복호화한 문서 매개로 성공. **Save 미호출·원본 mtime/hash 무변경**(NFR-SEC-2). Agent가 탐색·선택(harness 미제시) |
| **Git 전송** | `git` CLI(subprocess) + **team-skill-store 전용 로컬 미러 dir**(D-2) | 별도 서버 없음(FR-SYNC-2), dev worktree 미오염 |
| **lifecycle 영속** | **CJ `store` 저장·로드 API 사용(C-a 구현 제공됨 `ef03b3a`)** | `save/load_lifecycle_state`·`list_lifecycle_records`. 상태 판단·변경 요청·읽기전용 조회는 S3(U2) 단독, 자체 lifecycle.json 미구현, exact id/version/digest 연결. 실제 영속 통합 검증 전 NOT_RUN |
| **테스트 프레임워크** | pytest + Hypothesis | NFR-TEST-1(PBT partial)·TEST-2(process/contract/regression) |

> **모델·의존성 확정(Code Plan 이월 아님)**: P1 실패 모델(Office 암호화 + 실행 중 Excel attach)·직접 접근(표준 zip 리더)/허용 대안(Excel attach)·필요 의존성(`pywin32` + **Excel 설치·실행**)은 **본 FD/NFR로 고정**. **NFR-RUN-1의 P1 Excel 경로 한정 예외 승인**(P0·기타 범위 확대 금지, Excel 미설치→`NOT_RUN`). Code Plan은 **구현 세부(attach 재시도·워크북 매칭·셀 범위 읽기 정확한 호출)만** 확정.

---

## 3. 실행 환경
- Windows-native, 로컬 CLI. 합성·비민감 데이터만(CON-1).
- P1 합성 XLSX: 3개 완료월 총생산량을 담되 **원본 업무 데이터·secret 미포함**(NFR-SEC-1). **Office 암호화본**으로 저장하며 **암호는 사용자(사전조건) 소유** — harness/Agent/후보 절차에 평문 암호 미포함.
- **P1 사전조건**: Excel 설치·실행 + 사용자가 합성 파일을 (암호로) 열어둔 상태. 미충족 시 P1 Excel 경로 `NOT_RUN`.
- read-only 경계: 실행 중 Excel attach는 **Save 미호출·원본 무변경**의 read-only만, DRM 실제 우회·비허용 접근 금지(NFR-SEC-2).
- gitsync 미러: 로컬 별도 clone/체크아웃 경로. push 성공 확인 전 PUBLISHED 미보고(D-3).

---

## 4. 필수 검증 항목 (U2 완료 기준)

| # | 항목 | 근거 | 판정 방식 |
|---|---|---|---|
| U2-V1 | 표준 zip 리더 직접 접근이 암호화본에서 **실제 실행 관찰 실패**(`BadZipFile`, 강제 raise 아님), 실행 중 Excel attach 대안으로 셀 내용 획득·원본 무변경 | FR-P1-1/4, C7 경계, NFR-RUN-1 P1 예외 | integration(run-p1, Excel 있을 때)/NOT_RUN |
| U2-V2 | 실제 검색 수행 후에만 NO_MATCH, 오류/timeout/미호출은 별도 상태로 구분 | FR-P1-2 | unit/integration |
| U2-V3 | FR-P1-5 OLS: 기준월=마지막 완료월+1, 3점 OLS(x=1..3→x=4), 음수 0 clamp | FR-P1-5 | property(Hypothesis)+unit |
| U2-V4 | 결과 표시: 실제 3개월 + 예상 1개월 구분, 예측 대상 월·단위·값 명시 | FR-P1-5 | unit |
| U2-V5 | 후보 descriptor는 **환경 절차만**(계산식·생산량·차트·원본·secret 제외), digest dedup | FR-P1-6, FR-SKILL, NFR-SEC-1 | unit/property |
| U2-V6 | 게시 게이트: 승인·Replay PASS·digest 동일성 **모두** 충족 시만 진행 | FR-P1-7 | unit/integration |
| U2-V7 | 거절/FAIL/NOT_RUN/미완료 → BLOCKED(게시 금지) | FR-P1-7 | unit |
| U2-V8 | 승인 후 내용/version/digest 변경 → 기존 승인 무승계, 재검토·재Replay | FR-P1-7 | unit |
| U2-V9 | 상태 명확 구분(제안/검토/Replay/LOCALLY_APPROVED/PUBLISHED/PUBLISH_PENDING/BLOCKED) | FR-P1-7 | unit |
| U2-V10 | **PUBLISHED는 원격 push 성공 확인 후에만**; 실패/불가 시 로컬 SHAREABLE 보존 + PUBLISH_PENDING | FR-P1-7, FR-SYNC-4, D-3 | integration(가능 시)/NOT_RUN |
| U2-V11 | sync: DB 파일 미전송, descriptor/이벤트만; 실패 시 로컬 미손상·재시도 근거 | FR-SYNC-5, FR-SYNC-4, NFR-RES-3 | unit/integration |
| U2-V12 | 읽기전용 상태 조회 계약(list/query_lifecycle_state)이 원격/로컬 근거 분리 반환 | 계약 7, AD-Q4 | unit(U3 소비 계약) |
| U2-V13 | 원격 수신 Skill 자동 실행 금지(Replay는 명시적·독립) | NFR-SEC-4 | unit |
| U2-V14 | run-p1 실제 샘플 실행 = 직접 실패 관찰 → (검색) → 대안 → OLS 완료·검증 → 후보 → 검토·Replay·(게시 시도) | US-P1-1~4 | e2e 데모, 실행 증거 |

> **실패 실행 근거 vs NOT_RUN 구분(정직 기록)**: (a) 최초 `git push`(작업 브랜치)는 **403으로 실제 시도 후 실패** → "**실패 실행 근거**"로 보존(이후 권한 해결로 push 성공). (b) **아직 실행하지 않은** 제품 원격 게시 성공 도달(U2-V10 PUBLISHED)·원격 왕복(U2-V11)·C-b/C-d pull·이벤트 공유 통합 검증은 **`NOT_RUN`**. (a)와 (b)는 혼동하지 않는다.

---

## 5. 보안·복원력 (반영, 신규 아님)
- **NFR-SEC-1(정정)**: **P1 업무 결과 화면에는 계산값을 표시한다**(FR-P1-5: 실제 3개월 + 예상 1개월 값·단위·대상 월). 제외 대상은 **공유 Skill descriptor·공유 bundle**에 담기는 **업무 데이터·계산 로직·생산량 값·secret·원본**이다(공유물은 환경 접근 절차만). 즉 "미포함"은 화면이 아니라 **공유물** 경계에 적용.
- **NFR-SEC-2**: 보호 XLSX는 승인된 read-only 접근만, DRM 우회 금지.
- **NFR-SEC-3**: descriptor digest·입력 무결성 검증.
- **NFR-SEC-4**: 원격 수신 Skill 자동 실행 금지 — Replay·적용은 명시적.
- **NFR-RES-1**: 후보 digest dedup. **RES-2**: CONFLICT는 store 위임(동일 id,ver+다른 digest만). **RES-3**: sync 실패 로컬 보존·재시도. **RES-4**: lifecycle/후보 재시작 보존(로컬 JSON).
- **NFR-INT-1**: 소유 상태 단일 writer(S3 lifecycle, gitsync 전송) — 공유 mutable state 동시 수정 최소화.

## 6. 성능·규모
- 로컬 단일 실행·소량 합성 데이터. **정량 성능 목표 없음(해당 없음)**. 결정성·재현성·정직한 상태 구분이 우선.

## 7. 미결정 (Code Plan 이월)
- 직접 parser 실패 메커니즘 확정(강제 raise 금지) + openpyxl 채택 여부.
- 합성 XLSX 픽스처 정의(3개월 생산량 스키마).
- gitsync 미러 경로·**team-skill-store branch 초기화(D-4, B 담당)**·bundle 파일 레이아웃.
- lifecycle 저장·로드는 **CJ `store` 계약**(C-a 확정, 제공 ①)에 연결(자체 파일 저장 없음). CLI 명령 문자열 연결(cli.py=CJ 계약).
- OLS·게이트·digest 불변식 PBT 구체화.
- CJ 공통 계약(C-a/C-b/C-d) **확정** — 검증 commit SHA(제공 ①②) 수신 시 stub→실연동 전환 및 해당 NOT_RUN 해제. A 계약(C-c)은 대기 유지.

## Approved implementation alignment — operator/org Cold

See construction/plans/operator-open-org-cold-code-generation-plan.md, approved 2026-09-09. Operator open/activate uses public fixture password outside Agent workspace; exact full path identifies the workbook across Excel instances. Preparation never counts as discovery or Replay. Git context binds explicit remote/branch/mirror, preserving legacy default; new live branch starts P0-only. C6 supports action-specific pip install/version/import evidence and file read-only evidence; S3 retains exact review+fresh Replay+confirmed push gates. Claude Code conversational review records the actual user response and exact candidate; no native GUI or automatic yes; candidate completion invites user approval proactively. Technical prerequisites remain Windows Excel/pywin32, Python venv/pip and authenticated Git for remote transport. Local workflow remains offline except Git sync. PBT partial scope and existing security/resiliency requirements unchanged.
