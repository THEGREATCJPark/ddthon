# P0 (U0 P0 필수 + U1) — Tech Stack Decisions (minimal)

**단계**: CONSTRUCTION / NFR Requirements / P0
**작성일**: 2026-09-08
**근거**: 확정된 제약(Windows-native Python, 로컬 JSON) + 승인된 핵심 NFR + PBT partial(Hypothesis). 추가 대안 탐색 없음(사용자 지시).

> 세부 버전·패키지·CLI 문자열은 Code Plan에서 고정. 여기서는 **의존성·실행 환경·검증 도구**만 확정.

---

## 1. 언어·런타임
| 항목 | 결정 | 비고 |
|---|---|---|
| 언어 | **Python 3** (Windows-native) | 무설치 지향, 표준 라이브러리 우선 |
| 실행 형태 | 로컬 CLI(`skillloop`) + 얇은 Agent Skill wrapper | 서버·네트워크 서비스 없음(P0) |
| 최소 Python 버전 | Code Plan에서 고정(≥3.10 권장) | 팀 환경 합의 |

## 2. 저장·직렬화
| 항목 | 결정 |
|---|---|
| 저장 | **로컬 JSON 파일**(DB 엔진 미도입) |
| 직렬화 | 표준 `json` + **canonical 직렬화 규칙**(키 정렬·정규화, digest용) |
| 해시 | `hashlib` **SHA-256** |

## 3. P0 실행 의존성
| 목적 | 도구 | 비고 |
|---|---|---|
| 실제 설치 실행 | `pip`(subprocess 등) | 실제 종료코드·설치·버전 관찰 |
| 환경 재현 | envharness_p0(로컬 mock index 2종) | 오프라인·결정적. 외부 네트워크 미의존 |
| 설치 검증 | 배포 패키지 조회 + 합성 패키지 import | clean 환경 전제 |

## 4. 테스트·검증 도구
| 목적 | 도구 | 강제 |
|---|---|---|
| Property-Based Testing | **Hypothesis** | PBT-02/03/07/08/09(round-trip·invariant·generator·shrinking/reproducibility·framework) |
| 단위·프로세스·계약·회귀 | 표준 테스트 러너(pytest 권장, Code Plan 확정) | 핵심 규칙 검증 |

## 5. 미결정(Code Plan 이월)
- 구체 버전 핀·의존성 목록·가상환경 방식, pip 격리 실행 방식, `new_execution_id` 구현, JSON 파일 경로·락, CLI 인자 문자열, 합성 패키지 정의.
