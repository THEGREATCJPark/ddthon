# U3 하단 상태줄 보완 — 최소 Code Plan

상태: 사용자 승인 후 구현·검증 완료 / 코드 결과 REVIEW REQUIRED. 사용자 요청한 기존 FR-UI-1/3·FR-ORG-2의 표현·연결 보완.
기존 P0 구현·수용 PASS와 결과 검토 게이트는 유지한다. 새 제품 범위/Unit/게시 의미를 추가하지 않는다.

## 확인한 누락

- statusline.py는 한 줄 요약만 구현됐다. 사용자가 제시한 네 줄 표현은 미구현.
- 새 Desktop/skillloop-p0-work에는 C9 Skill만 있고 statusLine 설정이 없다.
- 기존 명령은 cwd/.skillloop_demo를 읽으므로 새 작업의 .skillloop/store·usage와 연결되지 않는다.
- Claude Code 공식 문서는 여러 줄 stdout을 지원한다고 명시한다. 외부 사전 구현은 접근하지 않았다.
  https://code.claude.com/docs/en/statusline

## 표현·데이터 계약 보완

1. C11 기본 표현을 네 줄로 구성: 팀/연결·공개 Skill·사용자 → 내 기여/안내 → 기여 1위·인기 Skill → 데모 기준/실제 검증·데이터 범위.
2. 팀 표시명은 사용자가 지정한 “디디톤 기술혁신팀”, viewer는 명시 alias 또는 OS 사용자명을 사용한다. 사람/Skill 표시명은 식별자를 바꾸지 않는 명시적 표시 설정이며 실제 작성자/선택 Skill과 연결한다.
3. C10의 동일 집계 스냅샷을 사용한다. 게시·팀 연결은 S3/C4 근거가 있어야 한다. 미연결은 로컬 모드/공개 확인 대기로 표시한다. 로컬 기여를 팀 전체 순위라고 표시하지 않는다.
4. “20회”, “공개 1개”, “박찬준 1위”는 고정값으로 넣지 않는다. 실제로 존재하는 DEMO_SEED/actual·게시·작성자 근거를 표시하고 없는 값은 없음/미연결로 구분한다. 현재 예시와 같은 DEMO 20을 새로 적재하는 작업은 이번 UI 변경에 포함하지 않는다.
5. status는 명시 --store/--usage를 받을 수 있게 하고, 작업 프로젝트의 skillloop-work.json 연결 경로를 사용한다. 다른 작업 폴더로 이동해도 해당 프로젝트 데이터를 읽도록 상태줄 명령에 경로를 고정한다.
6. 프로젝트 statusLine만 연결한다. 사용자 전역 설정·Bedrock 토큰은 수정하지 않는다. 상태줄은 읽기전용이며 실행·검증·카운트·게시를 발생시키지 않는다.

## 파일·실행 순서 — CJ

- [x] S1. 승인 후 u3-minimal-design.md §2.2/§4와 현재 단계 기록에 이 보완을 연결.
- [x] S2. skillloop/statusline.py의 네 줄 표현 및 필요시 org_aggregator.py의 기존 데이터 표시 필드 연결. 새 저장 schema·게시 상태 추정 없음.
- [x] S3. skillloop/cli.py status 경로/표시 인자 연결. tests/prepare_p0_work.py가 새 작업에도 프로젝트 statusLine 설정을 생성하도록 보완. 저장소 .claude/settings.json과 이미 준비된 사용자 작업 폴더의 프로젝트 설정을 보존 병합.
- [x] S4. tests/test_statusline.py·test_org_aggregator.py 및 필요한 CLI/준비 도구 테스트: 실제/DEMO 분리, 네 줄, 미연결 표기, 순위 근거, 작업 경로·한국어·읽기전용. 기존 P0 회귀.
- [x] S5. Claude 입력 JSON과 다른 cwd에서 실제 statusLine 명령 실행, 작업 전후 실제 실적 변화 표시 확인. 실제 하단 렌더링은 확인 가능한 도구/사용자 화면으로 별도 판정하며 stdout만으로 UI 육안 PASS를 주장하지 않는다.
- [x] S6. 코드 결과 및 실제 출력 증거 기록 후 REVIEW REQUIRED.

기존 승인된 U3 구현 계획은 한 줄 출력 기준이었다. 이번 문서는 후속 수정의 사전 계획이며 이전 승인을 소급 확대하지 않는다. 승인 후 구현한다.

## A PR 수신 기록

origin/review-pr-1 = cb25a62. 코드 diff에서 실제 B 모듈 경로, AccessResult 속성 접근, original_unchanged/completed_month_rows/save_called 판정, 미지원 action 거절 반영 확인.
A 보고 74 passed는 A 브랜치 결과다. CJ main 병합·실 Excel PASS는 아직 아니다.
A의 수정 범위는 인계 가능한 상태로 판단하며 추가 장문 문답 없이 CJ가 통합 검증을 맡는다. 통합 후 미연결 전제 테스트와 실제 B 반환형 연결도 확인한다.

## 사용자 라이브 로그에 따른 기존 계약 정합화
C9의 work context 분기와 일반 검색 설명 중복을 제거해 apply-requirements 경로에서 불필요한 별도 match를 호출하지 않도록 한다. 기존 cmd_match(store_path) 계약에 --store CLI 인자를 연결하고, context 경로를 정확히 사용한다. A의 검색 알고리즘은 변경하지 않는다. 추가 파일: .claude/skills/skillloop/SKILL.md, tests/test_cli_match.py.

## 완료 증거
result/statusline/: 관련 30 passed, 전체 86 passed/0 skipped, 실제 작업 데이터 1회 표시·별도 실제 설치 0→1 갱신. 사용자가 네 줄 실제 하단 표시를 확인했다. 글로벌 설정과 사용자 설치·실적 데이터 보존. 새 C9 지침으로 fresh Agent 실행을 추가 수행한 것은 아니며, 잘못된 중복 match 유도 안내를 정정했다.
