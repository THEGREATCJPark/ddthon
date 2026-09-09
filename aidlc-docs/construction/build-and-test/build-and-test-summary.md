# Build & Test — 사용자 수용 및 main 전달 완료

## 현재 검증 기준 — 승인된 후속 수정 포함

Python은 `d77177b` 기준 **228 PASS / 2 SKIP**(로컬 cp949·UTF8 각각 및 GitHub CI), 웹은 10 PASS·일반/대용량 ZIP 제외 빌드 PASS다. [후속 수정 결과·CI](../../../result/post-closeout-corrections-20260909/README.md)를 현재 근거로 사용한다. 이후 소개 영상 필터 호환성 보완은 [승인 계획](../plans/intro-filter-docs-plan.md)에 따라 별도 검증·main 반영·웹 CI까지 완료했다. [소개 영상 보완 결과](../../../result/intro-filter-correction-20260909/README.md). Python 소스는 변경하지 않았다.

## MVP 최초 마감 당시 기록

**아래 200 PASS 및 “이후 Python 동일” 문구는 최초 마감 시점에 한정한다.** 후속 수정 이후의 현재 코드·테스트 개수로 읽지 않는다. 이전 실행·사용자 수용 근거는 보존한다.

최종 전달 보완: 다른 세션의 설명 웹 변경 `2f19f3c`를 보존·통합했다. 동일 소스의 웹 CI34318992726(테스트·규칙·빌드·Pages) SUCCESS, Python은 `0a23c49`와 동일하다. `result/development-closeout-20260909/final-web-followup-ci.json`에 확인 근거를 추가했다. 이후 기록 커밋은 이 소스와 동일하다.

**해커톤 MVP 범위의 Build & Test 완료, 최종 사용자 수용 완료.**

- Python 테스트 대상 코드: `6197a975b020768cc29bcd92dd27553406da268e`. 이후 Python 제품/테스트 동일. 웹은 원격 `3b2c19d`와 승인된 입력 PBT 보완을 포함해 재검증했다.
- 새 환경 설치·pip check·CLI 진입 PASS. **Python200 PASS/2 SKIP**, Hypothesis seed20260908, 319.60초.
- SKIP: 실제 Excel opt-in 1건, 통합된 B 모듈의 미연결 대역 시나리오 N/A 1건.
- 웹 의존성 설치, **10 tests PASS**, build PASS. 변경되지 않은 Firestore rules는 기존 GitHub CI34315865105의 emulator PASS 및 운영 API 조회 exact hash 일치 근거를 유지한다. main 병합 SHA `0a23c49748107279139d240275b1e0cadf9db9ce`의 웹 테스트·emulator·빌드·Pages 배포를 실제 SUCCESS로 확인했다.
- P0 WITH_SKILL3/3, P1 추가 Cold4/4 업무·차트 PASS. 수동 P1 승인/Replay/Git 게시도 별도 실제 증거로 완료. 이전 ‘사용자 게시 대기’는 해당 과거 시점의 기록이다.
- Git 수신/Warm/usage 왕복은 독립 workspace의 실제 원격 검증. 다른 물리 PC의 전체 제품 실행을 독립 확인했다고 주장하지 않는다.
- 공개 영상 P0/P1 HTTP200. 편집 영상과 자동 측정 세션은 별개다.

## 현재 검토 상태

1. 신규 웹 예시 입력 PBT — 승인 후 구현·검증 완료. 해당 blocking finding 해소.
2. 신규 웹 쓰기 — 사전 근거 미확인 보존, 사용자의 현재 기능 수용 기록 완료. 소급 승인 아님.
3. README 최신 상태·제출 구조 연결 완료. 최종 사용자 결과 수용, main 전달 및 CI·Pages 확인 완료.

[최종 검토 보고·명령·실행 로그](../../../result/development-closeout-20260909/README.md)에서 범위와 근거를 확인한다. [이전 요약 원문](../../history/build-and-test-pre-closeout-20260909.md)은 당시 기록으로 보존했다. 최신 미해결 사항을 숨기거나 과거 테스트 개수를 합산하지 않는다.

Operations는 승인된 MVP에서 placeholder다. 후속 변경은 기존 완료 SHA를 보존하고 영향 확인·해당 계획/승인·수정·검증으로 진행한다.

## 최종 수용 이전 보완 기록 — 2026-09-09T06:13:53.688628+00:00

웹 예시 등록·삭제는 사용자가 현재 시점에서 수용했다(사전 근거 미확인 보존). 입력 PBT3개(각200회, seed20260909, 기본 shrinking) 추가, 웹10 PASS/0 SKIP 및 최신 원격3b2c19d 포함 build PASS. 운영 Firestore 규칙은 변경되지 않았다. Python 소스/테스트도 기존6197a97과 동일하여 200 PASS/2 SKIP 근거 유지. README·제출 구조·필터 점검 완료. 과거 이 문서의 웹 PBT·승인 대기는 이 항목으로 해소. 최종 결과 사용자 수용 및 main 전달/CI는 아직 대기한다.

## 최종 전달 확인 — 2026-09-09T06:26:40.006695+00:00

사용자 원문: “최종 결과와 알려진 제한을 수용합니다. main 반영과 CI 확인 후 개발 완료로 마감해주세요.”

PR #4 merged, main `0a23c49748107279139d240275b1e0cadf9db9ce`. Python CI34318706218와 웹/Pages CI34318706589 모두 SUCCESS. 각 step/시각/공개 페이지 응답은 [최종 CI 영수증](../../../result/development-closeout-20260909/final-delivery-ci.json)에 보존한다. 기존 실제 Excel·Agent 시연과 최신 CI는 별도 검증 조건이다. 이후 마감 문서 커밋은 검증된 코드 트리를 바꾸지 않는다.

최종 main Python CI는 Python3.12/Windows에서 200 passed, 2 skipped in199.89s를 기록했다. 로컬 Python3.14 회귀319.60s와 별도 실행이다. final-python-ci-summary.json에 실제 CI 로그 발췌를 보존한다.
