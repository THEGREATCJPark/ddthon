# Unit of Work Dependency — Agent SkillLoop

**단계**: INCEPTION / Units Generation (Part 2)
**작성일**: 2026-09-08

> Unit 간 의존성·착수 순서·계약 동결 지점·수정 가능/금지 경로. **P0-우선 + 비블로킹** 원칙(사용자 결정).

---

## 1. Unit 의존성 매트릭스 (행 → 열: "행이 열에 의존")

| ↓의존 \ 대상→ | U0 공통·계약 | U1 P0 실행 | U2 P1·게시 | U3 집계·표현 |
|---|---|---|---|---|
| **U0 공통·계약(CJ)** | — | | | |
| **U1 P0 실행(A)** | ✅ 계약 1·3·4, C1/C2/C3/C7-P0/C8 | — | | |
| **U2 P1·게시(B)** | ✅ 계약 1·2·3·5, C1/C2/C3/C7 | ✅ S1 재사용 경로(파일접근), C5 계약 | — | |
| **U3 집계·표현(CJ)** | ✅ 계약 3(공유 usage), C2/C3, gitsync.last_sync | | ✅ **S3 상태 조회 계약(읽기전용)**, gitsync.py(전송 호출) | — |
| **Q1 QA(C)** | 횡단(전 Unit 실행·증거 검토, 코드 의존 아님) | | | |

**규칙**
- **U0가 유일하게 동결 계약을 소유·수정**. 나머지 Unit은 **인터페이스로만 접근, 계약 파일 수정 금지**(변경 제안은 CJ 조율).
- **파일별 단일 수정자**: `usage.py`=CJ, `cli.py`=CJ, `gitsync.py`=B, `envharness_p0.py`=CJ, `envharness_p1.py`=B. 다른 Unit은 호출 계약으로만 접근(분담 편집 금지).
- **게시 게이트·상태 lifecycle는 U2(S3)만 소유**. cli.py·U3는 우회 금지(AD-Q3).
- **재사용 이벤트 공유(U3)는 U2.S3.publish 와 독립**: U3는 S3 상태를 **읽기만**(추정·게이트 재구현 금지). 이벤트는 C3 검증·event_id dedup(`usage.py`, CJ), gitsync.push_shared_usage 전송(B 파일 호출).
- **읽기전용 vs 상태 변경**: U3 집계·표현(C10/C11/C12)은 읽기전용. **C3 공유 이벤트 import는 로컬 usage 상태를 변경하는 쓰기**(VERIFIED_REUSE 통과분만) — 읽기전용 아님.
- **U3 소유자=CJ**(“여력” 표기 폐기). UI·조직 집계는 **승인된 필수 범위**; P0 비블로킹은 선택 기능 의미 아님.
- **순환 없음**: U0 ← U1 ← U2 ← U3 방향(+ U2→U1 재사용 경로는 단방향 호출, 계약 고정).

---

## 2. 계약 동결 지점 (정렬 구간에서 먼저 확정 — 소유=U0/CJ, 단 7은 U2, 8은 U3)

| # | 계약 | 소유 | 소비 Unit | P0 blocking? |
|---|---|---|---|---|
| 1 | SkillDescriptor 직렬화 + digest 규칙 | U0 | U1,U2,U3 | ✅ |
| 2 | SkillStore import/export + CONFLICT 판정 | U0 | U2,U3(C4) | (P0는 로컬 저장만) |
| 3 | UsageTracker 카운트 인터페이스 + ReuseEvidence | U0 | U1(카운트),U3(공유 이벤트) | ✅ |
| 4 | SearchOutcome / Applicability 반환 규격 | U0 | U1,U2 | ✅ |
| 5 | ReplayResult + 게시 게이트 입력 규격 | U0→U2 | U2 | ❌(비블로킹 — P0는 미사용) |
| 6 | 공유 재사용 이벤트 레코드 + VERIFIED_REUSE 자격 + event_id 검증·dedup | U0 규격→CJ(U3) 구현(`usage.py`) | U3, gitsync(B) | ❌(비블로킹) |
| 7 | **S3 읽기전용 상태 조회 계약**(list/query_lifecycle_state + remote_publish_evidence/local_review_evidence) | **U2(S3)** | U3(C10) | ❌(비블로킹) |
| 8 | OrgSnapshot 규격 + last-sync 메타 | CJ(U3) | U3(C11/C12) | ❌(비블로킹) |

> **P0 blocking 최소 계약 = 1·3·4** (+ C1/C2 로컬 저장·C7 P0 harness·C8 run-p0 골격). 이 최소셋이 서면 U1 P0 종단이 가능.

---

## 3. 착수 순서 (17:30 P0 앵커)

```
[선행 — CJ, 즉시 / U0 전체 완료를 기다리지 않음]
U0 P0 최소셋 먼저 확정: 계약 1·3·4 초안 동결
   + 로컬 저장 조회(C2)·카운트(C3, usage.py)·환경 인터페이스(envharness_p0.py) + cli.py run-p0 골격
   ↓ (P0 최소 계약·인터페이스 확정 — U0 나머지는 이후에 계속)
[병렬 — 9/8 오후 : U0 공통부와 U1 실행부 동시 진행]
U1 P0 재사용 실행(A): 검색·매칭·적용·검증·카운트 → ★ 9/8 17:30 P0 종단 목표
CJ(U0): 나머지 계약 2·5 + 통합·기준 SHA·경로 확정 계속(U1을 막지 않음)
   ↓
[U2 — Day2 대기 아님: 계약(1·2·3·5)+승인 게이트 충족 시 U1과 병행 착수 가능]
U2 P1·게시(B): S2/S3/C6/gitsync.py(push_descriptors 등)/envharness_p1.py. U0 계약 + U1 재사용 경로 사용.
   S3 상태 조회 계약(7) 확정 → U3 소비 가능.
[병렬·비블로킹 — 필수 범위]
U3 집계·표현·이벤트 공유(CJ): 계약 6·7·8 확정 후 골격(모의 스냅샷) 병렬 →
   실데이터는 U2 게시·pull 후, 시연 미검증은 NOT_RUN. P0/P1 종단을 막지 않음(단 필수 완료 대상).
[횡단]
Q1 QA(C): 전 구간 독립 재현·사용성·증거 검토.
[수렴]
Build and Test(통합) → README/증거 정리 → 제출 점검.
```

---

## 4. 수정 가능 / 금지 경로 (P0 우선 명확화)

**파일별 단일 수정자(single-writer). 다른 Unit은 호출 계약으로만 접근, 편집 금지.**

| 파일/경로 | **단일 수정자** | 타 Unit 접근 |
|---|---|---|
| 동결 계약(1~5) 정의 | **CJ (U0)** | 읽기·인터페이스 사용만, **수정 금지**(제안은 CJ 조율) |
| `descriptor.py` (C1) | CJ (U0) | 인터페이스 사용 |
| `store.py` (C2) | CJ (U0) | 인터페이스 사용 |
| `usage.py` (C3 카운트 **+ 공유 이벤트 export/import·VERIFIED_REUSE 검증·dedup**) | **CJ** | 인터페이스 사용. gitsync는 전송만 호출 |
| `envharness_p0.py` (C7 P0) | CJ (U0) | 인터페이스 사용 |
| `cli.py` (C8) | **CJ** | 타 Unit은 **연결할 호출 계약(엔트리 시그니처) 제공**, 직접 편집 금지 |
| `match.py` (C5) / `reuse_service.py` (S1) | A (U1) | U2는 S1을 호출만 |
| `experience_service.py` (S2) / `publish_pipeline.py` (S3, +상태 조회 계약) / `replay.py` (C6) | B (U2) | U3는 S3 상태를 **읽기만** |
| `gitsync.py` (C4: push_descriptors·push_shared_usage·pull·last_sync 전송) | **B** | U3는 push_shared_usage/pull/last_sync를 **호출만**(편집 금지). 검증·dedup은 usage.py(CJ) |
| `envharness_p1.py` (C7 P1) | B (U2) | 인터페이스 사용 |
| `org_aggregator.py` (C10) / `statusline.py` (C11) / `dashboard.py` (C12) | CJ (U3) | **읽기전용 파생**, 소유 상태 미수정 |
| `agent_skill/` (C9) | CJ (U0) | — |
| `tests/`·실행 증거 | 각 Unit 작성 + **Q1/C 독립 검토** | — |

> **함수별 분담 편집을 폐기**하고 파일별 단일 수정자로 통일(함수 추가만 해도 병합 충돌 가능). 공유 이벤트 검증·dedup은 `gitsync.py`가 아니라 `usage.py`(CJ)에 위치하고, `gitsync.py`(B)는 전송만 담당. 동결 계약은 **추가(append-only)** 원칙, 시그니처 변경은 소유자 조율.

---

## 5. 비블로킹 보장 (사용자 요구)
- P0 종단(U1)은 **U2/U3/UI에 의존하지 않는다** — 계약 최소셋(1·3·4)+U0 P0 기반만 필요.
- **U0 전체 구현 완료를 U1이 기다리지 않는다**: P0 최소 계약(1·3·4)과 로컬 저장 조회(C2)·카운트(C3)·환경 인터페이스(envharness_p0)가 서면 **U0 공통부와 U1 실행부는 병렬 구현**.
- U3(UI·집계·이벤트 공유)와 U2의 게시·sync 완성도는 **P0 실행 성공의 전제 조건이 아니다.** 단 UI·조직 집계는 **승인된 필수 범위**이며 비블로킹 ≠ 선택 기능.
- **U2(B)는 Day2 대기가 아니다**: 필요한 계약(1·2·3·5)과 해당 설계·Code Plan 승인 게이트를 충족하면 U1과 병행 착수 가능.
- U3 실데이터·시연 미검증은 **NOT_RUN**으로 기록하고 P0/P1 완료 판정과 분리.
