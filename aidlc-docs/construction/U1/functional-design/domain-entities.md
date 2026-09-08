# U1 — Domain Entities (Functional Design, minimal)

**단계**: CONSTRUCTION / Functional Design / U1 (P0 재사용 실행)
**작성일**: 2026-09-08
**소유**: A 최호길 (`match.py` C5, `reuse_service.py` S1). U0 계약(1·3·4)·envharness_p0는 **호출만**.

> U1은 새 지속 엔티티를 만들지 않는다. U0 엔티티(SkillDescriptor/Applicability/SearchOutcome/ReuseEvidence)를 소비하고, 아래 **실행 시 값 객체**를 다룬다.

---

## E-U1-1. FailureObservation (관찰된 실패 신호)
| 필드 | 설명 |
|---|---|
| `command` | 실패한 명령(예: pip install 대상) |
| `target_pkg` | 대상 패키지명 |
| `error_signature` | 정규화된 에러 시그니처(결정적 매칭 입력) |
| `exit_code` | 실패 종료코드 |

> C5는 이 신호를 descriptor.applicability.signals와 대조한다.

## E-U1-2. MatchDecision (C5 내부 → SearchOutcome로 반환)
| 필드 | 설명 |
|---|---|
| `valid_candidates` | applicability를 만족하는 후보 목록 |
| `ranking_key` | 안정 정렬 키(예: 신호 적합도 → version → id 사전식) |
| `tie_break` | 동점 시 결정적 규칙(예: 최신 version, 그다음 id 사전식) |
| `selected` | 선택된 단일 후보 `{id,version,digest}` |
| `rationale` | 선택 근거 문구 |

- valid_candidates ≥ 1 → SearchOutcome.MATCH(selected + rationale + ranked).
- valid_candidates = 0 → SearchOutcome.NO_MATCH.

## E-U1-3. ApplicationResult (S1 적용 결과)
| 필드 | 설명 |
|---|---|
| `applied_procedure` | 실행한 절차 요약 |
| `pip_exit_code` | 실제 pip 설치 종료코드 |
| `installed_check` | 대상 배포 패키지 설치 여부 |
| `version_check` | 요구 버전 충족 여부 |
| `import_check` | 합성 패키지 import 성공 여부 |
| `is_real_success` | 위 검증들이 모두 충족될 때만 true |
| `run_id` | **논리적 실행 식별자** — 입력(observation)이 아니라 한 번의 실제 실행을 식별. 새 논리적 실행=새 run_id, 동일 실행의 재검증·재시도·재시작=기존 유지. 같은 문제의 **다른 환경 재사용은 다른 run_id**(각각 +1). 생성·보존 방식은 Code Plan |

## E-U1-4. VerificationContext (검증 전제)
| 필드 | 설명 |
|---|---|
| `clean_env` | 대상 패키지 미설치 확인(envharness_p0.is_clean) |
| `index_source` | 실제 사용 index/옵션 — **선택된 descriptor.procedure에서 취득**(harness가 정답 index를 강제하지 않음) |

> 성공 판정은 실제 설치·버전·import 확인으로만 성립. **성공 index 선택·전역 Python 존재는 성공 근거에서 제외.** 적용 설정은 매칭 성공이 아니라 선택된 descriptor의 절차가 결정.
