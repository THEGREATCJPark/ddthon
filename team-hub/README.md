# 노웨어 · Agent Skillloop

[웹 열기](https://thegreatcjpark.github.io/ddthon/) · 제4회 디디톤

데스크톱에서 진행 순서도를 보고, 댓글과 답글로 이야기하는 작은 팀 공간입니다.

## 네 가지 탭

- **진행 순서도**: AI-DLC의 INCEPTION에서 아이템의 문제·사용자·성공 기준을 정하고, CONSTRUCTION에서 U1 Python 설치·U2 Excel 분석·U3 협업 Web을 병렬 진행합니다. 구현과 분리된 팀원 한 명이 평가를 맡은 뒤 통합 시연으로 연결합니다. 각 박스를 눌러 대기·진행 중·막힘·완료를 직접 선택합니다.
- **팀 의견**: 이름과 내용만 입력합니다. 댓글 아래에 한 단계 답글을 남길 수 있습니다. 방문자도 열람할 수 있는 공개 공간이며 인증된 팀원 전용 게시판은 아닙니다.
- **딴지 걸기**: 다른 팀도 로그인 화면 없이 익명으로 의견을 남깁니다. 이름을 받지 않고 공개 문서에 사용자 ID를 넣지 않습니다. 예시 한 개는 **샘플**로 표시하며 실제 의견 수에서 제외합니다.
- **시연**: P0의 Python 설치 실패→기존 Skill 재사용은 6단계, P1의 합성 보호 Excel 분석 실패→새 Skill 게시·재사용은 8단계로 넘겨 봅니다. 단계 목록을 직접 선택하거나 이전·다음·초기화 버튼을 사용합니다.

시연 탭은 제품 흐름을 설명하는 브라우저 메모리 기반 시뮬레이션입니다. 표시되는 승인, Replay, 게시, 기여 및 재사용 수치는 실제 실행 증거가 아니며 Firebase나 GitHub에 저장하지 않습니다. P1은 실제 사내 보호체계를 재현하거나 우회하지 않고 **사내 보호문서와 유사한 합성 제약 환경**만 사용합니다.

작업 등록, 대시보드, 칸반 보드, 목표 관리, GitHub Issues 동기화, Mermaid 편집기는 제거했습니다. GitHub는 소스와 Pages 배포에만 사용합니다. 순서도는 실제 Archify workflow 렌더러로 생성합니다.

## 저장과 공유

댓글과 답글은 **Firebase Firestore에 실제 저장**하고 다른 브라우저에 실시간 전달합니다. Firebase 익명 인증은 백그라운드에서 처리하며 별도의 가입/로그인 화면은 없습니다. 작성자만 자신의 글을 삭제할 수 있습니다. 답글이 있는 원문이 삭제되면 답글을 유지하고 원문 자리에 안내를 표시합니다.

진행 순서도의 수동 상태는 **각 브라우저에 저장**합니다. **상태 링크 공유**는 복사 시점의 모든 노드 상태를 전달하며 이후 변경은 새 링크로 공유합니다. 실시간 공동 상태 편집이 아닙니다. 이전 구조의 상태를 현재 AI-DLC 6단계(v3)로 추측해서 옮기지 않습니다.

- 댓글: 1~~1,000자, 이름: 1~~20자. 최근 댓글·답글 200개 조회.
- 서버 규칙: 보드·본문·이름·타임스탬프 검증, 답글의 보드와 부모 확인, 계정별 3초 등록 간격, 타인의 수정/삭제 및 작성자 식별 문서 조회 차단.
- 익명은 방문자 화면에서의 익명입니다. 서비스 운영자는 Firebase 관리 권한으로 작성자 인증 UID를 확인할 수 있습니다. 공개 글은 누구나 볼 수 있습니다.
- 원격 등록이 확인되어야 공유 완료를 표시합니다. 연결 실패 시 입력은 남아 있으며 다시 시도할 수 있습니다.

## 개발·배포

웹 소스: `codex/team-hub` 브랜치의 `team-hub/`. `main`에는 Pages workflow와 링크만 연결합니다.

```sh
npm ci
npm run dev
npm test
npm run build
```

로컬 주소는 `http://127.0.0.1:5173/ddthon/`입니다. 사용자가 제공한 행사 배너는 원본 바이트 그대로 `public/images/ddthon-banner.png`에 보존합니다. UI는 네이비·블루·골드를 사용합니다.

Firebase 프로젝트는 이 웹 전용 `nowhere-skillloop-ddthon`이며 Firestore 위치는 `asia-northeast3`입니다. 사용자의 다른 Firebase 프로젝트를 변경하지 않았습니다. 웹 SDK 설정은 공개 식별자이며 접근 통제는 `firestore.rules`가 담당합니다. 서비스 계정/관리자 토큰은 브라우저에 넣지 않습니다.

Firebase 규칙·인덱스를 변경한 경우 프로젝트 관리자 인증으로 별도 배포합니다:

```sh
npx firebase-tools@15.29.0 deploy --project nowhere-skillloop-ddthon --only firestore,auth
```

웹 push 시 GitHub Actions가 단위 테스트, Java 21 기반 Firestore 에뮬레이터 규칙 테스트, 빌드 후 GitHub Pages를 배포합니다. Issue/댓글 이벤트와 데이터 스냅샷 단계는 없습니다. 규칙 검증은 `demo-nowhere` 에뮬레이터에만 수행하며 실제 저장소에 쓰지 않습니다.

```sh
# Java 21 이상
npx firebase-tools@15.29.0 emulators:exec --only firestore --project demo-nowhere "npm run test:rules"
```

## Archify

MIT · [tt-a1i/archify](https://github.com/tt-a1i/archify) commit `daced37a66ab21f1f8bb096daedd2c5337204020` 고정. `diagrams/development.workflow.json`에서 생성하고 원본 HTML/SVG와 라이선스를 보존합니다. 웹의 클릭/점등/색상/글자 확대 계층은 생성물과 분리합니다.

```sh
git clone https://github.com/tt-a1i/archify.git .archify
git -C .archify checkout daced37a66ab21f1f8bb096daedd2c5337204020
npm run diagrams -- .archify/archify
```

노드와 간선 이름은 해당 작업 자체로 의미가 명확하므로 중복 간선 설명을 생략했습니다. 원본 뷰어의 고정 UI는 영어이며 웹의 진행 화면은 한국어입니다. 생성물 검증 정보는 `diagrams/archify-receipt.json`, 실제 웹과 저장 동작 검증은 [VERIFICATION.md](VERIFICATION.md)를 확인하세요.
