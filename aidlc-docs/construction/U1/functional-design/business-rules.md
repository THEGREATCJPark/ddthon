# U1 — Business Rules (Functional Design, minimal)

**단계**: CONSTRUCTION / Functional Design / U1 (P0 재사용 실행)
**작성일**: 2026-09-08
**대상 스토리**: US-P0-1 / FR-P0, FR-MATCH, FR-USAGE-1·2, NFR-SEC-4

---

## RU1. 검색·매칭 (C5, 결정적)
- 동일 입력(FailureObservation + Store 상태) → 동일 SearchOutcome.
- **유효 후보 판정**: applicability.signals가 관찰 실패 신호를 만족하는 descriptor.
- **다중 유효 후보 ≠ NO_MATCH**: 안정 정렬(신호 적합도 → version → id 사전식) + 결정적 동점 규칙으로 **단일 선택**하고 근거(ranked_candidates 포함) 반환.
- **NO_MATCH는 유효 후보 0건일 때만.**
- 검색 오류·timeout·미호출 → ERROR/TIMEOUT/NOT_INVOKED로 반환(NO_MATCH·성공과 혼동 금지).
- 매칭은 **근거 없이 성공을 주장하지 않는다**(FR-MATCH: 근거 제시 의무).

## RU2. 적용·검증 (S1) — "실제 성공" 정의
성공(is_real_success=true)은 **다음을 모두 충족**할 때만:
1. clean 환경 확인(대상 패키지 미설치, `envharness_p0.is_clean`).
2. 실제 pip 설치 **종료코드 성공**.
3. **대상 배포 패키지 설치 여부 + 요구 버전** 확인.
4. 합성 패키지의 경우 **import 성공** 확인.

**오판 방지 규칙**:
- 기존/전역 Python 설치로 인한 성공을 배제(1번 clean 전제).
- **성공 index를 선택했다는 사실 자체는 성공 근거가 아니다** — 실제 실행 결과로만 판정.
- **적용 설정은 선택된 descriptor.procedure에서 취득**한다. 매칭 성공이 harness의 정답 index를 강제 선택하는 흐름이 아니다(정합화 3). harness는 두 index를 제공만 한다.

## RU3. 카운트 연동 (FR-USAGE-1·2, U0 계약 3) — **쓰기 주체는 C3**
- 성공 시 상위(run-p0)가 **`C3.record_actual_reuse(evidence)`** 호출(C2 아님). C2 dedup은 usage·카운트를 건드리지 않는다.
- is_real_success=true 且 demo_seed=false 且 **새 논리적 실행(run_id)** → **+1**.
- **run_id는 실행 단위**: 동일 실행의 재검증·재시도·재시작만 no-op. **같은 문제라도 다른 환경의 실제 재사용은 다른 run_id → 각각 +1**(입력만으로 dedup 금지, NFR-RES-1).
- **사전 적재 Skill을 실제로 재사용한 성공은 demo_seed=false로 실적 반영**. DEMO_SEED 제외는 미리 만든 실적에만 적용.
- 검증 실패/NO_MATCH → 카운트 없음, 상태만 기록.

## RU4. 시나리오 비의존 (S1 설계 원칙)
- S1은 "pip 설치 실패" 유형의 **적용+검증**을 일반 절차로 처리(특정 게임/데모에 하드코딩 금지). P1의 파일접근 유형도 동일 인터페이스로 재사용 가능하도록 경계 유지.

## RU5. 보안 (NFR-SEC-4)
- 원격/미검증 Skill의 자동 실행 금지. P0 시연은 합성 descriptor + 로컬 mock index만 사용.
