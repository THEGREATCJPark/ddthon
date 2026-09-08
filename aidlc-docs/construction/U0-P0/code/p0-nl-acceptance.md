# P0 자연어 업무 요청 — 구현·수용 검증

상태: **Code Generation Part 2 완료 / REVIEW REQUIRED**.
근거: 사용자 승인된 p0-nl-acceptance-plan.md 개정 2, FR-P0/FR-MATCH/FR-USAGE, US-P0-1.
기준 a22e176 + validation-manifest.json의 소스 변경 해시. 아직 이 변경은 새 커밋·push로 배포하지 않았다.

## 실제로 달라진 것

일반 설치 요청을 run-p0로 대체하지 않는다. 새 apply-requirements는 지정한 기존 작업 venv에서 requirements 설치를 실제 시도하고, 공급 실패가 관찰되면 기존 C5 검색 → S1 적용/검증 → C3 실적 기록을 연결한다. 설치한 환경을 보존한다.

- 준비 도구는 업무 요청 이전에 별도 프로젝트·venv·로컬 Skill 두 건·공급 경로를 준비한다. 성공 이력은 미리 만들지 않는다.
- 실행 명령에서는 prepare/venv 생성/seed/패키지 삭제를 하지 않는다.
- 지원 입력은 skillloop-demo-pkg==1.0.0 한 건이다. 범위 밖은 UNSUPPORTED_REQUIREMENTS. 임의 패키지 지원으로 확대하지 않았다.
- 지정 venv/Python/pip와 기존 store를 확인하며, 공급 오류와 기타 pip 오류를 구별한다.
- 선택 descriptor의 content digest, action/target을 검사한다. 현재 무인 적용은 기존 승인 합성 content의 exact digest 하나로 제한된다. 그 외는 CONFIRMATION_REQUIRED이며 원격 승인 흐름을 새로 구현한 것이 아니다.
- 첫 설치가 바로 성공하거나 이미 설치돼 있으면 INSTALL_OK_NO_REUSE. 복구 성공만 카운트하며 기존 run_id dedup을 사용한다.
- A/B 코드와 기존 run-p0 본문은 변경하지 않았다.

## 재현 방법 — 새 작업 환경 준비 후 Claude 실행

제품 checkout에서 선언된 의존성을 설치한다. 개발/제품 설치와 모델 호출은 네트워크를 사용할 수 있으며, 합성 업무 설치·복구는 로컬 공급 경로만 사용한다.

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e . -r requirements-dev.txt
.\.venv\Scripts\python.exe tests/prepare_p0_work.py C:\work\skillloop-p0
cd C:\work\skillloop-p0
claude
~~~

준비 도구는 기존 디렉터리를 덮어쓰지 않으므로 새 경로를 지정한다. Claude Code/Bedrock 인증은 이미 설정돼 있어야 한다. 해당 프로젝트의 Skill을 로드하고 필요한 작업 Python/제품 CLI 실행 요청을 허용한다. 사용자 비밀 설정을 복사하지 않는다.

사용자 메시지는 한 문장:

> 이 프로젝트 requirements.txt의 패키지를 설치하고, 실제로 사용할 수 있는지 확인해줘.

product_python/work_python/store/usage는 skillloop-work.json에 있다. CLI 단독 재현:

~~~text
<product_python> -m skillloop apply-requirements --requirements <requirements> --python <work_python> --store <store> --usage <usage>
~~~

출력된 run_id를 같은 실행 재시도에 --run-id로 전달한다. 이미 설치된 작업 환경의 재확인은 실적을 추가하지 않는다. 설치 결과를 제거해 실패 장면을 만들지 말고 새 테스트는 준비 도구로 새 프로젝트를 만든다.

## 실제 실행 결과

| 확인 | 결과 |
|---|---|
| 새 Claude 세션의 자연어 요청 | Skill 도구로 skillloop 자동 선택 |
| 일반 pip 설치 | 요청 작업 venv에서 실제 공급 실패, exit 1 |
| 검색 | 관련/무관 Skill 중 관련 exact Skill MATCH |
| S1 검증 | pip exit 0, 설치·버전·import true |
| C3 | reuse=1, counted=True, reason=ok |
| 별도 프로세스 확인 | 같은 작업 Python import 성공, version 1.0.0 |
| 보존 | requirements/Skill store 해시 동일, venv 잔존, candidate +0 |
| 설치 후 새 세션 | INSTALL_OK_NO_REUSE, 실적 1 유지 |
| 신규 관련 테스트 | 14 passed |
| 깨끗한 snapshot 전체 | 80 passed, 0 failed, 0 skipped (기존 66 포함) |

테스트 snapshot은 git archive a22e176에 승인 범위의 변경 파일만 덮어씌워 구성했다. 별도 깨끗한 Python 3.14 venv에 pyproject 및 requirements-dev 선언만 설치했다. 원래 의존성 상태에서 setuptools.build_meta 부재를 실제 재현한 뒤 의존성을 정합화했다. 합성 wheel 캐시 없이 전체 테스트가 생성·실행했다.

명령: python -m pytest tests/test_apply_requirements.py -q / python -m pytest -q.
버전·대상 코드 해시·실제 로그·Agent 도구 기록·독립 확인은 result/p0-nl/에 있다. 개인정보 경로는 토큰으로 치환했고 thinking/auth metadata는 제출 증거에서 제외했다.

1차 Agent 실행은 테스트 권한 설정 문제로 중단됐다. 2차는 다중 행 명령 1건 거부 후 동일 명령을 한 줄로 재시도해 성공했다. 3차는 설치된 환경 확인이며 새로운 Cold 성공으로 집계하지 않는다. 거부 기록은 agent-sessions.json에 보존했다.

## 남은 범위와 검토

- P1 A/B 통합·Replay·게시·Git 왕복 및 조직 상태 실연결: 별도 후속 작업.
- 임의 패키지·실제 사내 시스템 및 원격 Skill 실행: 이번 PASS 범위 아님.
- Claude 하단 상태줄/화면 캡처·브라우저 육안: 이번 검증에 포함하지 않음. 실제 명령/결과를 증거로 보존했고 화면을 연출하지 않았다.
- README/EVALUATION 사용자 변경은 보존. 기능 사용법은 우선 이 문서에 기록했다.
- 승인된 계획의 구현과 수용 검증 완료로 보고한다. 전체 제품 Build and Test 또는 제출 완료로 간주하지 않는다.
