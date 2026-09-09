# 소개 영상·현재 검증 안내 보완

기록: 2026-09-09T07:41:29.000824+00:00. [승인 계획](../../aidlc-docs/construction/plans/intro-filter-docs-plan.md). 기준 main0c802c2의 필터 적용 빌드 실패를 먼저 재현했다.

- 16.26MB 원본 소개 영상은 바이트 그대로 보존하고, ProductIntro의 정적 import만 커밋 고정 raw GitHub URL로 교체했다. 재생에는 인터넷이 필요하다. 기존 UI/문구/원본 미디어는 바꾸지 않았다.
- SUBMISSION/Build & Test에서 현재 228 PASS/2 SKIP과 최초 MVP 마감 당시 200 PASS/2 SKIP을 구분했다. 과거 실측값은 삭제하지 않았다.
- 일반 사본과 10MB 초과 MP4·ZIP 제외 사본 각각 웹 **10 tests PASS / build PASS**, dist 전체 hash 동일. 의존성/lockfile은 무변경이며 검증된 설치를 사본의 junction으로 재사용했다.
- 필터 사본 브라우저에서 소개 영상 재생 버튼을 누르고 실제 영상 프레임 렌더를 확인했다. URL HEAD200, 원본 SHA256 불변. 전체 재생 시간/성능 재측정은 하지 않았다.
- Python/테스트/공식 규칙 무변경. 기존 d77177b의 로컬 cp949·UTF8 각228/2 및 Python CI 결과를 유지하며 재실행하지 않았다.
- 사전 계획·승인 커밋 a24081d → 단계2 수정 및 즉시 체크/audit → 단계3 실제 검증 순서로 진행했다. 새 기능/Units 재분석이나 기존 완료 취소는 없다.

main `fcc1e50` 반영 및 웹 CI34325148671의 테스트·권한 규칙·빌드·Pages 배포 SUCCESS를 2026-09-09T07:42:59.407096+00:00에 확인했다. [CI 영수증](ci.json). 이번 보완은 완료이며 기존 MVP 수용 상태를 유지한다.
