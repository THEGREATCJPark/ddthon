# P0/P1 새 Cold 검증 — 2026-09-09 오전

**기능: 세 건 PASS. 사용자 응답: 개선 필요.** 승인된 Build & Test 추가 검증이며 제품/C9 소스는 d8c45cb에서 고정했다. 이전 실행을 재포장한 로그가 아니다.

| 실행 | 소요 | 실제 결과 | 실적·후보 |
| --- | --- | --- | --- |
| P0 새 작업 venv | 46.5초 | 실제 공급 실패 → MATCH → 설치1.0.0 → 같은 Python 독립 import PASS | reuse1, store 변화0 |
| P1 Cold1 | 156.3초 | 1200/1350/1500 → 예상1650, PNG·원본 hash 유지 | 후보1, reuse0, PROPOSED |
| P1 Cold2 | 146.1초 | 다른 시트/행/열의2100/2250/2400 → 예상2550, PNG·원본 hash 유지 | 후보1, reuse0, PROPOSED |

P0 Cold는 패키지 미설치+검증된 기존 Skill이 있는 새 작업 환경이다. P1 두 환경에는 관련 Excel Skill이 없었다. 두 번째 폴더 이름이 기존 준비 도구의 `warm`이어도 이번에는 pull/기존후보 주입 없이 시작했으므로 실제 검증은 **Cold2**다. 새 세션 각각에 한국어 업무 요청만 제공했고 환경 사실/실행 범위 지침 외에 해결 방법·예상값·표현 요구를 추가하지 않았다.

## 결과와 원문

- [기계 검사 결과](validation.json), [응답 품질 직접 검토](response-review.md).
- P0: [전체 대화·도구 로그](p0-transcript.md), [Agent 안내만](p0-responses.md), [구조화 원문](p0-trace.json), [실제 상태·독립 import](p0-status.json).
- P1 Cold1: [전체 대화·도구 로그](p1-cold-1-transcript.md), [Agent 안내만](p1-cold-1-responses.md), [구조화 원문](p1-cold-1-trace.json), [제품 실제 반환값](p1-cold-1-product-reports.json), [상태](p1-cold-1-status.json).
- P1 Cold2: [전체 대화·도구 로그](p1-cold-2-transcript.md), [Agent 안내만](p1-cold-2-responses.md), [구조화 원문](p1-cold-2-trace.json), [제품 실제 반환값](p1-cold-2-product-reports.json), [상태](p1-cold-2-status.json).
- 각 stderr·permissions·runner 출력과 run-context도 보존했다. 표시용 transcript는 원문 trace에서 역할을 구분해 만든 파생본이며, Skill 로드로 삽입된 user/tool 내용은 Agent의 발언으로 평가하지 않았다. 원본 JSONL은 run-context에 기록한 로컬 TEMP 경로에 보존하며, 공개 trace는 비공개 thinking/signature를 제외했다. 중간 실패는 삭제하지 않았다.

P0 tool error1은 기대된 최초 pip 공급 실패다. P1 Cold1의7건은 정상 대기2/권한 거절2/입력 형식3, Cold2의6건은 정상 대기1/권한 거절1/입력 형식4다. 이는 최종 기능 실패7회/6회를 뜻하지 않는다. 성공은 원문, 저장소, usage, 파일 hash와 별도 검사를 대조해 판단했다. 두 실제 PNG도 육안 확인했다.

## 재검사와 환경 정리

`python result/cold-review-20260909/verify.py`는 저장된 실제 결과를 재검사한다(새 Agent 실행 아님). 새로운 수용 테스트가 필요하면 `python result/cold-review-20260909/run.py <새-증거-폴더>`로 실행한다. 이전 로그 덮어쓰기를 거절한다. 준비 도구는 기존 계약을 사용하며 새 업무 환경만 만들고 실제 Excel이 필요하다.

이번 준비 도구의 STOP 프로토콜이 완료됐고 소유 Excel PID25332 종료를 확인했다. 다른 사용자 Excel은 종료하지 않았다. 제품/C9/공식 AI-DLC 규칙 변경 없음. 최초 운영자 로그 표시에서 cp949 오류, 파생 transcript 생성에서 문법 오류가 있었으며 UTF-8/형식 정정 후 원래 trace로 생성했다. 이들은 Agent 업무 실행 실패와 구분한다.

## 범위

동일 Windows PC의 새 Claude 세션3개다. B PC 재현·새 후보 사람 승인/Replay/원격 게시를 이번에 실행하지 않았다. P1은 현재 지원된 Excel 접근 어댑터이고 P0는 기본 단일 패키지 fixture다. 이번 결과만으로 임의 환경 전반의 성공률이나 성능 SLA를 주장하지 않는다. 기존 전체142PASS/2SKIP와 이번 Agent3건은 합산하지 않는다.
