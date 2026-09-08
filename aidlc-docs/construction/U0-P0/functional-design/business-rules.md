# U0 P0 — Business Rules (Functional Design, minimal)

**단계**: CONSTRUCTION / Functional Design / U0 P0 필수
**작성일**: 2026-09-08

> 계약 1·2·3·4의 불변식. PBT partial(PBT-02/03) 및 dedup·CONFLICT invariant는 테스트로 검증.

---

## R1. Digest 규칙 (계약 1)
- digest = SHA-256( canonical_json( content_without_digest ) ).
- **content_without_digest** = `{id, version, origin, applicability, procedure}` (digest 필드·usage 전부 제외).
- canonical JSON: 객체 키 사전식 정렬, 안정적 공백·숫자·유니코드 정규화, 배열 순서 보존.
- **불변식**: `deserialize(serialize(d)).digest == d.digest` (round-trip 동일 — PBT-02/03).
- usage(actual_reuse/demo_seed) 변경은 digest에 **영향 없음**.

## R2. CONFLICT 판정 (계약 2)
- 동일 `(id, version)` + **다른 digest** → **CONFLICT**.
- **다른 version** → CONFLICT 아님(독립 레코드).
- 동일 `(id, version)` + **동일 digest** → **DEDUP(중복 저장 아님, no-op)**. **usage 병합·카운트 변경 없음.**
- CONFLICT 시 P0 정책: 자동 덮어쓰기 금지 — 거부/보류하고 사유 반환(사용자·상위 계층 판단).

## R3. 카운트 규칙 (계약 3, NFR-RES-1 idempotent)
- **쓰기 주체는 C3 단독**: 실제 재사용 기록은 오직 `C3.record_actual_reuse(...)`로 이뤄진다. **C2는 카운트를 쓰지 않는다**(descriptor dedup이 usage를 건드리지 않음, R2).
- `actual_reuse += 1`은 **실제 적용 + 효과 검증 성공(is_real_success=true)** 일 때만.
- **run_id 기반 dedup = 실행(execution) 단위**: 동일 `run_id`(동일 논리적 실행의 재검증·재시도·재시작)의 재기록만 no-op. **같은 문제라도 다른 환경에서의 실제 재사용은 다른 run_id → 각각 +1.**(입력만으로 dedup 금지)
- `demo_seed=true`(미리 만든 실적)는 actual_reuse에 반영하지 않음. **사전 적재 Skill을 실제로 재사용한 성공은 demo_seed=false로 실적 반영**(FR-UI-3 표시 구분 근거).
- 검증 실패·NO_MATCH는 카운트 없음.

## R4. 검색 결과 규칙 (계약 4, C5 소비)
- 결정적: 동일 입력 → 동일 SearchOutcome.
- 유효 후보 ≥ 1 → **MATCH**(안정 정렬·동점 규칙으로 단일 선택 + 근거·ranked_candidates).
- 유효 후보 = 0 → **NO_MATCH(reason)**.
- 검색 오류/timeout/미호출은 ERROR/TIMEOUT/NOT_INVOKED로 **NO_MATCH와 구분**(허위 성공·허위 매칭 금지).

## R5. run-p0 오케스트레이션 규칙
- 순서: 실패 index 재현 → C5.search → (MATCH면) S1.apply(**선택된 descriptor.procedure 기준**) → 검증 → 성공 시 **C3.record_actual_reuse** → 결과 출력.
- **정답 환경 강제 금지**: MATCH가 곧바로 허용 index를 강제 선택하지 않는다. harness는 두 index를 제공만 하고 적용 설정은 descriptor.procedure가 결정(정합화 3). 실제 실패·설치·버전·import 검증 기준 유지.
- NO_MATCH/ERROR/TIMEOUT/검증 실패 → 카운트 없이 명확한 상태 출력(성공으로 위장 금지).

## R6. 보안·무결성 (NFR-SEC, 설계 반영)
- 시연 데이터는 합성만. 사내 원본·secret 미포함.
- 입력 descriptor는 저장 전 스키마·digest 무결성 검증(FR-SKILL-4).
- 원격 Skill 자동 실행 금지(P0 범위 밖이나 계약상 유지).
