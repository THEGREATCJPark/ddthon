# 소개 영상 필터 호환성·최신 검증 안내 보완

상태: COMPLETE / 승인된 두 항목 구현·검증·main/CI 완료. 기록 2026-09-09T07:39:09.889871+00:00. 기준 main `0c802c21bf5f876051dfc724dcc5d8fdd867e3e1`.

기존 MVP 완료 및 Units/계약은 유지한다. 기존 제출 ZIP 보완 계획의 웹 전달 호환성과 Build & Test 현재 결과 안내만 연장한다. 이전 검토에서 16,255,648바이트 소개 MP4가 평가의 10MB 파일 필터에서 제외될 때 ProductIntro의 정적 import 때문에 빌드 실패를 재현했다. 이전 P1 ZIP 보완은 정상이다.

사용자 승인 원문: “어 그것만 반영해봐 ai-dlc 위배된다면 하지말고”. 직전 제안의 두 항목만 승인한 것으로 기록한다. 새 기능·시연·Python 로직·비교 수치·원본 미디어 변경은 하지 않는다.

## 최소 Code Plan

- [x] 1. 최신 main과 실패 근거를 확인하고 최소 계획/승인을 구현 전에 기록한다. 기존 공식 규칙과 extension 설정 유지. Python/PBT 로직 변경이 없어 재실행은 N/A이며 기존 228/2 및 CI 근거를 참조한다.
- [x] 2. `team-hub/src/ProductIntro.tsx`의 원본 MP4 import를 아래 커밋 고정 URL 상수로 교체한다. `SUBMISSION.md`에 현재 검증 연결·이전 마감 기준·소개 영상 필터/인터넷 의존을 표시하고, `aidlc-docs/construction/build-and-test/build-and-test-summary.md` 맨 앞에서 현재 228/2 근거와 기존 MVP 마감 기록을 구분한다. 원본 영상·해시·설명/UI 배치는 유지한다. 단계 완료 즉시 체크 및 audit 갱신 후 검증한다.
- [x] 3. 일반 및 10MB 초과 원본 ZIP/MP4가 모두 빠진 사본에서 기존 웹 테스트·빌드, dist 동일성, 영상 URL·브라우저 재생 가능 여부, 문서 링크·원본 hash를 검증한다. 영향 없는 Python/실 Excel 시나리오는 반복하지 않는다. 실패 시 고친 뒤 관련 검증만 반복한다.
- [x] 4. 실제 결과를 기록하고 main 반영·웹 CI 확인 후 완료로 기록한다. 동시 다른 세션 변경은 보존한다. 과거 절차 이탈/승인 기록을 소급 변경하지 않는다.

원본 URL: https://raw.githubusercontent.com/THEGREATCJPark/ddthon/2e034256e1529bec30687a110c9cdea50b357171/result/agent-skillloop-intro-20260909/Agent_SkillLoop_Animated_30s.mp4

원본 SHA256: `110bce964ae6ce075b836b82456bc401f4fc140317cfc1be47cf1e3841804b89`. 원본 유지; 평가기가 10MB 초과 영상을 직접 읽거나 오프라인 재생할 수 있다는 보장은 하지 않는다. 실제 P0/P1 실행 증거의 작은 개별 파일은 계속 제공한다.

읽기 전용 검토에서 확보한 실패 로그: 운영자 `final-intake-review-073646/filtered-build.txt` (main0c802c2, exit1). 결과 폴더에 원본 복사해 연결한다.


완료 2026-09-09T07:42:59.407096+00:00: [결과·CI](../../../result/intro-filter-correction-20260909/README.md). 사전 계획/승인 a24081d → 수정 fcc1e50 → 웹 CI SUCCESS. 원본 영상/Python/규칙 무변경.
