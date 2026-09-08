# P0 관찰·검색 결함 재검증

기준 main a22e176 위 미커밋 수정본. 사용자 요청에 따른 기존 승인 P0 결함 수정이며 전체 제품 완료 판정은 아니다.

## 피드백 판정과 수정

raw pip 오류를 canonical signature로 잘못 전달한 초기 검색은 결함이다. 당시 스캔 0건에는 작업 store 미지정 문제도 포함한다. 같은 사용자 로그의 후속 apply-requirements는 실제 MATCH·설치·import·reuse+1을 완료했으므로 과거 전체 e2e를 FAIL로 덮어쓰지 않는다.

C8에서 실제 pip 종료코드·stderr·요청 대상의 일치를 확인해 기존 FailureObservation 신호로 정규화한다. 패키지 이름과 버전, 대소문자/구분자 표기를 처리하며 Skill id나 해결 index를 선택하지 않는다. apply-requirements와 기존 P0 실패 관찰은 같은 helper를 사용한다. 독립 검색은 --pip-stderr / --exit-code / --target / --store로 관찰을 전달한다. raw 오류를 --signature로 잘못 넘기면 INVALID_SIGNAL이며 검색하지 않는다.

미인식 오류·다른 대상·성공 종료를 공급 실패로 위장하지 않는다. 현재 실행 지원은 선언된 합성 패키지 범위이며 임의 requirements 문법/패키지 일반화 완료를 주장하지 않는다. C9의 정답 canonical 문자열 예시를 제거했고 A matcher/reuse_service는 수정하지 않았다.

## 실제 검증

- 정규화 CLI·상태줄 대상 검사: 21 passed, exit 0.
- apply-requirements / run-p0 e2e / matcher / reuse_service 회귀: 22 passed, exit 0. 이번 수정 후 전체 suite를 다시 실행한 것은 아니다. 이전 86 passed는 이전 소스 검증 기록으로 보존한다.
- 새 Claude Code 세션에 “이 프로젝트 requirements.txt의 패키지를 설치해줘” 한 문장만 전달. operator가 먼저 새 작업 venv·합성 실패 공급원·기존 Skill 저장소 연결을 준비했고, Agent 업무 실행은 그 환경을 유지했다. 기존 사용자 venv는 초기화하지 않았다.
- Skill 자동 로드 → apply-requirements 내부 실제 pip exit 1 → canonical observation → MATCH → 실제 설치·버전·import → reuse 1→2, candidate_delta=0. 새 run_id: 457588103ff547ed936309e715d30487.
- Agent의 별도 작업 Python 프로세스에서 version=1.0.0/import_ok=True. CJ도 새 환경·기존 환경을 각각 독립 확인. store·requirements hash 전후 동일.
- 상태줄 명령 출력도 실제 검증 2회를 표시한다. 기존 네 줄 표시는 사용자 확인 이력이 있으나 이번 1→2 화면 육안 확인/스크린샷은 수행하지 않았다.

## 권한·증거 구분

Agent가 먼저 요청한 별도 pip 명령은 stderr 파일 리다이렉션을 포함했고 테스트 세션 권한에서 거절되었다. 그 호출은 실제 pip 실패 근거가 아니다. 이어 허용된 apply-requirements 내부의 실제 pip 실행이 공급 실패를 관찰했다. 거절 기록도 agent-session.json에 보존했다. run-p0 대체나 권한 우회 설정 변경은 없었다.

observed-pip-errors.txt는 해당 실제 실행 출력의 ERROR 줄을 그대로 추출한 파일이다. standalone-match.txt는 이 관찰 파일로 실행한 독립 읽기전용 검색 결과이며 별도의 pip 재실행을 주장하지 않는다.

agent-session.json은 도구 호출·출력·최종 답변·권한 거절을 포함하며 개인 경로는 역할 이름으로 치환하고 비공개 사고·인증은 제외했다. independent-verification.json은 count 1→2와 환경 보존, regression.txt/validation.json은 회귀 결과와 소스 hash, status-after.txt는 현재 로컬 상태줄이다.

판정: 승인된 합성 P0 자연어 수용 경로 PASS. CONSTRUCTION 코드 결과 REVIEW REQUIRED 유지. P1 통합·원격 공유·전체 Build and Test 미완료. 공식 규칙 변경 및 과거 기록 소급 수정 없음.
