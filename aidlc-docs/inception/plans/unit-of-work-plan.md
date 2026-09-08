# Unit of Work Plan — Agent SkillLoop

**단계**: INCEPTION / Units Generation (Part 1 계획)
**작성일**: 2026-09-08
**깊이**: **최소(minimal)** — 승인된 Application Design 계약 기반, 사용자 제공 파라미터를 결정으로 반영
**근거**: 승인된 `application-design.md`(및 components/component-methods/services/component-dependency), `stories.md`, `execution-plan.md`

> 사용자 승인(2026-09-08)으로 아래 결정 파라미터가 확정되어 **계획 질문을 재개하지 않는다**(재질문 금지 지시). 남은 결정(프레임워크·상세 schema·로컬 Git 경로 등)은 per-unit 설계/Code Plan·NFR Requirements(minimal)로 이월.

## 결정 파라미터 (사용자 승인 — 재질문 없음)
- **앵커**: 9/8 **17:30 P0 샘플 실행**을 기준선으로 구성. P0 종단이 최우선 경로.
- **역할**: CJ=메인 통합·공통부 관리 / A 최호길·B 한석훈=승인된 Unit 개발 / C 윤여훈=독립 QA·사용성·실행 증거 검토(개발 아님, 유지).
- **Unit 수 고정 금지**: 사람 수(4)·컴포넌트 수(12)에 Unit 수를 맞추지 않는다.
- **P0 우선 명확화**: P0에 필요한 공통부·실행부의 **선행 계약·담당·수정 가능/금지 경로**를 먼저 고정.
- **비블로킹 경계**: UI·조직 집계·P1 전체 구현 완료가 **P0 실행을 막는 의존성이 되지 않도록** 구성.
- **착수 게이트 유지**: 실제 개발 착수는 해당 Unit의 필요한 설계·Code Plan 승인 + **공통 기준 SHA·작업 경로 확인** 후.

### 승인 시 정정 반영 (2026-09-08, 사용자)
- **U3 소유자 = CJ**('여력' 표기 폐기). UI·조직 집계는 승인된 **필수 범위**, P0 비블로킹 ≠ 선택 기능. **U2(B)는 Day2 대기 아님**(계약+게이트 충족 시 즉시 병행 착수).
- **파일별 단일 수정자**: `usage.py`=CJ(카운트+공유 이벤트), `cli.py`=CJ, `gitsync.py`=B(전송, dedup은 usage.py=CJ), `envharness_p0.py`=CJ / `envharness_p1.py`=B. '함수별 분담' 폐기. U3 집계·표현=읽기전용, C3 공유 이벤트 import=상태 변경(쓰기).
- **P0 착수 우선**: 계약 5는 **비블로킹**으로 정정. U0 전체 완료를 U1이 기다리지 않고, P0 최소 계약+로컬 저장·카운트·환경 인터페이스 확정 후 U0/U1 **병렬**.

---

## 계획 체크리스트 (Part 1 → Part 2)

### Part 1 — 계획 (본 문서)
- [x] 결정 파라미터 확정(사용자 승인) — 재질문 없음
- [x] 분해 방식 확정: **P0-우선 + 소유 경계 + 계약 동결** (사람/컴포넌트 수 비고정)
- [x] Unit 초안 정의(U0/U1/U2/U3 + QA 트랙 Q1)
- [x] 착수 순서·수정 가능/금지 경로·비블로킹 경계 정의

### Part 2 — 생성 (필수 산출물)
- [x] `application-design/unit-of-work.md` — Unit 정의·책임·소유·수정 경로·코드 조직 전략(Greenfield)
- [x] `application-design/unit-of-work-dependency.md` — Unit 의존성 매트릭스 + 계약 동결·착수 순서
- [x] `application-design/unit-of-work-story-map.md` — 스토리 ↔ Unit 매핑(모든 스토리 배정 확인)
- [x] Unit 경계·의존성 검증, 모든 스토리 배정 확인

---

## 분해 방식 (요약)
1. **공통 계약·도메인·저장·통합**을 한 Unit(U0)에 모아 CJ가 소유·동결 → 병렬 개발의 토대(NFR-INT-1). P0 blocking 최소셋 우선 제공.
2. **P0 재사용 실행부**(U1)를 A가 소유하여 17:30 종단 목표. U0 계약 초안 확정 시 병렬 착수.
3. **P1 경험·게시**(U2)를 B가 소유. U0 계약 + U1 재사용 경로 참고. **Day2 대기 아님** — 필요 계약(1·2·3·5)+승인 게이트 충족 시 U1과 병행 착수 가능.
4. **조직 집계·표현·재사용 이벤트 공유**(U3)는 **CJ 소유**('여력' 표기 폐기), **P0 비블로킹이나 승인된 필수 범위**(선택 기능 아님) — 계약 확정 후 골격 병렬(모의 스냅샷), 실데이터·시연은 U2 게시·pull 후(미확인 NOT_RUN). C는 개발 아님(횡단 QA).
5. **QA·실행 증거**(Q1)는 **횡단 트랙**(C 소유) — 코드 소유 Unit 아님. 전 Unit 교차 검토.

> 상세는 `unit-of-work.md` / `unit-of-work-dependency.md` / `unit-of-work-story-map.md`.
