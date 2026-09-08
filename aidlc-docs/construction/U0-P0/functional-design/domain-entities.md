# U0 P0 — Domain Entities (Functional Design, minimal)

**단계**: CONSTRUCTION / Functional Design / U0 P0 필수
**작성일**: 2026-09-08
**기술 비의존**: 저장은 로컬 JSON 파일(확정), 세부 코드 구성은 Code Plan.

> 소유 경계: content = 불변(digest 대상), usage = 가변(카운트·표식). 두 경계를 파일·갱신 경로에서 분리 유지.

---

## E1. SkillDescriptor
| 부분 | 필드 | 설명 | 가변성 |
|---|---|---|---|
| **content(불변)** | `id` | Skill 식별자(문자열) | 불변 |
| | `version` | 버전(문자열, 예: semver 또는 정수 증가) | 불변 |
| | `digest` | content(=이 표에서 digest·usage 제외분)의 SHA-256 | 파생·불변 |
| | `origin` | 생성 출처(작성자·세션·근거 링크) | 불변 |
| | `applicability` | 적용 판별 근거(→ E2) | 불변 |
| | `procedure` | 재현 절차(순서 있는 단계 목록) | 불변 |
| **usage(가변)** | `actual_reuse` | 실제 검증된 재사용 횟수(정수) | 가변 |
| | `demo_seed` | 사전 적재/시연 표식(bool) — 실적과 분리 | 가변 |

- **digest 입력**: `{id, version, origin, applicability, procedure}` — **`digest` 필드 자체·`usage` 전부 제외**. canonical JSON(키 정렬·공백/인코딩 정규화) 직렬화 후 SHA-256.
- **정체성(identity)**: `(id, version)`. 동일 (id,version)에서 digest가 다르면 CONFLICT(→ business-rules R2).

## E2. Applicability
| 필드 | 설명 |
|---|---|
| `signals` | 매칭 신호 집합(예: 실패 명령 패턴, 에러 시그니처, 대상 패키지명) |
| `constraints` | 적용 전제(예: OS/도구 조건) — P0 최소에서는 선택 |
| `rationale_template` | 매칭 시 근거 문구 생성용 |

> C5 검색이 **관찰된 실패 신호**와 `signals`를 결정적으로 대조하는 데 사용.

## E3. SearchOutcome (C5 반환 규격 — 계약 4)
| variant | 필드 | 의미 |
|---|---|---|
| `MATCH` | `{descriptor_ref{id,version,digest}, rationale, ranked_candidates[]}` | 유효 후보 중 안정 정렬·동점 규칙으로 선택된 단일 후보 + 근거 |
| `NO_MATCH` | `{reason}` | **유효 후보 0건**일 때만 |
| `ERROR` | `{error}` | 검색 내부 오류 |
| `TIMEOUT` | `{limit}` | 시간 초과 |
| `NOT_INVOKED` | `{}` | 검색이 호출되지 않음 |

> 다중 유효 후보는 NO_MATCH가 **아니다** — MATCH로 선택하고 `ranked_candidates`에 정렬 근거를 남긴다.

## E4. ReuseEvidence (C3 기록 규격 — 계약 3)
| 필드 | 설명 |
|---|---|
| `skill_ref` | `{id, version, digest}` (정확한 참조) |
| `is_real_success` | 실제 적용+검증 성공 여부(bool) |
| `verification` | 검증 방법·결과(pip 종료코드, 설치·버전 확인, import 확인) |
| `run_id` | **논리적 실행(execution) 식별자** — 입력(문제/observation)이 아니라 **한 번의 실제 실행**을 식별. 새 논리적 실행 = 새 run_id, 동일 실행의 재검증·재시도·재시작 = 기존 run_id 유지 |
| `demo_seed` | **미리 만든 실적**(사전 적재된 usage)인지 표식. 사전 적재 Skill을 **실제로 재사용한 성공**은 demo_seed=false(실적 반영) |
| `timestamp` | 기록 시각(UTC ISO 8601) |

> **run_id 의미 확정**: 같은 문제를 **다른 환경에서 실제 재사용**한 경우는 **서로 다른 논리적 실행**이므로 각각 +1로 반영된다(입력만으로 dedup하지 않는다). 중복 제외는 오직 **동일 실행의 반복 기록**에만 적용. 구체 생성·보존 방식은 Code Plan.

## E5. SkillStore 저장 모델 (C2 — 계약 2, P0는 로컬만)
- 로컬 JSON 파일. 논리 키 `(id, version)`. 레코드 = content(불변) + usage(가변) 분리 보관.
- 연산(계약): `get(id,version)`, `list()`, `put(descriptor) -> {STORED | CONFLICT | DEDUP}`.
- **C2는 카운트를 쓰지 않는다**: descriptor `put` dedup은 **usage를 병합하거나 actual_reuse를 변경하지 않는다**(content 정체성만 판정). 실제 재사용 기록은 **C3.record_actual_reuse가 유일한 쓰기 주체**(→ E4-note, R3).
- content 갱신과 usage 갱신 경로를 분리. usage 쓰기는 C3(`usage.py`=CJ) 소유.

## E6. Environment (envharness_p0)
- **이중 mock index**: `failing_index`(대상 패키지 없음) / `allow_index`(무해한 패키지 존재).
- clean 환경 개념: 대상 패키지가 사전 설치되지 않은 상태에서 실제 pip 실행 결과로 실패·성공을 관찰.
