# P0 세 번의 재현 결과

동일 소스의 새 위치 checkout과 checkout/.venv에 선언 의존성을 설치했다. 기존 Codex session-context runtime 없이 업무 환경을 준비했다. 저장소 HEAD a22e176 위 현재 P0 수정본이며 소스 hash는 validation.json에 있다. 이후 P1 수정은 이 P0 검증 소스와 별개다.

| 검증 | 변화 조건 | 실제 결과 |
|---|---|---|
| 1 | 새 작업 폴더, 기본 요구 파일 | Claude 진입·실제 실패·MATCH·같은 venv 설치·독립 import·실적 1 PASS |
| 2 | 공백 경로, 주석/공백 포함 requirements | 재시도에서 같은 경로 PASS, 실적 1 |
| 3 | 한글 경로, 추가 무관 Skill | 같은 경로 PASS, 실적 1 |

각각 새 Claude 세션에 “이 프로젝트 requirements.txt의 패키지를 설치해줘”만 입력했다. 업무 요청 외 runtime 지침은 코드 수정·외부 사전 구현 접근 금지와 작업 보존/정직한 실행 보고였다. 2차 재시도부터는 셸 명령을 불필요하게 결합하지 않는 실행 지침을 추가했다. 정답 신호·Skill·성공 경로를 prompt로 주지 않았다.

첫 번째 2번 시도는 권한 거절과 Claude API ENOTFOUND로 설치 전에 중단됐다. agent_exit=1, import 실패, count=0이었다. attempt1-agent-2.json/attempt1-three-results.json에 보존했다. 같은 미설치 작업 환경을 초기화하지 않고 명령 허용 범위를 정합화하여 재시도했으며 이후 PASS다. '3번 시도 전부 한 번에 성공'이라고 주장하지 않는다.

3회 모두 requirements/store hash가 유지됐고 작업 venv가 남아 있다. 독립 Python import/version 검사와 usage event 검사를 실행했다. 각 log의 run_id에 실제 재사용 1건씩이며 서로 다른 로컬 usage 저장소다. 합산 조직 실적이나 원격 공유로 오인하지 않는다.

최신 P0 전체 회귀는 93 passed, exit 0이다. 실패 시도나 이전 버전 테스트 개수를 더한 수치가 아니다. 세션 로그에서 비공개 사고·인증정보를 제외하고 개인 작업 경로를 치환했다. 실행 원본은 로컬 재현 폴더에 보존했다.

정확한 한계: 대상은 여전히 승인된 단일 합성 패키지 1.0.0이다. 다른 패키지 일반화 증거는 없고 digest 승인 보호를 완화하지 않았다. 준비 도구는 checkout의 fixture를 사용하므로 wheel 단독 배포 지원은 주장하지 않는다. 이 결과는 P1 진행의 사용자 지정 P0 기준을 충족하지만 전체 제품 완료는 아니다.

재현 안내: aidlc-docs/construction/U0-P0/code/p0-reproduction.md. 핵심 명령은 저장소에서 scripts/prepare-p0.ps1 -Destination <새-작업폴더> 실행 후 작업 폴더에서 Claude 업무 요청이다.
