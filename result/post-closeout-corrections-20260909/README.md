# 승인된 후속 수정 결과

기록: 2026-09-09T07:33:34.985768+00:00. 제품 통합 main: `d77177b`. 기존 MVP 최종 수용은 유지한다.

| 수정 | 결과 |
|---|---|
| 한글 Windows 테스트 설정 | 실제 한글·공백 경로를 유지하고 pip.ini의 find-links만 ASCII file URI로 기록. 기존 검증 조건 유지. `02857b9` |
| legacy pip target | 옵션·URL·경로·wheel/압축파일·잘못된 형식을 설치 호출 전에 거부. 기존 bare distribution name 계약 유지. `02e16f7` |
| CLI 오류 표시 | 파일/설정/런타임/timeout 오류는 stderr와 비정상 종료로 보고. TypeError·AssertionError·KeyboardInterrupt와 argparse 종료 유지. `4734406` |
| P1 원본 ZIP | 11,270,872바이트 원본은 보존. 빌드 import만 커밋 고정 GitHub 다운로드 링크로 교체. `a906565` |

## 실제 검증

- Windows Python 3.14, `PYTHONUTF8=0` (cp949): **228 passed / 2 skipped**. UTF8 강제로 테스트를 회피하지 않았다.
- 같은 환경 `PYTHONUTF8=1`: **228 passed / 2 skipped**. 각 전체 실행의 명령·시각·종료코드는 [python-results.json](python-results.json)에 기록했다. SKIP 2건은 실 Excel opt-in 미실행 1건과 B 모듈 통합으로 미연결 전제가 없어진 테스트 1건이다.
- 웹 일반/10MB 초과 ZIP 제외 사본 각각 lockfile 설치·**10 tests PASS**·build PASS. 두 dist의 전체 파일 hash가 동일하다. 제외한 원본 ZIP은 삭제하지 않았다.
- 필터 적용 사본의 P1 탭에서 영상·자막·원본 ZIP 링크·실제 차트·응답·로그 표시를 확인했다. MP4/PNG/로그의 HTTP200 및 파일 바이트, 원본 ZIP HEAD200 확인. 영상 전체 재생은 다시 측정하지 않았다.
- 통합 `d77177b`의 Python CI 및 웹 테스트/권한 규칙/빌드/Pages 배포 **SUCCESS**: [CI 원본 상태](ci.json). 로컬 검증 이후 동시 웹 소개 슬롯 변경 `50ffe71`을 보존 병합했고, 해당 병합은 CI에서 검증됐다. Python 소스는 로컬 검증 이후 변경하지 않았다.
- 원본 ZIP SHA256: `fe2abcd51a1d1e53e73b40b2ec96eeaf9c86b7a2149ffca6e4acf335e995a879`. 기존 영상/이미지/로그·공식 AI-DLC 규칙 무변경.

## 범위와 AI-DLC 판단

사전 계획 `45e3275`와 사용자 “어 진행해봐 빠르게” 승인 뒤 구현했다. 계획의 항목별 순차 검증 대신 구현을 묶어 전체 검증한 실행 순서 이탈 및 늦은 상태 갱신은 audit에 보존했다. 항목별 커밋·실제 결과를 연결했지만 이를 소급해 완전 준수로 바꾸지 않는다. Inception/Units를 다시 시작하지 않은 후속 결함 수정이며 기존 개발 완료를 취소하지 않는다.

형식 검사로 원격 Skill의 신뢰 문제 전체가 해결되는 것은 아니다. 실제 악용·외부 설치 재현은 NOT_RUN이고, 잘못된 입력이 설치 함수를 호출하지 않는지는 대역으로 검증했다. P1 승인·독립 Replay·게시 게이트와 카운트 경로는 유지했다. 기존 라이브 Excel 검증/시연 근거는 그대로이며 새 라이브 시나리오는 실행하지 않았다.

효과 탭 제목·비교 회차·갤러리 표현·계정명 일괄 치환·Firebase 설정·가짜 chat-logs는 이번 수정에서 제외했다. 동시 웹 세션 변경은 해당 작성자의 변경으로 보존했다. 공식 QA 점수·finding 정본을 임의로 다시 매기지 않았다.
