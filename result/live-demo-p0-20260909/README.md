# P0 LIVE DEMO RUN #1 — NOT_RUN

**실제 Claude Code interactive UI 시연은 실행하지 못했다.** 화면 캡처·대화·성공 증거가 없다. 기존 headless 로그나 웹 화면을 대신 사용하지 않았다.

- 제품 source SHA: `fff0ffac97fd52bd36995265c9ed14b12e2961c0`.
- 새 isolated workspace: `C:\Users\cik61\Desktop\skillloop-live-p0-20260909`.
- 예정 질문: `이 프로젝트 requirements.txt의 패키지를 설치해줘.` — **아직 입력되지 않음**.
- 초기/확인 시 usage: 0/0. 패키지는 미설치 상태 그대로, Candidate delta0. 설치·version/import 검증은 미실행이다.
- 기존 승인 로컬 Skill, work venv, 연결 파일과 네 줄 statusLine 설정은 기존 준비 도구로 만들었다. 사용자 설정·토큰은 읽거나 수정하지 않았다.
- Claude Code를 지정 workspace/session으로 실제 실행했다. OS 프로세스에서 powershell29504 및 Claude 실행을 확인했다. 그러나 `@oai/sky`의 실제 list_windows/list_apps 결과에서 해당 터미널이 제어 대상으로 제공되지 않았다. GUI 도구 런타임 자체는 동작하므로 '모든 Computer Use가 없다'고 표현하지 않는다.
- 반환받지 못한 window handle을 만들어 주입하거나 다른 입력/캡처 우회 도구를 사용하지 않았다. 자연어 요청·권한 응답·시연 입력은 보내지 않았다.
- `verification.json`은 이 미실행 상태와 준비 점검만 기록한다. `visible-transcript.md`에도 대화 미취득임을 기록했다. 01/02/03/00 PNG 파일은 생성하지 않았다.

## 사용자 직접 실행 4단계

1. 열린 Claude Code 창에서 작업 경로가 `C:\Users\cik61\Desktop\skillloop-live-p0-20260909`인지 확인한다. 창을 찾지 못하면 이 폴더에서 Claude Code를 연다. 아직 설치 요청은 수행하지 않았다.
2. 하단 SkillLoop 상태줄의 실제 검증0을 확인하고, `이 프로젝트 requirements.txt의 패키지를 설치해줘.`만 한 번 입력한다. 질문/상태줄 화면을 캡처한다.
3. 동일 세션의 실제 설치 실패와 팀 Skill 검색 장면을 캡처한다. 도구 권한이 필요하면 해당 업무 범위만 확인한다. 오류가 나도 새 성공 세션으로 교체하지 않는다.
4. 같은 세션의 설치·version/import 성공 답변과 실제 검증1 상태줄을 캡처한다. 결과와 캡처를 전달하면 실행 로그·실제 usage를 확인해 판정한다. 그 전까지 이 기록은 NOT_RUN이다.

`run-context.json`의 session_id는 준비한 세션 식별자이며, 실행 성공이나 화면 관찰 근거가 아니다. 웹 실제 실행 카드는 이번에 만들지 않았다.
