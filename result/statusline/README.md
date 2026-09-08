# Claude 하단 상태줄 — 실행 증거

사용자 승인한 u3-statusline-followup-plan.md에 따라 네 줄 표현과 작업 데이터 연결을 구현했다.

## 확인한 것

- 사용자 작업 skillloop-p0-work의 프로젝트 설정(.claude/settings.local.json)에 제품 Python과 store/usage 절대경로를 고정했다. main 프로젝트에도 해당 프로젝트 데이터 경로를 고정했다. 사용자 전역 Claude 설정은 읽거나 수정하지 않았다.
- Claude와 동일한 Git Bash 명령에 workspace JSON stdin을 주고 프로젝트 밖 cwd에서 실행했다. exit 0, 네 줄, 실제 검증 1회 표시. actual-status.txt 참조.
- 사용자 requirements/Skill store/usage 해시는 연결 전후 동일하다. 설치된 venv와 실적을 초기화하지 않았다.
- 별도 새 합성 프로젝트에서 실제 apply-requirements 설치를 실행해 상태줄 0회→1회 갱신을 확인했다. real-transition.json 참조.
- 데모 수/공개 수/팀 순위를 꾸며 넣지 않았다. 현재 실제 데이터는 DEMO 0, actual 1, 로컬 Skill 2개(관련 1+무관 1)다. 원격 상태 미연결이므로 공개 수 확인 대기와 로컬 모드가 표시된다.

## 사용자 P0 로그 판정

최종 흐름은 실제 설치 실패→정확한 store에서 MATCH→S1 설치/버전/import 검증→C3 counted=True→별도 프로세스 import 성공으로 정상 완료됐다.
중간 별도 match는 원문 오류 문자열을 signature로 전달하고 실제 작업 store를 지정하지 않아 스캔 0건이었다. 해당 NO_MATCH는 의도한 업무 store 검색 증거로 사용하지 않는다.

C9의 중복 분기 안내를 정리했다. 작업 연결 파일이 있는 지원 대상은 apply-requirements가 관찰·검색까지 수행한다. 별도 검색이 필요할 때는 정규화된 applicability 신호와 명시 --store를 사용한다. 기존 C5 알고리즘은 그대로다.

## 제한

실제 Claude 하단 화면은 사용자가 “네, 네 줄이 보입니다”로 확인했다(USER_CONFIRMED). 도구의 stdout/Git Bash 검증과 사용자 화면 확인을 구분한다. 스크린샷은 획득하지 않았다. 설치 성공 장면을 반복하기 위해 작업 패키지를 삭제하지 않는다.

이 변경은 기존 승인 UI의 표현·연결 보완이며 P1/Git 통합이나 전체 제품 완료가 아니다. A cb25a62는 코드 반영 확인 상태, 아직 main 병합/실 Excel 검증을 수행하지 않았다.

## 회귀 결과
UI/조회 관련 30 passed. 기존 P0·PBT를 포함한 전체 86 passed, 0 failed, 0 skipped, pytest exit 0. full-pytest.txt 및 validation.json 참조.
