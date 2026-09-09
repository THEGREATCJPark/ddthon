# 대화 UX 정합화 검증 — 2026-09-09

AI-DLC 기존 CONSTRUCTION의 승인된 `dialogue-ux-live-demo-code-generation-plan.md`를 실행했다. 사용자 승인 원문은 “어 승인”이며 구현 전 audit/계획에 기록했다. 공식 규칙·기존 승인·과거 실패 이력은 그대로다.

## 소스와 결과

- Python/C9 기준: `fff0ffac97fd52bd36995265c9ed14b12e2961c0`.
- 변경 경로39 PASS (`pytest-targeted.txt`), 전체 **144 PASS / 2 SKIP**, Hypothesis seed20260908 (`pytest-full.txt`). 실제 Excel 선택 테스트의 SKIP과 별도 실제 Agent 테스트는 합산하지 않는다.
- 웹 테스트7 PASS, production build PASS. 첫 build는 이 checkout의 node_modules 미설치로 tsc를 찾지 못했다. `npm ci` 후 성공했으며 `web-build-before-install.txt`를 보존했다. 의존성/lockfile 변경 없음.
- 로컬 웹 P0 4단계/P1 9단계·이전·초기화·차트 파일 로딩 검토. P1 사용자 환경 사실 턴 추가. 기존 로컬 승인 Skill1과 이번 신규 게시0→1을 구분하고, 사용하지 않던 데모20은 만들지 않았다.
- 추가 표시 결함: 완료 안내 div 때문에 `:last-of-type`이 마지막 대화를 찾지 못해 처음으로 스크롤됐다. 실제 마지막 대화 node를 선택하도록 수정했다. 이후 웹7 tests/build 재검증, 마지막 제목/스크롤 위치/두 차트 로딩을 브라우저에서 확인. Python 소스는 변하지 않았다.
- 좁은 in-app 브라우저의 첫 full-page 캡처에는 가독성과 중복 영역 문제가 있어 대표 증거로 쓰지 않는다. `web-p1-final.png`는 당시 검토 원본으로 보존하고 `web-p1-scroll-fixed.png`가 수정 후 화면이다. Chrome 클릭 도구 timeout도 있었으며 제품 실행 오류로 합산하지 않는다. 웹은 설명용 시뮬레이션이다.

## 실제 P1 2-turn Cold

**operator-assisted test**: 운영자가 준비된 파일을 열어 두고 승인된 두 번째 사용자 문장을 테스트 입력으로 전달했다. 실제 팀원이 대화했다고 주장하지 않는다. 같은 Claude session을 resume했고 초기 입력에 해결법/정답 배치/예측값은 넣지 않았다.

1. `BBBBB02_직전_3달_생산량.xlsx를 읽고 다음달 예상 생산량을 포함한 추세선을 보여줘.`
2. 실제 direct parser BadZipFile·Team Skill NO_MATCH → Excel에서 열어 볼 수 있는지 질문하고 턴 종료. 아직 후보/usage 변화 없음.
3. `이상하네, 난 엑셀을 열어서 데이터를 볼 수 있는데? 한번 다른 방법으로 진행해봐.`
4. 실제 실행 중인 Excel의 대상 workbook을 확인 → 현재 문서의 B/E열·9행부터 데이터를 읽어 업무 완료. 실제값2100/2250/2400, 2026-08 예상2550, PNG생성·최종 절대 경로 전달. 원본 hash 유지, 환경 절차 후보1/reuse0, 사람 승인/게시 없음.

`warm`이라는 준비 폴더명을 사용했지만 원격 Skill을 받지 않았고 초기 store에는 P0 Skill뿐이다. **이번 실행은 Cold**이며 기존 Warm 증거와 섞지 않는다.

`p1-verification.json`의 기대값은 제품 OLS self-check가 아닌 운영자별도 expected 값이다. `p1-status.json`에는 시작/턴1후/종료 store·usage·hash·session이 있다. `p1-turn-*-trace.json`과 `*-transcript.md`는 private thinking/signature를 제외한 전체 보이는 실행 로그다. `*-responses.md`는 설명만 따로 모았다. 원본 비공개 stream은 local TEMP에만 있고 제출하지 않는다. 중간 권한 거절을 삭제하지 않았다. 이번 procedure/task-mapping 형식 오류는0이다.

## UX 판정

- 개선 확인: 첫 턴 환경 사실 질문·실제 기다림, 두 번째 턴 실제 앱/대상 확인, 정확한 배치 입력(형식 재시도0), 전체 한국어 중심, 실제 chart 경로, 후보/게시 구분, 실제 검색 scope 표기.
- 남은 표현 한계: `dedicated` 한 단어, workbook/COM/일부 내부 옵션과 시트 배치를 진행 설명에 언급했고 첫 답변이 길었다. C9 지침이 모델 출력을 완전히 강제하지는 않는다. CLI는 `사내환경 · NASCA(가상)`을 표시했지만 Agent 자체 설명에는 이번에도 환경명을 명시하지 않았다. **모든 표현 목표가 완벽히 통과했다고 보고하지 않는다.** 실제 NASCA 원인 진단으로 과장하지도 않았다.
- Org Knowledge: 현재 CLI에는 별도 지식 source가 제공되지 않고 Team Skill만 검색했다. trace scope/query/result와 not_provided를 기록한다. 외부 조직 지식 연동을 구현했다고 주장하지 않으며 FR-P1-2의 조건부 의무를 삭제하지 않았다.
- 기존 exact approval/다른-workbook Replay/게시/Warm은 변경하지 않은 후보·lifecycle의 과거 증거다. 새 로컬 후보에 승인을 자동 생성하지 않았다. 다른 PC/Agent/문서를 항상 기술적으로 강제하는 보장도 아니다.

## 실제 P0 UI와 잔여

[`../live-demo-p0-20260909/README.md`](../live-demo-p0-20260909/README.md): **NOT_RUN**. 프로세스는 열렸으나 Computer Use 대상 창이 제공되지 않아 prompt를 입력하지 못했다. 실제 캡처 없음. 웹/이전 headless를 대체 증거로 쓰지 않았다. 사용자 직접 실행 안내4단계를 제공했다.

B-PC Warm/Git 왕복은 NOT_RUN 유지. 이번에 원격 게시·새 후보 승인·usage push를 재실행하지 않았다. Python CI/Pages exact SHA와 status는 `github-actions.json`, public 검토는 후속 completion receipt에 기록한다.


## Remote completion receipt

- Python CI: 9065a72284d93eb2fffdda51401f34638457e681, run34295654337, success. Latest change was an ASCII requirements comment; product tree equals the locally testedfff0ffa.
- Pages: 6fefa6bbfd3c2614771a81e9c7d5aba0ab19187a, run34295561705, success. Current web tree is identical.
- Public browser: https://thegreatcjpark.github.io/ddthon/?verify=6fefa6b#demo-p1 — index-Da_E1P2H.js; first actual-failure/NO_MATCH explanation and the second user-fact turn confirmed. public-environment-turn.txt/png are WEB SIMULATION evidence, not an actual Claude UI capture. Initial cached navigation showed the previous bundle; final navigation verified the updated bundle. A click tool timed out although the page advanced; preserved as a tool limitation, not a product failure.
- Local P0 four-step/P1 nine-step, counts/reset/back/scroll and chart loading checks remain in this folder.
- P0 interactive UI NOT_RUN; B-PC verification NOT_RUN. No new candidate approval/publish. Final evidence-only commit is distinct from tested/deployed source SHAs.
