# P0 (U0 P0 필수 + U1) — NFR Requirements (minimal)

**단계**: CONSTRUCTION / NFR Requirements / P0
**작성일**: 2026-09-08
**범위**: US-P0-1 경로(U0 P0 필수 + U1). NFR Design·Infrastructure Design은 SKIP(승인). 본 문서는 **의존성·실행 환경·필수 검증 항목**만 간결히 기술.

> 승인된 핵심 NFR(NFR-SEC-1~4, NFR-RES-1~4)과 PBT partial은 설계·테스트에 반영(SKIP-BOUNDARY-1). 신규 NFR을 추가하지 않는다.

---

## 1. 의존성 (P0 착수 전 확정 필요)
- **U0 → U1 계약(선행)**: 계약 1(digest·직렬화), 계약 3(C3.record_actual_reuse·build_evidence·run_id 실행 dedup), 계약 4(SearchOutcome/Applicability), envharness_p0(prepare/setup_failing/setup_allow/is_clean).
- **외부 의존**: Python 3, `pip`, 표준 라이브러리(`json`,`hashlib`,`subprocess`), 테스트에 Hypothesis. **외부 네트워크·사내 데이터·secret 미의존**.
- **파일 소유(단일 수정자)**: descriptor.py/store.py/usage.py/envharness_p0.py/cli.py = CJ, match.py/reuse_service.py = A.

## 2. 실행 환경
- Windows-native, 로컬 CLI. 오프라인 결정적 실행(이중 mock index).
- **clean 환경 전제**: 대상 패키지 미설치 상태에서 실제 pip 실행으로 실패·성공 관찰. 전역 Python·기존 설치로 인한 오판 배제.
- 데이터: 합성 descriptor + 로컬 JSON. DEMO_SEED(미리 만든 실적)와 실제 재사용 실적 구분.

## 3. 필수 검증 항목 (P0 완료 기준)
| # | 항목 | 근거 | 판정 |
|---|---|---|---|
| V1 | 직렬화 round-trip 후 digest 동일 | PBT-02/03, R1 | Hypothesis property |
| V2 | digest는 불변 content만 대상(usage 변경 무영향) | R1 | property/unit |
| V3 | CONFLICT: 동일 (id,version)+다른 digest만, 다른 version은 아님 | R2 | unit |
| V4 | DEDUP은 usage 병합·카운트 변경 없음(**C2는 카운트 미기록**) | R2, 정합화1 | unit |
| V5 | 검색 결정성 + 다중 유효 후보→안정 선택(NO_MATCH는 0건만) | R4, RU1 | unit/property |
| V6 | 검색 오류/timeout/미호출을 NO_MATCH·성공과 구분 | R4 | unit |
| V7 | "실제 성공" = clean + pip 종료코드 + 설치·버전 + (합성)import | RU2 | integration(run-p0) |
| V8 | 성공 index 선택 자체는 성공 근거 아님(적용 설정=descriptor.procedure) | RU2, 정합화3 | integration |
| V9 | 카운트 쓰기 주체=C3 단독, 실제 성공만 +1 | R3, 정합화1 | unit/integration |
| V10 | run_id=실행 단위 dedup: 재검증·재시작 중복 +1 방지, 다른 환경 재사용은 각각 +1 | R3, RU3, 정합화2, NFR-RES-1 | property/unit |
| V11 | 사전 적재 Skill의 실제 재사용 성공은 실적 반영(demo_seed=false) | R3, 정합화2 | unit |
| V12 | run-p0 실제 샘플 실행 = 실패→적용→검증→reuse+1 (17:30 목표) | US-P0-1 | e2e 데모, 실행 증거 |

## 4. 보안·복원력 (반영, 신규 아님)
- NFR-SEC-1(secret·원본 비표시), SEC-2(읽기전용 경계 — P0 범위 밖이나 유지), SEC-3(입력·무결성 검증), SEC-4(원칙적으로 원격 Skill 명시적 확인; 2026-09-09 승인된 P0 동일 요청/exact 정책 예외는 p0-scoped-auto-reuse-code-generation-plan.md 참조).
- NFR-RES-1(중복 방지=run_id dedup), RES-2~4(충돌·재시작 보존 — P0는 로컬 저장 무결성 중심).

## 5. 성능·규모
- P0는 단일 로컬 실행·소량 데이터. 정량 성능 목표 없음(해당 없음). 결정성·재현성이 우선.

## 6. 미결정(Code Plan 이월)
- 버전 핀·pip 격리 방식·`new_execution_id` 구현·JSON 경로/락·CLI 문자열·합성 패키지 정의.
