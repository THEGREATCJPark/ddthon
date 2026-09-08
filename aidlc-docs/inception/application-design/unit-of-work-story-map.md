# Unit of Work ↔ Story Map — Agent SkillLoop

**단계**: INCEPTION / Units Generation (Part 2)
**작성일**: 2026-09-08

> 모든 승인된 스토리(US-P0-1, US-P1-1~4, US-UI-1, US-UI-2)를 Unit에 배정. 누락 없음 확인.

---

## 스토리 ↔ Unit 매핑

| 스토리 | 주 Unit(소유) | 지원 Unit(계약 제공) | 핵심 요구사항 | P0 blocking? |
|---|---|---|---|---|
| **US-P0-1** (설치 실패→Skill 적용→실제 설치·검증·reuse+1) | **U1 (A)** | U0 (C1/C2/C3/C7-P0/C8, 계약 1·3·4) | FR-SURF, FR-P0, FR-MATCH, FR-USAGE-1/2, NFR-SEC-4 | ✅ **17:30 핵심** |
| **US-P1-1** (직접 접근 실패 관찰 + 검색 NO_MATCH 구분) | **U2 (B)** | U0(C7-P1), U1(C5 계약) | FR-P1-1/2, FR-MATCH, NFR-SEC-2 | ❌ |
| **US-P1-2** (환경 사실·허용 대안 탐색 + OLS 업무 완료·검증) | **U2 (B)** | U0(C7-P1/C1), U1(S1 재사용) | FR-P1-3/4/5, NFR-SEC-2 | ❌ |
| **US-P1-3** (새 절차만 후보화, 계산·원본 제외) | **U2 (B)** | U0(C1) | FR-P1-6, FR-SKILL, NFR-SEC-1/3, NFR-RES-1 | ❌ |
| **US-P1-4** (검토·독립 Replay·게시 게이트, branch push, PUBLISHED=push 성공) | **U2 (B)** | U0(C2, 계약 5), C6/C4.push_descriptors | FR-P1-7, FR-SYNC-1~5, FR-USAGE-4, NFR-RES-2/3, NFR-SEC-4 | ❌ |
| **US-UI-1** (상태줄 조직 현황 간단 표시) | **U3 (CJ)** | U0(C2/C3), U2(S3 상태 조회 읽기전용), C10 | FR-UI-1/3, FR-ORG, FR-USAGE-3/4 | ❌ **비블로킹(필수 범위)** |
| **US-UI-2** (localhost 읽기전용 대시보드) | **U3 (CJ)** | U0(C2/C3), U2(S3 상태 조회 읽기전용), gitsync.last_sync, C10 | FR-UI-2/3, FR-ORG, FR-USAGE-3/4, NFR-SEC-1/2 | ❌ **비블로킹(필수 범위)** |

**재사용 이벤트 공유(FR-USAGE-4, US-P1-4·US-UI-*에 걸침)**: 자격=VERIFIED_REUSE(게시와 독립). 생산=U1/U2 실제 재사용 성공(C3 기록). export/import·VERIFIED_REUSE 검증·event_id dedup=`usage.py`(CJ, U3 로직) — **import는 로컬 상태 변경(쓰기)**. 전송=`gitsync.push_shared_usage/pull`(B 소유 파일 호출). A게시→B import→B 검증 성공→B 공유→A 1회 반영.

---

## 배정 검증
- ✅ 7개 스토리 전부 주 Unit 배정(US-P0-1→U1, US-P1-1~4→U2, US-UI-1/2→U3).
- ✅ P0 핵심(US-P0-1)은 U0 최소 계약(1·3·4) + U0 P0 기반만 의존 → **17:30 독립 실행 가능**.
- ✅ UI/집계(US-UI-1/2)는 **비블로킹** — P0/P1 종단의 전제 아님.
- ✅ Q1(C, QA 횡단)은 스토리 소유가 아니라 **전 스토리의 실행·재현·증거 독립 검토**(FR-SURF-2/3 사람 단독 재현 포함).
- ✅ 게시 게이트·상태 lifecycle 단일 소유(U2/S3), 재사용 이벤트 공유는 독립 경로(U3) — 승인된 계약과 정합.

---

## Unit별 스토리 요약
- **U0 (CJ)**: 스토리 직접 소유 없음 — 전 스토리의 **공통 계약·저장·카운트·환경·CLI 기반** 제공(특히 US-P0-1 blocking 최소셋).
- **U1 (A)**: US-P0-1. — 17:30 P0 종단.
- **U2 (B)**: US-P1-1/2/3/4. — Day2 P1 업무·후보화·게시.
- **U3 (CJ)**: US-UI-1/2 + 재사용 이벤트 공유 전송/집계. — 비블로킹이나 **승인된 필수 범위**. 집계·표현=읽기전용, C3 공유 이벤트 import=상태 변경(쓰기).
- **Q1 (C)**: 횡단 — 전 Unit 독립 QA·사용성·실행 증거.
