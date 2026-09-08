# 디디톤 Team Hub

팀 대시보드: https://THEGREATCJPark.github.io/ddthon/

팀의 목표, 개발 작업, 논의와 Mermaid 설명을 함께 보는 독립적인 협업 웹입니다. 제품 구현 및 AI-DLC 승인 상태를 대신하지 않습니다. P0/P1 설명은 지정된 전략 대화에서 정리한 목표이며 검증 성공으로 집계하지 않습니다.

## 팀원 사용법

상단 배너는 사용자가 제공한 제4회 디디톤 원본 이미지입니다. UI 키컬러는 네이비·블루·골드이며 흰색과 회색 계열은 바탕과 텍스트에 사용합니다.

### 순서도에서 바로 상태 표시

1. 대시보드 또는 순서도에서 **직접 표시**를 선택합니다.
2. 노드를 눌러 **할 일 / 진행 중 / 도움 필요 / 완료**를 선택합니다. 여러 단계를 동시에 진행 중으로 표시할 수 있습니다.
3. 표시와 모드는 이 브라우저에 저장됩니다. **상태 링크 복사**로 팀원에게 현재 상태를 전달합니다. 링크는 복사 시점의 상태이며 이후 변경은 새 링크로 공유합니다. 링크를 여는 브라우저에서는 전달받은 상태로 수동 표시가 바뀝니다.
4. **GitHub 연동**으로 전환하면 실제 연결된 작업 상태가 다시 표시됩니다. 수동 표시는 GitHub 작업·대시보드 작업 수·목표 진행률을 변경하지 않습니다. 노드에서 **연결된 작업**으로 이동할 수 있습니다.

브라우저 저장이 차단된 경우 화면에 표시하며 현재 탭에서만 유지됩니다. 클립보드 복사가 막혀도 공유 창의 링크를 직접 복사할 수 있습니다. 수동 상태의 실시간 공동 편집은 제공하지 않습니다.

### GitHub 작업 공유

1. **작업 추가**에서 제목, 트랙, 내용, 완료 기준을 적고 **GitHub에서 등록 완료**를 누릅니다. 새 창에서 로그인하고 Submit new issue를 눌러야 공유됩니다.
2. GitHub Assignees에서 담당자를 지정합니다. 진행 중에는 `status:doing`, 도움 필요에는 `status:blocked` 라벨을 사용합니다. 막힘 해소 후 해당 라벨을 제거합니다.
3. 결과·증거 링크를 남긴 뒤 Close as completed로 닫으면 완료에 집계됩니다. 취소할 때는 Close as not planned를 사용하며 집계에서 제외됩니다.
4. 목표, 의견과 다이어그램도 같은 방식으로 등록합니다. 댓글은 상세 창에서 읽고 GitHub에서 작성합니다.
5. 웹으로 돌아와 새로고침합니다. 열린 탭은 5분마다 갱신합니다.

첫 화면의 추천 작업은 **미배정 계획 초안**입니다. GitHub에 등록하기 전에는 진행률에 포함되지 않습니다. 이 사이트는 공개 공간이므로 회사 데이터나 인증정보를 작성하지 마세요.

### 공유 데이터 규칙

| 종류 | 제목 접두사 또는 라벨 |
|---|---|
| 작업 | `[TASK]` 또는 `hub:task` |
| 목표 | `[GOAL]` 또는 `hub:goal` |
| 의견 | `[DISCUSSION]` 또는 `hub:discussion` |
| 순서도 | `[DIAGRAM]` 또는 `hub:diagram` |

일반 Issues 및 PR은 허브 집계에 포함하지 않습니다. 라벨을 지정할 권한이 없어도 접두사로 분류됩니다. Markdown의 `### 트랙` 다음 줄에 `P0`, `P1`, `공통`, `공유`, `QA` 중 하나를 작성하면 트랙별로 볼 수 있습니다. 체크리스트는 Markdown `- [ ]` / `- [x]`를 사용합니다.

Mermaid는 아이템 설명에서 코드 편집·복사·다운로드를 지원합니다. 편집 중인 내용은 공유되거나 영구 저장되지 않습니다. 공유할 때 GitHub 등록을 완료하세요. 기존 다이어그램 변경은 해당 Issue 본문의 mermaid 코드 블록을 편집합니다. 너무 긴 코드는 GitHub에서 직접 작성할 수 있습니다.

## 브랜치와 배포

- `main`: 제품 저장소. `.github/workflows/team-hub.yml`로 웹 배포만 연결합니다.
- `codex/team-hub`: 웹 소스와 테스트. `team-hub/` 폴더에서 개발합니다.
- `team-skill-store`: 제품 공유 전송의 **설계 후보**이며 이 작업에서 만들거나 구현하지 않았습니다.

GitHub Pages의 Build and deployment는 **GitHub Actions**를 사용합니다. `codex/team-hub`의 소스 변경, Issue/댓글 변경, 수동 workflow_dispatch 때 최신 웹 브랜치를 빌드합니다. Issue 이벤트는 기본 브랜치의 workflow가 처리하므로 양쪽 브랜치의 workflow 파일을 동일하게 유지하세요.

Workflow는 의존성 설치 → 데이터 집계 테스트 → 공개 Issues/댓글 snapshot → 타입 검사 및 Vite build → Pages 배포 순서입니다. `GITHUB_TOKEN`은 Actions의 데이터 읽기에만 전달되며 브라우저 번들에는 들어가지 않습니다. Pages는 별도 서버·DB·유료 서비스 없이 동작합니다.

## 로컬 실행

Node 22.18 이상, npm 10 이상.

```sh
git clone --branch codex/team-hub https://github.com/THEGREATCJPark/ddthon.git
cd ddthon/team-hub
npm ci
npm run dev
```

http://127.0.0.1:5173/ddthon/ 에서 열립니다.

```sh
npm test
npm run snapshot
npm run build
npm run preview
```

## 동기화와 한계

- GitHub가 공용 데이터의 원본입니다. 읽기는 공개 API, 쓰기는 GitHub의 로그인된 UI를 이용합니다. 웹 내에서 직접 상태를 드래그하거나 글을 저장하지는 않습니다.
- 공개 API의 비인증 요청 한도·네트워크 실패 시 배포 때 저장한 snapshot으로 대체하고 날짜를 표시합니다. 마지막 실시간 조회가 있으면 해당 결과를 유지합니다. 실패를 빈 데이터나 최신 데이터로 표시하지 않습니다.
- GitHub 작성 창을 열었다는 것만으로 등록 성공을 표시하지 않습니다. 돌아와 새로고침하여 확인해야 합니다.
- Issue 본문과 댓글은 안전한 텍스트로 표시합니다. 원본 Markdown 렌더링·링크는 GitHub에서 확인합니다. Mermaid는 strict 보안 모드, 길이·간선 제한, 설정 지시문 차단을 적용합니다.
- 프로젝트 일정·인원·승인·실행 결과는 확인되지 않은 값으로 채우지 않습니다. P0/P1 기본 목표는 검증 대기로 유지하며 실제 결과는 공유 작업에 기록합니다.
- Google Fonts 연결이 없으면 시스템 글꼴을 사용합니다.

개발·검증 기록은 [VERIFICATION.md](VERIFICATION.md)에 정리합니다.

## Archify 순서도와 실제 작업 연결

`tt-a1i/archify`의 실제 workflow v2 렌더러를 사용했습니다. 버전은 commit `daced37a66ab21f1f8bb096daedd2c5337204020`에 고정했고 MIT 라이선스와 고지를 포함합니다. 단순히 Archify 스타일을 흉내 낸 것이 아닙니다.

- 대시보드와 순서도 탭에서 같은 작업 원본으로 노드를 갱신합니다.
- 새 작업의 **순서도 단계**에서 위치를 선택합니다. 노드 클릭 → 작업 연결은 해당 단계를 자동 선택합니다.
- `### 단계`의 stable ID: `requirements`, `design`, `p0`, `p1`, `sharing`, `integration`, `qa`, `submission`.
- 명시적인 단계가 없을 때 P0/P1/공유/QA 트랙은 대응 노드에 연결됩니다. 공통 트랙의 위치를 추측하지 않습니다.
- GitHub 연동 모드에서 미등록은 꺼짐, 할 일은 대기, 진행 중은 블루 점등, 도움 필요는 골드, 모든 연결 작업 완료 시 네이비 채움입니다. 일부 완료만으로 노드 전체를 완료 처리하지 않습니다.
- 우선순위는 막힘 → 전체 완료 → 진행 중 → 할 일입니다. 취소 작업은 제외합니다.
- 노드와 연결선의 색은 **개발 작업 상태**입니다. 제품 runtime trace, AI-DLC 사람 승인, 시연 성공을 뜻하지 않습니다. 흐름 자체는 팀 운영을 위한 계획입니다.
- Archify 원본 HTML은 보존합니다. 웹은 추출한 SVG에 별도의 작업 상태·키보드 클릭 계층을 적용합니다. 정적 원본의 검증과 웹의 실제 동기화 테스트는 따로 수행합니다.
- Archify 원본 뷰어의 고정 UI는 한국어를 지원하지 않아 영어입니다. 협업 웹의 UI·노드·상태는 한국어입니다.

### 순서도 다시 생성하기

빌드 시 이미 생성된 SVG를 사용하므로 일반 팀원은 Archify를 설치할 필요가 없습니다. 순서도 구조를 바꿀 때만:

```sh
git clone https://github.com/tt-a1i/archify.git .archify
git -C .archify checkout daced37a66ab21f1f8bb096daedd2c5337204020
# diagrams/development.workflow.json을 수정한 후
npm run diagrams -- .archify/archify
npm run build
```

`deliver`가 모든 9개 검사를 통과해야 HTML·SVG가 갱신됩니다. `diagrams/archify-receipt.json`에 원본과 결과 SHA-256을 남깁니다. 직접 HTML을 편집하지 마세요. 생성 후 Archify `visual-check`와 실제 웹에서 노드 클릭·상태 동기화를 각각 확인하세요.
