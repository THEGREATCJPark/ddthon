# Unit of Work — Agent SkillLoop

**단계**: INCEPTION / Units Generation (Part 2)
**작성일**: 2026-09-08
**깊이**: 최소(minimal). 근거: 승인된 Application Design + 사용자 결정 파라미터(17:30 P0 앵커, 역할, Unit 수 비고정, P0 우선, 비블로킹).

> Unit은 **논리적 개발 단위**(단일 소유자·소유 경계·동결 계약)다. 컴포넌트/서비스와 1:1이 아니며, 사람 수(4)·컴포넌트 수(12)에 Unit 수를 맞추지 않는다.

---

## Unit 요약

| Unit | 이름 | 소유자 | 포함 컴포넌트/서비스 | P0 blocking? | 착수 |
|---|---|---|---|---|---|
| **U0** | 공통·계약·통합 | **CJ** | C1, C2, C3(카운트·ReuseEvidence), C7(P0 harness 우선), C8 CLI 골격, C9 wrapper 통합 지점, 계약 동결(1~5) | **YES(선행)** | 즉시 |
| **U1** | P0 재사용 실행 | **A 최호길** | C5, S1 (+C3.record_actual_reuse 호출) | **YES(핵심)** | U0 계약 초안 후 병렬 |
| **U2** | P1 경험·후보화·게시 | **B 한석훈** | S2, S3(+상태 조회 계약 제공), C6, gitsync.py(**B 단일 수정자** — push_descriptors·push_shared_usage·pull·last_sync), C7-P1(envharness_p1.py) | NO(P0 비블로킹, 단 Day2 대기 아님) | 필요한 계약+승인 게이트 충족 시 즉시 독립 착수 |
| **U3** | 조직 집계·표현·재사용 이벤트 공유 | **CJ** | C10, C11, C12, C3 공유 usage import/export(VERIFIED_REUSE) | **NO(P0 비블로킹, 필수 범위)** | 계약(6·7·8) 후 병렬 |
| **Q1** | 독립 QA·사용성·실행 증거 (횡단 트랙, 코드 소유 Unit 아님) | **C 윤여훈** | (소스 미소유) 전 Unit 교차 검토·재현·증거 | — | 전 구간 |

---

## Unit 상세

### U0 — 공통·계약·통합 (CJ) — **선행, P0 blocking**
- **책임**: 공용 도메인·저장·카운트·환경·CLI 골격을 제공하고 **공유 계약을 동결**한다. repo/branch 통합, 공통 기준 SHA, 작업 경로 확정.
- **포함**: C1(직렬화 round-trip + digest 불변), C2(dedup/CONFLICT/import·export), C3(실제 성공 카운트 + ReuseEvidence + DEMO_SEED 구분; 공유 이벤트 규격은 **계약만** 우선, 구현은 U3), C7(**P0 이중 mock index 우선**; P1 보호 XLSX는 P0 이후/또는 U2 협의), C8 CLI 골격(run-p0 경로 우선) + C9 wrapper 통합 지점.
- **동결 계약(다른 Unit은 인터페이스로만 접근, 수정 금지)**: (1) SkillDescriptor 직렬화+digest, (2) SkillStore import/export+CONFLICT, (3) UsageTracker 카운트 인터페이스+ReuseEvidence, (4) SearchOutcome/Applicability 반환 규격, (5) ReplayResult+게시 게이트 입력 규격.
- **P0 blocking 최소셋(17:30 우선)**: C1·C2·C3 카운트·C7 P0 harness·C8 run-p0 골격 + 계약 (1)(3)(4).
- **수정 경로**: 동결 계약 파일은 **CJ 소유**. 변경 필요 시 CJ 조율(다른 Unit 직접 수정 금지, 제안만).

### U1 — P0 재사용 실행 (A 최호길) — **17:30 핵심 경로**
- **책임**: pip 설치 실패 관찰 → 검색·applicability 매칭(근거) → 적용·검증 → **실제 성공만 카운트**(US-P0-1, FR-P0, FR-MATCH, FR-USAGE-1/2, NFR-SEC-4).
- **포함**: C5 SkillSearchMatcher(결정적 검색+applicability+근거, NO_MATCH 구분), S1 ReuseService(시나리오 비의존; pip-install 유형 적용+효과검증; 성공 시 C3.record_actual_reuse).
- **소유 경계**: C5/S1 파일 소유. **U0 동결 계약 파일 수정 금지**(사용만). C3는 인터페이스(record_actual_reuse)로만 호출.
- **의존**: U0 (C1/C2/C3/C7-P0/C8 run-p0 골격, 계약 1·3·4).

### U2 — P1 경험·후보화·게시 (B 한석훈) — **P0 비블로킹(Day2 대기 아님)**
- **책임**: 직접 접근 실패 관찰 → (파일접근 유형이면 S1 재사용) → 환경 사실·허용 대안 탐색(Agent) → OLS 업무 완료·검증 → 새 절차만 후보화 → 검토·독립 Replay·게시 게이트(US-P1-1~4, FR-P1-*, FR-SYNC-1~5).
- **포함**: S2 ExperienceService, S3 PublishPipeline(**+ 읽기전용 상태 조회 계약 `list_lifecycle_states`/`query_lifecycle_state` 제공** — U3가 소비), C6 ReplayVerifier, **`gitsync.py` 단일 수정자**(C4: push_descriptors·push_shared_usage·pull·last_sync 전부 — 단, **공유 이벤트 검증·dedup 로직은 C3/CJ 책임**이고 gitsync는 전송만), **`envharness_p1.py`**(C7 P1 harness, 보호 XLSX).
- **소유 경계**: S2/S3/C6/gitsync.py(전체)/envharness_p1.py 소유. S1 재사용 경로는 U1 계약으로 호출(재구현 금지). **게시 게이트·상태 lifecycle는 U2(S3)만 소유** — 우회 금지.
- **착수**: Day2 대기 아님 — 필요한 U0 계약(1·2·3·5)이 서고 해당 설계·Code Plan 승인 게이트를 충족하면 **U1과 병행하여 지금부터 독립 착수 가능**. U1 재사용 경로(S1)는 계약으로 참조.
- **의존**: U0 계약(1·2·3·5), U1 재사용 경로(S1, 파일접근 유형), C5 계약.

### U3 — 조직 집계·표현·재사용 이벤트 공유 (CJ) — **P0 비블로킹, 승인된 필수 범위**
- **책임**: 재사용 이벤트 공유(VERIFIED_REUSE, 게시와 독립) + 읽기전용 조직 스냅샷 + 상태줄/로컬 대시보드(US-UI-1/2, FR-UI-*, FR-ORG-*, FR-USAGE-4). **UI·조직 집계는 승인된 필수 범위** — "P0 비블로킹"은 P0 종단 성공의 전제가 아니라는 의미이며 선택(optional) 기능이라는 뜻이 아니다.
- **포함**: C10 OrgAggregator(C2/C3/`gitsync.last_sync` 읽기 + **S3 읽기전용 상태 조회로만** 상태 확인), C11 StatuslineRenderer, C12 DashboardServer(localhost 127.0.0.1 읽기전용), C3 공유 usage export/import(VERIFIED_REUSE 검증·event_id dedup — **`usage.py`에 위치, CJ 단일 수정자**).
- **소유 경계**: `org_aggregator.py`/`statusline.py`/`dashboard.py` 소유. 전송(gitsync.py)은 **B 소유 파일 호출**(U3가 수정하지 않음). 공유 usage 코드는 `usage.py`(CJ 단일 수정자) 안에 있으므로 CJ가 작성.
  - **읽기전용 vs 상태 변경 구분**: C10/C11/C12 **집계·표현은 읽기전용**(쓰기·승인·게시 없음). 반면 **C3 공유 이벤트 import는 로컬 소유 usage 상태를 변경하는 쓰기 작업**이다 — 읽기전용이 아니며, VERIFIED_REUSE 검증·event_id dedup을 통과한 이벤트만 반영한다. S3 상태 조회 계약은 U2 소유 → **U3는 읽기만**(추정·게이트 재구현 금지).
- **비블로킹 규칙**: 계약(6 공유 이벤트, 7 S3 상태 조회, 8 OrgSnapshot) 확정 후 **골격은 모의 스냅샷으로 병렬**. 실데이터·시연은 U2 게시·pull 이후, 미검증은 **NOT_RUN**. **U3 미완이 P0/P1 종단을 막지 않는다**(단 필수 범위로서 완료 대상).
- **의존**: U0 계약, U2 S3 상태 조회 계약 + gitsync.py(전송 호출), C3(공유 usage).

### Q1 — 독립 QA·사용성·실행 증거 (C 윤여훈) — **횡단 트랙(코드 소유 Unit 아님)**
- **책임**: 각 Unit의 실제 실행·재현(사람 단독 CLI 재현 FR-SURF-2/3)·사용성·증거(PASS/FAIL/NOT_RUN) **독립 검토**. 개발 소유와 분리해 편향 없이 검증.
- **경계**: 소스 코드 소유·수정 아님. 테스트/증거 디렉터리 검토·기록. Build and Test 단계의 독립 검증 주체.

---

## 코드 조직 전략 (Greenfield, 제안 — 상세는 Code Generation)
- **Windows-native Python 단일 패키지 + 얇은 Agent Skill wrapper**(승인된 AD-Q6). 단일 배포 아님(로컬 CLI).
- 제안 레이아웃(확정은 Code Generation):
- **파일별 단일 수정자(single-writer) 원칙**(사용자 정정): 한 파일은 정확히 한 명이 수정. 다른 Unit은 **호출 계약**으로만 접근하며 그 파일을 편집하지 않는다(함수 추가만 허용해도 병합 충돌이 나므로 분담 편집 금지).
```
skillloop/                 # 파이썬 패키지 (application code, 워크스페이스 루트)
  descriptor.py            # C1                         — 수정자: CJ(U0)
  store.py                 # C2                         — 수정자: CJ(U0)
  usage.py                 # C3 (카운트 + 공유 이벤트 export/import·VERIFIED_REUSE 검증·dedup) — 수정자: **CJ 단일**
  envharness_p0.py         # C7 P0 harness (이중 mock index) — 수정자: CJ(U0)
  envharness_p1.py         # C7 P1 harness (보호 XLSX)       — 수정자: B(U2)
  cli.py                   # C8 — 수정자: **CJ 단일**. 타 Unit은 연결할 호출 계약(엔트리 시그니처)만 제공
  match.py                 # C5                         — 수정자: A(U1)
  reuse_service.py         # S1                         — 수정자: A(U1)
  experience_service.py    # S2                         — 수정자: B(U2)
  publish_pipeline.py      # S3 (+읽기전용 상태 조회 계약)  — 수정자: B(U2)
  replay.py                # C6                         — 수정자: B(U2)
  gitsync.py               # C4 (push_descriptors·push_shared_usage·pull·last_sync 전송) — 수정자: **B 단일**
                           #     (전송만; 공유 이벤트 검증·dedup은 usage.py=CJ 책임)
  org_aggregator.py        # C10 (읽기전용 집계)          — 수정자: CJ(U3)
  statusline.py            # C11 (읽기전용 표현)          — 수정자: CJ(U3)
  dashboard.py             # C12 (localhost 읽기전용)     — 수정자: CJ(U3)
  agent_skill/             # C9 wrapper (자연어→CLI)      — 수정자: CJ(U0)
tests/                     # Q1 검토 대상: PBT(Hypothesis)·process·contract·regression
```
- **환경 harness는 P0/P1 파일 분리**(`envharness_p0.py`=CJ, `envharness_p1.py`=B)로 단일 수정자 원칙 유지.
- `usage.py`·`cli.py`는 **CJ 단일 수정자**, `gitsync.py`는 **B 단일 수정자**로 통일(이전의 "함수별 분담" 표기를 폐기). 공유 이벤트 검증·dedup은 gitsync가 아니라 `usage.py`(CJ)에 위치.
- 실제 branch·Git 작업 경로·remote 등록·인증은 **미결정**(착수 게이트에서 공통 기준 SHA·경로 확인 시 확정).
