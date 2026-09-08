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

**계약 확정 (CJ 공통 의존성 확정 2026-09-08 2차 — 호출 계약 확정, 검증 commit SHA 대기)**
> 제공 순서: **① lifecycle 저장 + descriptor import/export, ② 공유 usage 이벤트**. 각 항목 검증 commit SHA 전달 예정. U2는 확정 호출 계약 기준 연결 + 승인 Code Plan 범위 독립 구현 + 테스트 대역(stub)만 진행하고, 실제 성공은 SHA 수신·실행 후 인정(미실행 NOT_RUN, 대역과 구분). **CJ 공통 계약 승인 ≠ U2 전체 구현 승인.**
- ✅확정 C-a: lifecycle **저장·로드 = CJ `store` 계약 제공**(제공 ①). 상태 판단·변경 요청·읽기전용 조회는 S3(U2) 단독, 자체 lifecycle.json **미구현**, 상태는 exact `id/version/digest`에 연결. SHA 수신·실행 전 **영속 연동 NOT_RUN**.
- ✅확정 C-b: descriptor **export/import = CJ 제공**(제공 ①). digest 검증·DEDUP/CONFLICT는 **store 처리**(U2 미구현). S3는 **공유 자격 판단한 정확한 후보만 export** 연결. gitsync 전송 stub 병행 → 실제 import/pull·CONFLICT 검증은 SHA 전 **NOT_RUN**.
- ⚠대기 C-c: `match.search` P1 입력 **+ 파일접근 Skill 적용·검증 계약** — **A 조율 중(대기)**. 미구현 검색을 NO_MATCH로 간주 금지, store 직접 조회 우회 **제거**. 확정 전 **검색·파일접근 재사용 분기 NOT_RUN**.
- ✅확정 C-d: 공유 이벤트 규격·검증·dedup·**저장 = CJ**(제공 ②). **Git 전송·pull·last-sync 경계만 B**, 전송 시 **event_id 재발급 금지**(그대로 전송). 전송 stub 병행 → 이벤트 공유 왕복 실검증은 SHA 전 **NOT_RUN**.

**외부 의존**
- Python 3, 표준 라이브러리: `json`, `hashlib`, `zipfile`, `xml.etree.ElementTree`, `subprocess`, `uuid`, `tempfile`, `csv`.
- **Git CLI**(`git`): gitsync가 `subprocess`로 호출(별도 서버 없음, FR-SYNC-2). 실제 원격 push는 **인증 필요** — 불가 시 D-3(PUBLISH_PENDING + NOT_RUN).
- 테스트: `pytest` + `Hypothesis`(PBT partial).
- **외부 인터넷·사내 데이터·secret 미의존**(NFR-RUN-1, NFR-SEC-1).

**파일 소유(단일 수정자)**: `experience_service.py`/`publish_pipeline.py`/`replay.py`/`envharness_p1.py`/`gitsync.py` = **B**. descriptor/store/usage/cli/envharness_p0 = CJ, match/reuse_service = A → **호출만**.

---

## 2. Tech-Stack 결정 (minimal)

| 항목 | 결정 | 근거 |
|---|---|---|
| **XLSX 파서(허용 대안)** | **stdlib 전용**(`zipfile` + `xml.etree`) 기본 채택 | NFR-RUN-1(새 clone/ZIP에서 선언 의존성만으로 실행). 제3자 XLSX 라이브러리 **필수 의존 회피**. XLSX=OOXML zip이므로 `xl/worksheets/*.xml` read-only 파싱 가능 |
| **직접 parser(실패 관찰)** | Code Plan에서 **실제 관찰 실패 메커니즘 확정**(강제 raise·DRM 금지) | FR-P1-1/NFR-SEC-2. naive 접근이 이 합성 파일에서 실제 실행 시 실패를 반환하도록 구성. openpyxl 등은 **선택**(더 현실적 데모용)이며 새-clone 실행 필수 아님 |
| **Git 전송** | `git` CLI(subprocess) + **team-skill-store 전용 로컬 미러 dir**(D-2) | 별도 서버 없음(FR-SYNC-2), dev worktree 미오염 |
| **lifecycle 영속** | **CJ `store` 저장·로드 계약에 위임(C-a 확정, 제공 ①, SHA 대기)** | 상태 판단·변경 요청·읽기전용 조회는 S3(U2) 단독, 자체 lifecycle.json 미구현, 상태는 exact id/version/digest 연결. SHA 수신·실행 전 영속 연동 NOT_RUN |
| **테스트 프레임워크** | pytest + Hypothesis | NFR-TEST-1(PBT partial)·TEST-2(process/contract/regression) |

> **미결정→기본 채택 안내**: 직접 parser의 정확한 실패 메커니즘과 openpyxl 채택 여부는 Code Plan에서 확정. 기본은 **stdlib 전용 + 강제 raise 없는 실제 관찰 실패**. 다른 방향(예: openpyxl 필수 채택) 원하시면 검토 게이트에서 지정.

---

## 3. 실행 환경
- Windows-native, 로컬 CLI. 합성·비민감 데이터만(CON-1).
- P1 합성 XLSX: 3개 완료월 총생산량을 담되 **원본 업무 데이터·secret 미포함**(NFR-SEC-1).
- read-only 경계: 승인된 대상만 read-only 접근, DRM 우회·비허용 접근 금지(NFR-SEC-2).
- gitsync 미러: 로컬 별도 clone/체크아웃 경로. push 성공 확인 전 PUBLISHED 미보고(D-3).

---

## 4. 필수 검증 항목 (U2 완료 기준)

| # | 항목 | 근거 | 판정 방식 |
|---|---|---|---|
| U2-V1 | 직접 parse는 **실제 실행 관찰 실패**(강제 raise 아님), 합성 XLSX read-only 대안으로 내용 획득 가능 | FR-P1-1/4, C7 경계 | integration(run-p1) |
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

> 실제 원격 push 인증 불가 항목(U2-V10 PUBLISHED 도달, U2-V11 원격 왕복, C-b/C-d 관련 pull·이벤트 공유)은 **NOT_RUN으로 정직 기록**.

---

## 5. 보안·복원력 (반영, 신규 아님)
- **NFR-SEC-1**: candidate·bundle·화면에 secret·원본 업무 데이터·계산 결과 미포함.
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
