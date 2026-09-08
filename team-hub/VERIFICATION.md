# Team Hub 검증 기록

2026-09-08 · Windows 11 / Node 22.18.0 / Chromium · 웹 소스는 codex/team-hub 브랜치에 분리.

## 결과

- `npm test`: 11/11 PASS. 작업 분류·취소 제외·완료 집계·본문 파싱·작성 링크·URL 경계·노드 단계 매핑·부분 완료·재개 상태 검증.
- `npm run build`: TypeScript 및 Vite production build PASS.
- `npm audit` (설치 결과): 취약점 0개.
- 실제 Chromium: 25개 행동 검사 PASS. 1440×1100 데스크톱, 390×844 모바일.
- 공개 저장소 조회: 실제 GitHub API snapshot 생성 성공. 등록된 Hub Issue 0개로 확인.
- GitHub Actions build + deploy 성공: [첫 웹 배포](https://github.com/THEGREATCJPark/ddthon/actions/runs/34198635230).
- 배포 URL: [Team Hub](https://thegreatcjpark.github.io/ddthon/), HTTPS HTTP 200 확인.

## 브라우저에서 확인한 동작

1. 미등록 8개 단계는 점등되지 않음.
2. 노드 클릭 → 관련 작업 → 작업 연결 시 해당 단계 자동 선택.
3. 빈 작성 폼의 등록 버튼 비활성화.
4. GitHub 작성 URL에 stable 단계 ID와 한국어 내용 보존.
5. 진행 중·막힘·완료 작업에 연결된 노드만 정확한 상태로 변경.
6. 하위 통합 단계를 자동으로 시작·완료 처리하지 않음.
7. 전체 4 / 진행 1 / 막힘 1 / 완료 1 집계.
8. 일반 Issue, PR, not_planned 취소 작업 제외.
9. 담당자 필터, 단계 필터, 제목·내용 검색.
10. 의견 상세에서 댓글 조회, HTML 입력을 실행하지 않고 텍스트 표시.
11. 목표 작성 링크의 종류와 내용.
12. 기본 Mermaid 4개 렌더링 및 잘못된 문법의 오류 표시·복구·공유 코드 보존.
13. 모바일 대시보드·보드의 페이지 가로 넘침 없음, 메뉴 선택 후 닫힘.
14. GitHub API 403 시 배포 snapshot을 날짜와 함께 표시.

상태가 있는 작업·댓글·API 실패 검사는 브라우저에서만 합성 응답을 주입했습니다. 실제 GitHub에 테스트 Issue나 댓글을 작성하지 않았으며 해당 화면을 제품 실행 증거로 쓰지 않습니다. 실제 공개 API 연결과 빈 상태도 별도로 확인했습니다. GitHub 로그인 이후 Submit 및 댓글 작성은 사용자가 GitHub에서 완료하는 동작이며 이 검증에서 원격 제출하지 않았습니다.

## Archify

[고정 소스](https://github.com/tt-a1i/archify/tree/daced37a66ab21f1f8bb096daedd2c5337204020) · workflow v2 · MIT.

- `deliver`: 9/9 showcase PASS, composition errors 0, warnings 0.
- 정확한 spec / HTML의 SHA-256: [archify-receipt.json](diagrams/archify-receipt.json).
- `visual-check`: 실제 Chrome에서 1440×900, 1600×1000, 1920×1080, 2048×1320의 containment PASS. 양 끝 크기의 light/dark 이미지 생성 완료.
- 이미지 검토: 원본 light 화면 및 웹에서 합성 상태를 적용한 화면을 직접 확인. 노드 글자·관계선·점등·큰 작업 카드 확인. 원본 dark 화면의 이미지 검토는 별도 미수행이며 자동 검증 결과와 구분합니다.
- 원본 Archify HTML은 유지하고, 추출 SVG에 웹의 별도 상태 표시와 노드 상호작용을 적용합니다. 위 Archify receipt는 원본 정적 HTML에 대한 것이며 동기화 기능의 검증은 브라우저 검사에 해당합니다.

## 수정 및 검증 중 발견한 사항

- Archify 노드 제목 폭 진단에 따라 해당 노드의 너비만 조정 후 모든 검사 통과.
- 첫 Mermaid 개요의 작은 글씨는 세로 흐름으로 수정. 후속 사용자 요청에 따라 메인 화면은 Archify 실시간 흐름으로 교체.
- 최초 TypeScript 추론 오류를 명시적인 트랙 문자열 타입으로 수정 후 build 통과.
- 브라우저 검사 스크립트의 Windows 인수 전달, URL 실행 컨텍스트, 전체본문 검색어, 의견 개수에 따른 접근성 이름 조건을 수정. 앱 결함과 테스트 도구 오류를 구분함.
- Git의 줄바꿈 변환으로 spec digest가 달라지는 것을 발견해 해당 생성 계약 파일에 -text 속성을 적용. 원격에 보존되는 실제 바이트로 재확인.

## 운영 범위

main에는 배포 workflow와 웹 링크만 추가했습니다. 제품 구현, 공유 Registry, team-skill-store 또는 AI-DLC 승인 기록은 생성·변경하지 않았습니다. 첫 화면 추천 작업과 P0/P1 목표는 실제 작업 등록·검증과 별개입니다.
