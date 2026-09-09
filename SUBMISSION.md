# 제출 안내 — 노웨어 / Agent SkillLoop

기준: 사용자가 2026-09-09 제공한 제4회 디디톤 제출 가이드와 운영진 대화. 첨부 대화의 일부 운영진 메시지는 본문이 비어 있어 내용 추정에 사용하지 않았다. 공식 사이트에 제출 버튼을 누르거나 manifest를 업로드한 상태는 아니다.

## 저장소에서 읽는 순서

1. [README](README.md): 문제·해결·설치·실행·AI 도구·팀, 실제 P0/P1 화면.
2. [현재 상태](aidlc-docs/aidlc-state.md) → [최신 후속 수정·검증](result/post-closeout-corrections-20260909/README.md) → [Build & Test](aidlc-docs/construction/build-and-test/build-and-test-summary.md) → [MVP 마감 당시 근거](result/development-closeout-20260909/README.md).
3. [요구사항](aidlc-docs/inception/requirements/requirements.md), [스토리](aidlc-docs/inception/user-stories/stories.md), application-design/와 construction/의 설계·계획·테스트 근거.
4. [audit](aidlc-docs/audit.md): 실제 승인·변경·실패·정정 기록. 과거 state는 aidlc-docs/history/에 보존.

| 경로 | 역할 |
|---|---|
| skillloop/ | 실제 Python 제품 소스(src/로 이름 변경하지 않음) |
| tests/, scripts/ | 검증·사내환경 데모 준비 |
| pyproject.toml, requirements-dev.txt | 설치 의존성 선언 |
| team-hub/ | 소개·커뮤니티 웹 소스와 lockfile |
| aidlc-docs/ | AI-DLC 생성 구조 전체 보존 |
| result/ | 실제 화면·영상·공개 로그·검증 영수증 |

예시 폴더명에 맞추려고 audit/state를 루트에 복제하거나 빈 chat-logs 폴더를 만들지 않는다. 원본 비공개 추론·인증정보를 제출용 대화 로그로 추가하지 않는다.

## Git 제출과 필터 한도

공개 저장소 https://github.com/THEGREATCJPark/ddthon 의 **기본 main 브랜치**가 Git 제출 대상이다. MVP 마감 당시 PR #4와 `0a23c49`의 CI/Pages를 확인했고, 이후 승인된 후속 수정은 별도 기록했다. 현재 Python 검증은 `d77177b`의 **228 PASS / 2 SKIP**이며 [후속 검증 근거](result/post-closeout-corrections-20260909/README.md)를 따른다. 그 뒤 소개 영상 등 웹 변경은 해당 커밋의 웹 CI로 구분한다. 사이트 최종 제출 버튼은 사용자가 수행한다. 특정 SHA 고정 제출은 그 SHA의 source ZIP을 사용한다.

사용자 제공 한도: source ZIP 200MB, 압축 해제 1GB/10,000개; 평가 필터는 개별 10MB/전체 100MB/1,000개. [inventory](result/development-closeout-20260909/submission-inventory.json)는 MVP 마감 당시의 파일 수·크기이며 이후 추가 파일을 포함한 현재값은 아니다.

원본 `result/p1-web-delivery-20260909/Agent-SkillLoop-P1-Video.zip`은 10MB를 넘어 평가에서 제외될 수 있다. 원본·해시를 보존하면서, 10MB 이하의 추출 MP4·PNG·SRT·텍스트에 README가 직접 연결된다. 웹의 선택적 원본 ZIP 다운로드는 해당 파일을 보존한 GitHub 커밋의 URL을 사용하며 ZIP을 빌드 입력으로 import하지 않는다. 원본 다운로드에는 인터넷 연결이 필요하며, 영상·자막·로그 표시는 개별 파일을 사용한다. 평가기가 ZIP 내부를 읽을 것이라고 기대하지 않는다. `.venv`, `node_modules`, `.git`, 개인 인증 설정은 추적 소스에 포함하지 않는다.

30초 소개 영상 `result/agent-skillloop-intro-20260909/Agent_SkillLoop_Animated_30s.mp4`도 16,255,648바이트로 개별 필터 대상이다. 원본은 보존하고 웹에서는 커밋 고정 GitHub URL로 재생하여 빌드 의존성을 없앴다. 소개 영상 재생에는 인터넷 연결이 필요하다. 이 애니메이션은 실제 P0/P1 실행 증거와 구분하며, 10MB 이하의 실제 시연 영상·이미지·로그는 개별 파일로 계속 제공한다.

## 갤러리에 직접 입력할 내용

제목: Agent SkillLoop — 한 Agent의 해결 경험을 다음 Agent의 Skill로

설명(일반 텍스트): 사내 환경 제약으로 막힌 코딩 Agent가 팀의 검증된 해결 경험을 재사용합니다. 기존 해결법이 있으면 같은 작업 환경에 적용하고 실제 성공을 기록하며, 처음 찾은 방법은 사람 승인과 독립 재검증을 거쳐 공유합니다. 해커톤에서는 Python 패키지 설치와 Excel 문서 접근 사례를 시연하고, 조직 공유 저장소는 GitHub로 구현했습니다. S3 등 사내 저장소 연결은 향후 확장 방향입니다.

화면 이미지 후보(각 10MB 이하):
- [P0 Claude 실제 화면](result/p0-demo-20260909/p0-claude-code.png)
- [P1 실제 게시 전후](result/p1-web-delivery-20260909/video/Agent_SkillLoop_P1_게시전후.png)

갤러리 미디어 형식은 PNG/JPG/JPEG/WebP이며 영상은 README/웹 링크로 제공한다. 운영진 채팅에 따르면 갤러리 설명은 HTML/Markdown을 지원하지 않는다. 갤러리에 코드·README가 그대로 보인다고 가정하지 않는다. 재제출은 새 버전이며 최신 제출만 갤러리에 표시된다. 업로드/최종 제출은 사용자가 수행한다.

## 평가 대응과 정직한 범위

AI 심사 25/20/15/15/15/10, 최종 AI 40% + 참가자 투표 60%라는 사용자 제공 기준을 사용한다. 자체 QA 점수는 공식 예측이 아니다. 요구→계획→코드→검증 연결, 실제 화면, 실행 가능성에 집중한다. 역사적 C9/match 계획 누락·timestamp 오류·웹 사전 근거 미확인은 보존하고 현재 보완/수용과 구별한다.
