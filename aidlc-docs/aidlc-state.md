# AI-DLC State Tracking

## 최신 상태 — 2026-09-09 오전 인계

- **현재 단계**: CONSTRUCTION / 통합 Build & Test. P0 자연어 재현 및 P1 Cold→사람 승인→독립 Replay→GitHub 게시→새 Agent Warm 실제 검증 완료. 전체 제품·제출 최종 승인 아님.
- **이번 추가 검증**: 동일 제품 소스 `96f3c85`에서 새 Claude Cold 3회 PASS(1100/600/0), 원격 Warm 1회 PASS(2550/reuse+1/candidate0). 코드 변경 없이 수행. 중간 권한/스키마 재시도와 Warm 설명 오류는 로그 보존.
- **사람 승인**: 사용자가 exact 후보 `file-access-8738e696cff8bbb20c98@1.0.0`, digest `359c5c1763416cdb3aa9828adef40219d1ac5448f82d62f91ebbca82768727af`의 검토·Replay PASS 후 게시·새 Agent 실행을 명시 승인. 실제 S3 기록 후 다른 문서 Replay PASS.
- **공유 근거**: `team-skill-store` Skill 게시 `28809464218e7328c7184a20bcafebb0e1b18916`, 재사용 이벤트 `04d831066e0fcdae3217412385e37dc0f08cae58`. 별도 mirror/store 수신, receiver local approval/Replay=null. 이벤트 첫 import1/반복0, 조직 총계1.
- **기존 회귀**: 139 PASS/2 SKIP 및 별도 실제 Excel 1 PASS; GitHub CI run34235737366 success. 이번 추가 사용자 시나리오 수와 합산하지 않음.
- **A/B 인수**: A PR#1 실제 merge `58adce9`, B 원작성 이력 merge `99cc4e5`. CJ가 완료 인수 코드 통합을 담당; A/B 동시 수정 대기 없음. B 다음 역할은 별도 PC Git 공유 시연 재현.
- **남은 것**: B PC 실제 재현 NOT_RUN, 상태줄의 공용 실적·팀 순위 표현 마무리, 최종 갤러리/README·시연 검토. 현재 인기·실적 상태줄은 로컬 기준, 조직 이벤트 데이터는 실제1.
- **기록**: `result/p1-acceptance/`, `construction/build-and-test/`. 제품 코드/C9 불변, 공식 AI-DLC 규칙 불변. 기존 audit append-only, UTC 시각 매번 취득. S3/DB adapter는 구현 아닌 확장안.


## 과거 인계 상태 — 2026-09-08 초기 Codex/Astra 인수 기록

- **현재 게이트**: CONSTRUCTION / P0 3회 재현·전체93 PASS 기준 확정 후 사용자 조건부 허가로 P1 구현 진행. A/B 인수 코드와 CJ S2/S3/C4 연결·검증 중. 실제 Excel 시도 FAIL_TIMEOUT, 전체 P1 완료 아님.
- **CJ 메인 수정자**: Claude Code가 수정 중단·백그라운드 작업 없음으로 인계 보고한 후 Codex/Astra가 인수. main 기준 `a22e1764527e89d73c648f890fa173527d99900e`. 도구 교체는 새 구현·계획 승인으로 간주하지 않는다.
- **P0 수용 결과**: 새 Claude Code 일반 업무 요청 → 기존 작업 venv 실제 실패 → C5/S1/C3 → reuse=1 → 독립 import/version PASS. 신규 14 tests, 깨끗한 snapshot 전체 80 passed/0 skipped. 설치 후 재요청 +0. result/p0-nl/ 참조.
- **보존**: README.md/EVALUATION.md 사용자 미커밋 변경, 모든 기존 승인·audit·팀원 코드 이력. 이 절은 당시 인수 기록이며, 현재 판단에는 문서 최상단의 최신 상태를 우선한다.
- **A 전달 수신**: PR #1 cb25a62의 3파일을 작업 트리에 원문 인수. GitHub PR merge는 미수행. P0 회귀와 P1 실제 연결을 현재 소스에서 검증 중.
- **B 전달 수신**: 1760d32 코드·U2문서 인수, B audit/state는 handoff 파일로 보존. CJ가 인수한 envharness/replay 무결성·정리 결함 수정. B환경61 PASS와 이번 PC Excel FAIL_TIMEOUT을 구분.
- **파일 소유권(최신)**: A=match/reuse_service와 담당 테스트 유지. B는 담당 범위 완료(`1760d32`) 보고 후 작업 종료, 사용자 대행 요청(2026-09-08)에 따라 envharness_p1/replay와 담당 테스트도 CJ가 인수. CJ=공통부·cli·C9·U3 및 experience_service/publish_pipeline/gitsync. B의 과거 작성 이력·저작자는 보존한다. P1 수정·통합은 P0보다 후순위이며 새 범위 추가는 별도 계획 검토 대상이다.
- **P1 통합 검토**: A 경로/dataclass 수정 인수, B digest mismatch 접근 전 차단·소유 Excel만 정리·placeholder 정직 표기 수정. 테스트 대역/로컬 Git 통과, 실제 Excel COM 시도 시간 초과 미해결.
- **전체 Build and Test**: 미완료. P0 수용 검증은 완료했으며 전체 제품 완료·제출 승인은 아니다.

## Project Information
- **Project Name**: Agent SkillLoop (MVP)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-08T14:45:14Z
- **Current Phase**: CONSTRUCTION
- **Current Stage**: CONSTRUCTION / 통합 Build & Test — P1 추가 Cold3/Warm1, 사람 승인·독립 Replay·GitHub 게시/usage 왕복 PASS. B PC 재현·팀 UI/최종 제출 검토 남음.
- **(이전) Current Stage**: **CONSTRUCTION 진입 — Units Generation 승인됨(정정 3건 반영, 2026-09-08)**. 다음: U0 P0 필수 + U1 최소 Functional Design → NFR Requirements(minimal) → Code Plan. **정정**: (1) U3 소유자=**CJ**('여력' 폐기), UI·조직 집계는 승인된 **필수 범위**(P0 비블로킹 ≠ 선택 기능); **U2(B) Day2 대기 해제**(계약+게이트 충족 시 즉시 병행 착수). (2) **파일별 단일 수정자**: usage.py=CJ(카운트+공유 이벤트), cli.py=CJ, gitsync.py=B(전송; 검증·dedup은 usage.py=CJ), envharness_p0.py=CJ/envharness_p1.py=B('함수별 분담' 폐기); U3 집계·표현=읽기전용, C3 공유 이벤트 import=상태 변경(쓰기). (3) 계약 5 **비블로킹**으로 정정, U0 전체 완료 대기 없이 P0 최소 계약+로컬 저장·카운트·환경 인터페이스 확정 후 U0/U1 **병렬**. **코드 작성은 설계·Code Plan 승인 + 공통 기준 SHA·작업 경로 확인 후.**
- **(이전) Units Generation (minimal) — 산출물 생성 완료**: Unit 정의(U0 공통·계약·통합/CJ, U1 P0 재사용 실행/A 최호길, U2 P1 경험·후보화·게시/B 한석훈, U3 조직 집계·표현·재사용 이벤트 공유, Q1 독립 QA 횡단/C 윤여훈), 의존성·계약 동결(1~8, P0 최소셋=1·3·4)·착수 순서(17:30 P0 앵커)·스토리 매핑(7개 전부 배정). 산출물: `application-design/unit-of-work.md`, `unit-of-work-dependency.md`, `unit-of-work-story-map.md`, `plans/unit-of-work-plan.md`.
- **(이전) Application Design Request Changes(2건 계약 보완)**: (1) **C10 상태 조회 경로**: S3에 읽기전용 상태 조회 계약(`list_lifecycle_states`/`query_lifecycle_state`, `remote_publish_evidence`/`local_review_evidence`) 신설, C10은 이를 통해서만 상태 조회(추정·게이트 재구현 금지). (2) **재사용 이벤트 공유 자격 분리**: `export_shared_usage(scope=VERIFIED_REUSE)`로 Skill 게시 게이트(SHAREABLE)와 분리, C3가 검증·event_id dedup, `sync`→C3/C4.push_shared_usage 경로는 S3.publish와 독립(A게시→B import→B 검증 성공→B 공유→A 1회 반영). 의존성 매트릭스·다이어그램·텍스트대안(C4→C3, C10→S3, localhost HTTP)·"네트워크 서비스 없음" 범위·UI 프레임워크 단계 표기·채택 repo/branch vs 미정 로컬 경로 정합화. **Application Design 전체 승인·Units Generation은 재검토 후 결정**(REVIEW REQUIRED).

## Workspace State
- **Existing Code**: Yes — P0 코어, U3 로컬 UI, C9 및 match CLI 구현됨. 자연어 P0 수용 PASS, P1 통합은 미완료.
- **Programming Languages**: Python >=3.10 (Windows-native)
- **Build System**: pyproject.toml / setuptools, pytest + Hypothesis. 깨끗한 환경의 wheel 빌드 의존성 정합성은 P0 계획의 검증 항목.
- **Project Structure**: skillloop/ (소스), tests/, .claude/skills/skillloop/, aidlc-docs/
- **Reverse Engineering Needed**: No (Greenfield)
- **Workspace Root**: C:\Users\cik61\Desktop\ddthon-main

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Extension Configuration
| Extension | Enabled | Mode / Note | Decided At |
|---|---|---|---|
| Security Baseline | No | 전체 강제 미적용(Q12=X). 단, 핵심 보안 요구(secret·원본 데이터 비공유, read-only 승인 접근, 입력/무결성 검증, 원격 Skill 자동 실행 금지)는 일반 요구사항(NFR-SEC-*)으로 유지 | Requirements Analysis |
| Resiliency Baseline | No | 전체 강제 미적용(Q13=B). 단, 중복 방지·충돌 처리·sync 실패·재시작 보존만 요구사항(NFR-RES-*)으로 유지 | Requirements Analysis |
| Property-Based Testing | Yes | **Partial** 모드(Q14=B) — 강제: PBT-02, PBT-03, PBT-07, PBT-08, PBT-09 (round-trip/invariant/generator/shrinking·reproducibility/framework). 그 외 advisory. 적용 대상: 직렬화 round-trip, digest·dedup 등 순수·불변 로직 | Requirements Analysis |

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection
- [x] Reverse Engineering — SKIP (N/A, Greenfield)
- [x] Requirements Analysis (승인됨)
- [x] Workflow Planning (승인됨)
- [x] User Stories — EXECUTE (minimal) — 승인됨 (stories.md/personas.md)
- [x] Application Design — EXECUTE — **승인됨**(2026-09-08). Request Changes 2건 반영 + S3→C3 제외 판단 사용자 동의.
- [x] Units Generation — EXECUTE (minimal) — **승인됨**(2026-09-08, 정정 3건 반영: U3=CJ·필수 범위, 파일별 단일 수정자, 계약5 비블로킹·P0 병렬)

### 🟢 CONSTRUCTION PHASE (진입, per-unit loop 시작: U0 P0 필수 → U1)
- [x] Functional Design — EXECUTE (per-unit) — **P0(U0 P0 필수 + U1) 승인됨(2026-09-08, 정합화 3건 반영: 카운트 쓰기=C3 단독, run_id=실행 식별, 허용 index는 descriptor.procedure 근거)**. U2/U3 Functional Design은 이후 별도.
- [x] NFR Requirements — EXECUTE (per-unit, minimal) — **P0 승인됨(2026-09-08)**: pytest+Hypothesis 채택·의존성 명시, "네트워크 미의존"=외부 인터넷 미의존, mock index 제공 방식은 Code Plan 구체화.
- [ ] NFR Requirements — EXECUTE (per-unit, minimal)
- [ ] NFR Design — SKIP
- [ ] Infrastructure Design — SKIP
- [ ] Code Generation — EXECUTE (per-unit) — **Part 1(Code Plan) 승인됨(2026-09-08)**. **Part 2**: S0 `8ccbfdc` → S6 스텁 `b0ee495` → CJ S2~S5+cli `986d1cc` → e2e 본문 `c811316` → **C-a/C-b(store.py) `ef03b3a`, C-d(usage.py+cli.py) `cfc62e9`** → **U1(P0) A 인계 통합·실제 검증 완료 `e07af72`(main)**. **A 인계**: 패치 2파일 sha256 동일 → 중복 미적용, 별도 통합 branch `integ/u1-p0-875c97e`에서 `git am` → `9dea075`(저작자 hogil 보존, match.py/reuse_service.py). CJ `e07af72`: e2e unskip + 실제 Windows 버그 수정(run-p0 출력 유니코드가 cp949 콘솔에서 UnicodeEncodeError로 카운트 직전 크래시 → `_ensure_utf8_stdout()` UTF-8 reconfigure). **실제 검증: pytest 42 passed / 0 skipped(회귀 없음) + 실제 run-p0 2회 reuse=1→2, usage.json counts=2·events 2건·seen_run_ids 2건·share-export 동작.** **P0 실제 재사용 루프 완료(파일 존재 아닌 실행 결과로 판정).** 병합: `integ/u1-p0-875c97e`(9dea075→e07af72)→main fast-forward. README/EVALUATION 로컬 변경 미커밋 보존. **B 대기 정합화**: "구현 SHA 대기"→"실제 계약 연결·검증 대기"(P0 SHA=e07af72). 잔여: U2(B) Code Plan, U3(CJ), Build and Test.
- [ ] Build and Test — EXECUTE

### 🟡 OPERATIONS PHASE
- [ ] Operations — PLACEHOLDER

## Execution Plan Summary
- **실행**: User Stories(minimal), Application Design, Units Generation, Functional Design(per-unit), NFR Requirements(per-unit, minimal), Code Generation, Build and Test
- **생략**: Reverse Engineering(N/A), NFR Design, Infrastructure Design, Operations(placeholder)
- **다음 단계**: B PC에서 게시 Skill 가져오기·Warm·usage 공유 시연, 상태줄 팀 지표 정리, 최종 결과 검토. 기존 Application Design/Units 승인을 재요청하지 않는다.
- **문서**: aidlc-docs/inception/plans/execution-plan.md

## 승인된 SKIP 경계 (Workflow Planning 승인 시 확정)
- **SKIP-BOUNDARY-1**: NFR Design 생략 ≠ 요구 면제. 승인된 핵심 보안(NFR-SEC-1~4)·무결성(digest, FR-SKILL-4)·복원력(NFR-RES-1~4)은 해당 Unit의 Functional Design과 테스트에 반드시 반영한다. **(범위 변경 확장)** UI·동기화 Unit: 읽기전용 경계(NFR-SEC-2)·secret/원본 비표시(NFR-SEC-1)·동일 집계와 실적/DEMO_SEED 구분(FR-UI-3)·공유 usage dedup(FR-USAGE-4, FR-ORG-3)도 설계·테스트에 반영.
- **SKIP-BOUNDARY-2**: Infrastructure Design 생략 ≠ Git 원격 동기화 축소. 채택된 원격 sync 요구(FR-SYNC-1, Q3=A + 범위 변경으로 team-skill-store branch 채택)는 유지되며 로컬 Git만으로 축소하지 않는다. 원격 clone/pull/push·무결성·CONFLICT·실패 보존 유지. 실제 branch·Git 경로·세부 운용은 미결정(설계 승인 + Units 담당 확정 후 초기 구현 준비).

## 범위 변경 이력 (Scope Changes)
- **SCOPE-CHANGE-1 (2026-09-08, 승인됨)**: UI 추가(상태줄 FR-UI-1 + 로컬 읽기전용 대시보드 FR-UI-2, 동일 집계 FR-UI-3) + 조직 집계(FR-ORG-1~5, FR-USAGE-4) + Git 공유 방식 변경(별도 private 저장소 전제 → 동일 저장소 `team-skill-store` branch, 로컬 DB 미전송 FR-SYNC-5). 근거·영향: `plans/change-impact-ui.md`. **과거 Q3=A("별도 private 저장소")·기존 승인 이력은 보존**하고 이번 변경으로 일반화. 표현 참고=ttt(상태줄, organization.html; 백엔드 중앙 API 미채택, 소스≠렌더링). export=SHAREABLE 유지(최초게시·재시도 가능), PUBLISHED=원격 push 성공 후에만.

## Notes
- **U2 공통 의존성 계약 — 승인·구현 진행(2026-09-08)**: 산출물 `construction/plans/u2-shared-dependency-contracts.md`(승인 조건·최소 Code Plan 포함). **이 승인은 CJ 공통 의존성 계약·구현에 한정 — B의 U2 전체 설계/Code Plan 승인 아님.**
  - **C-a/C-b 구현 완료(store.py, C2)**: lifecycle `save/load_lifecycle_state`·`list_lifecycle_records`(저장만·전이 미판단, 키=id/version/digest); descriptor `export_bundle(refs 허용목록·3자 digest 일치·content만)`/`import_bundle(digest 재계산·위조 거부·DEDUP/CONFLICT·content만·승인/Replay 미생성)`. **검증: 전체 26 passed / 8 skipped**(기존 19→26). commit/push·SHA 보고 진행.
  - **C-d 구현 완료(usage.py C3 + cli.py C8)**: 스키마 `{counts,seen_run_ids,events}`(하위호환); `compute_event_id`(결정적·재전송 dedup 키); `record_actual_reuse`가 counted=True & digest 있을 때만 이벤트 생성(카운트·run_id dedup 불변); `export_shared_usage`(VERIFIED_REUSE만)/`import_shared_usage(blob, local_ref_exists)`(재검증·event_id dedup·로컬 존재 확인, counts 미변경); exact 참조·reuser_alias는 호출자(cli, env `SKILLLOOP_ALIAS`) 제공; CLI `share-export`/`share-import` 추가. **역산 금지**(digest 없는 evidence는 이벤트 미생성). **검증: 전체 34 passed / 8 skipped**(26→34). commit/push·SHA 보고 진행.
  - **제공 순서(B)**: ①store.py(C-a+C-b, 완료) ②usage.py+cli.py(C-d, 완료) ③P1 A·B 조율(P0 독립, B·A 합의 대기).
- **A(U1) 인계 상태 — 통합·검증 완료(2026-09-08)**: A push 403 차단 → 패치 전달. 패치 2파일 sha256 동일(중복 미적용). 최신 main 기준 별도 통합 branch `integ/u1-p0-875c97e`에서 `git am` → `9dea075`(저작자 hogil 보존). CJ 통합 `e07af72`(e2e unskip + Windows UTF-8 출력 버그 수정) → main fast-forward. **실제 검증 완료: pytest 42 passed/0 skipped + run-p0 실제 2회 reuse=1→2.** V5~V8·V12(run-p0 e2e) **NOT_RUN → PASS.** P0 통합 SHA=`e07af72`(docs `7256272`)를 B에게 전달(B 대기="실제 계약 연결·검증 대기"로 정합화).
- **P0 CLI 사용 확인(2026-09-08)**: 사용자 직접 `python -m skillloop run-p0` 실행 → 실패 관찰→MATCH→reuse=3(counted=True). **변경·오류 없으면 P0 반복 테스트 중단.**
- **P1 환경 모델 승인(2026-09-08)**: 사용자 승인 = B의 **Office 암호화 합성 파일 + 열린 Excel read-only 접근 모델** + **P1 한정 Excel 의존성 예외** → A/B 전달. **독립 Replay·게시 게이트 유지.** "환경 모델 선택 대기"로 **되돌리지 않음** — A/B의 구체 계약·계획 반영·구현을 기다린다. (이전 "의존성 미설치 재현" 대안은 철회됨.)
- **U3(CJ) 최소 설계 준비(2026-09-08)**: 승인된 필수 범위(조직 집계 C10·상태줄 C11·읽기전용 대시보드 C12) 최소 Functional Design+NFR(minimal)+Code Plan 작성 → `construction/plans/u3-minimal-design.md`(REVIEW REQUIRED). CJ 단일 수정자(org_aggregator.py/statusline.py/dashboard.py + cli.py), B 파일 미수정 → P1과 독립 병렬. **열린 결정 2건 확정(2026-09-08)**: ①lifecycle 상태=**보류형** — `LifecycleView`(계약7 형태) provider에만 의존, 미연결 시 "상태 조회 미연결"(0·추정 금지), **실제 경로 store 직접 읽기 우회 금지**, 테스트는 계약7 형태 명시적 test 대역, B 제공 시 연결; 이 결정으로 나머지 U3 대기 안 함. ②대시보드=**stdlib http.server** 127.0.0.1·정의된 GET 경로만·파일 임의 노출 금지.
  - **U3 Code Plan 승인·구현·검증 완료(2026-09-08)**: 신규 `org_aggregator.py`(C10)·`statusline.py`(C11)·`dashboard.py`(C12) + `cli.py` `status`/`dashboard` 서브커맨드(P0와 동일 `.skillloop_demo/` 경로 연결). 정직성 기준 반영(게시=lifecycle만·미연결시 "확인 불가", 원격 게시=remote_publish_evidence 있을 때만, 로컬 vs 조직 구분, 실적/DEMO 구분). **검증: U3 단위 21 passed + 전체 63 passed(42→63, 회귀 없음); `skillloop status` 실데이터(reuse=3) 확인; 대시보드 실 HTTP(127.0.0.1) GET 200·정의외 404·POST 405·본문 정직성 확인.** **하단 상태줄 연결은 사용자 settings 필요 → 실제 확인 전이므로 연결완료 보고 안 함.** lifecycle/last_sync 실데이터·조직 시연=계약7·C4 연결 후 **NOT_RUN**.
- **사용자 화면·Agent 연결 마무리(2026-09-08)**:
  - **대시보드 실 HTML 검증**: 브라우저 렌더링 도구 없음(WebFetch=http→https 강제, localhost 미도달) → 각 경로(/,/skills,/skill,/people,/activity)의 실제 서빙 HTML을 UTF-8로 취득해 **실데이터(top_skill=fix-skillloop-demo-pkg-install, 재사용 3, actual_reuses=3, demo=0) 표시·정의외 404·traversal 404·POST 405** 확인. /skill 상세 **procedure 미노출 재확인**(word 'procedure'/action/index:'allow' 부재; applicability 신호 'pip-install-fail'만=의도된 비민감 매칭 값). **HTTP/HTML 바이트 확인 완료 ≠ 브라우저 육안 가독성 확인(=사용자 몫).**
  - **statusLine 실제 연결**: 사용자 `~/.claude/settings.json`(Bedrock 토큰 포함) **무수정 보존**. 프로젝트 **`.claude/settings.json` 신설**(`statusLine`: type=command, command=`python -m skillloop status`). 실행 Python=3.14(/c/Python314), cwd=프로젝트 루트, 데이터=`os.getcwd()/.skillloop_demo`(P0 동일). Claude Code 호출 형태(stdin JSON 주입) 시뮬레이션: **exit 0·단일 라인·재사용 3 출력**. **현재 창 하단 바 실제 표시=세션 재적용 필요·직접 관측 불가 → 사용자 확인 항목(연결완료 미보고).**
  - **C9 AgentSkillWrapper**: **미구현**(`agent_skill/`·`.claude/skills/` 부재) 확인. 승인 범위(handle_natural_language(request)->CliInvocation, 얇은 wrapper, 로직 중복·원격 자동실행 금지 NFR-SEC-4) **최소 구현 계획 제시**(파일·호출 흐름·검증) — **승인 전 미구현**. **상태줄 출력만으로 Agent 연결 완료 보고하지 않음.** 수용 기준=자연어 요청→CLI 매핑→명시적 CLI 실행(run-p0)→검증 성공 시 C3 카운트 갱신(라이브 장면=사용자 확인). **wrapper는 카운트 경로 미추가**(실제 재사용 성공과 무관한 카운트 증가 없음).
  - **C9 조정 범위 구현·검증 완료(2026-09-08)**: 사용자 조정 승인 반영 — **별도 wrapper.py 키워드 매핑기·그 매핑 검사 테스트 미생성.** 진입점=`.claude/skills/skillloop/SKILL.md`(자연어 해석=Claude, 제품 로직=기존 CLI/서비스). 구현: (a) **`.claude/skills/skillloop/SKILL.md`**(신규) — 요청 3분류: 명시적 P0 데모→`run-p0`(자체완결·"실제 업무 적용" 보고 금지), 실제 설치·업무→**run-p0 대체 금지**·실제 관찰→`skillloop match` 검색→절차 적용·실제 검증→**검증 성공 시에만 실적 보고**, 조직 현황→`status`/`dashboard`. 원격 자동실행 금지(NFR-SEC-4)·게시 게이트·비밀 미포함 유지. (b) **`cli.py` `match` 서브커맨드**(신규) — 승인된 검색 계약 **C5 `match.search` 호출만**(읽기전용, 적용·검증·카운트 없음, 매칭 로직 미복제). (c) **`tests/test_cli_match.py`** 3건(MATCH/NO_MATCH/읽기전용 usage 미생성). **검증: 전체 66 passed(63→66, 회귀 없음); 실제 `skillloop match --signature pip-install-fail:skillloop-demo-pkg` → MATCH fix-skillloop-demo-pkg-install@1.0.0(fit=2) exit 0; 미관련 신호 → NO_MATCH exit 0.** **남은 차단**: 임의 실제 업무 대상의 **일반화된 적용·검증·카운트**는 A의 **P1/RU4 확장 대기**(`reuse_service.apply_and_verify`가 P0 harness 타깃 TARGET_PKG/VERSION/IMPORT에 결합) → 실제 업무 **실적 반영은 그 연결 후 NOT_RUN**. **새 Agent 라이브 사용 장면**(합성 업무 환경+업무 요청만 제공→Skill 사용→실적)=**사용자 확인**. 카운트는 검증 성공 경로(C3)만 — match/CLI에 카운트 경로 미추가.
- **소유권 이관 대기(2026-09-08)**: B에게 `envharness_p1.py`/`replay.py` **유지**, `experience_service.py`/`publish_pipeline.py`/`gitsync.py`를 **CJ 이관하는 안 전달**됨. **B의 작업 종료 확인 + 현재 커밋 수령 후에만** 해당 파일 소유권을 기록·인수한다. 그 전까지 **현재 B 소유 유지**(CJ 미수정). A는 승인된 P1 연결 구현 계속.
- **CJ 최우선 목표 정합(2026-09-08)**: **CJ 최우선 = 승인된 P0 자연어 수용 검증**(US-P0-1). A/B의 현재 승인 작업 유지. 아래 항목은 추가 구현 포괄 승인이 아니다.
  - **C9/`match` 추적성 확인(구현 후 기록, 소급 아님)**: `skillloop match` CLI와 `.claude/skills/skillloop/SKILL.md`(C9)는 설계 근거(components/component-methods/unit-of-work U0·AD-Q6)와 **대화/audit 승인**은 있으나 **`construction/plans/`의 Part 1 Code Plan 아티팩트는 없이(누락)** 구현되었다(계획 내용은 audit·state 산문에만 존재). 누락 사실·현재 구현 상태를 지금 기록 → `plans/c9-match-traceability.md`. **기존 승인·구현 이력(`810c9f6`, 66 passed) 보존, 소급 작성 없음.** C5 `match.py` 모듈·U3는 Code Plan 아티팩트 있음(각각 p0-u0u1-code-generation-plan.md S7, u3-minimal-design.md).
  - **P0 자연어 수용 검증 남은 작업**: `match`(검색)는 기존 코드로 가능. **요청 기반 실패 재현(AC-1)·관찰 기반 적용+검증+카운트(AC-3/AC-5, 비-run-p0)**는 미구현 — run-p0는 자체완결(requirements.txt 미참조·대상 하드코딩)이라 대체 불가. **실제 계약 차이 확인**: `reuse_service.apply_and_verify`가 harness 합성 상수(TARGET_VERSION/IMPORT)·index 이름에 결합 → 합성 범위 한정. **최소 수정 Code Plan(검토 요청, 착수 전)** → `plans/p0-nl-acceptance-plan.md`(신규 `apply-requirements` 오케스트레이션 + 합성 픽스처, 기존 C5/S1/C3/C7 **호출만**, A/B 미수정). **승인 전 미착수.**
  - **소유권 이관 확인(8c7999a)**: B 커밋 **`8c7999a`**(hanseokhun, 2026-09-08 19:20 KST, "feat(u2): ① envharness_p1 run_file_access_procedure + 실제 Excel attach 검증") `origin/work/u2-p1-git` HEAD로 **확인**. 해당 브랜치에는 `envharness_p1.py`+테스트만 존재하고 **`experience_service.py`/`publish_pipeline.py`/`gitsync.py`·`replay.py`는 아직 미생성** → 이관은 **(미생성) 파일의 구현 소유권을 B→CJ로** 넘기는 것. **소유권 인수 ≠ 해당 파일 새 구현 승인**(구현은 별도 승인). **CJ의 해당 구현은 P0 자연어 수용 검증보다 후순위.** B는 `envharness_p1.py`(8c7999a 구현)·`replay.py`(미생성, 책임 유지) 보유.
- **Process/provenance 정합성 정정(제품 scope change 아님)**: 이 시점 이후 구현 기준은 현재 `ddthon`에서 본선 중 생성·승인된 Requirements/User Stories/Workflow Plan/Application Design 및 이후 승인될 Units/Functional Design/Code Plan과 현재 실제 실행 증거다. Application Design 전체 승인 대기 상태는 유지한다. UI는 사용자 승인 FR-UI/FR-ORG 자체를 근거로 유지한다.
- **외부 사전 구현 Reference 사용 중단**: `ttt`를 포함한 사전 구현의 검색/Fetch/Open/Read/비교/코드 복사/테스트 결과 참조를 중단한다. 필요 시 이유·범위를 먼저 제시하고 사용자 승인을 기다린다. 현재 산출물·실제 오류부터 조사하며 과거 외부 PASS/코드 구조를 본선 완료 근거로 사용하지 않는다. 과거 audit/chat/변경 검토 및 위 SCOPE-CHANGE-1의 참고 사실은 보존한다.
- **Audit timestamp correction**: 과거 일부 entry의 workflow 시작 timestamp 반복은 capture 오류이며 동일 시각의 이벤트를 뜻하지 않는다. 기존 entry는 수정하지 않고 correction note를 append한다. 이후 각 entry 작성 직전에 PowerShell `Get-Date`로 OS 현재 시각을 새로 취득해 UTC ISO 8601(`Z`)로 기록하고 고정 timestamp를 재사용하지 않는다. 취득 실패 시 `timestamp unavailable`로 표시한다.
- 사용자 제약: 팀 4명, 개발 시간 제한(9/8 오후 ~ 9/9 오후), Windows-native 목표.
- 통합 위험 회피: 공통 state/lifecycle을 여러 세션이 동시 수정하는 구조 지양 (Workflow Planning/Units 단계에서 반영).
- 평가 제출 요건: 실제 source + aidlc-docs 전체 + README + 동작 screenshots/result 보존. Inception 과확장 지양.
- seam (a)~(g)는 **후보**이며 Unit 수·담당자·상세 구조는 Application Design/Units Generation에서 확정. seam (g)=조직 집계 read-model + 재사용 이벤트 공유(VERIFIED_REUSE, 게시와 독립) + 표현 표면(상태줄/대시보드, 범위 변경).
- **Units Generation 참고 방향(확정 아님)**: "CJ 통합·공통부 / A·B 개발 / C 독립 QA 운영" 방향을 우선 참고하되 **4명을 4개 개발 Unit으로 고정하지 않는다.** 실제 Unit 경계·사람 배정은 Units Generation에서 계약을 근거로 결정.
- **Request Changes(2건) 처리 계약 요약**: (1) S3 읽기전용 상태 조회 계약 신설 → C10이 유일 경로로 상태 조회(추정·게이트 재구현 금지, 원격 게시본은 remote_publish_evidence/local_review_evidence 분리·수신 환경 승인/Replay 미생성). (2) 재사용 이벤트 공유 자격 VERIFIED_REUSE(정확한 Skill 참조+실제 성공 근거+비-DEMO)를 SHAREABLE 게시 게이트와 분리, C3 검증·event_id dedup, sync 경로는 S3.publish와 독립. 신규 Skill 게시 게이트는 유지. 반영 파일: components/component-methods/services/component-dependency/application-design/execution-plan.

## 후속 검토 — 하단 상태줄 / A 전달 갱신
- 하단 상태줄 여러 줄 표현·새 작업 설정/데이터 경로 누락 확인. u3-statusline-followup-plan.md 사전 계획 REVIEW REQUIRED. 제품 코드/설정 미수정.
- A PR #1 최신 수신 cb25a62: 요청 3건 코드 반영 확인. 아직 main 미병합, 실 Excel 통합 NOT_RUN. 이전 A SHA는 과거 수신 기록으로 보존.

## 하단 상태줄 구현 완료
- 승인 계획 S1–S6 완료. 관련 30 tests, 전체 86 passed/0 failed/0 skipped. 실제 하단 네 줄 표시는 사용자 확인 완료. result/statusline/ 참조.
- 사용자 P0 실제 작업 venv import/version 1.0.0 및 run_id 27dd984514ab4f6ca4e0d206985449f0, 실적 1을 독립 확인했다. 중간 잘못된 match 안내/경로 연결 정정.
- A cb25a62는 리뷰 수신 완료, 아직 main 미병합. 추가 A 개발 요청 없이 CJ 통합 검증으로 넘길 수 있다. 이 변경은 아직 commit/push하지 않았다.

## P0 관찰 계약 결함 재검증 완료

사용자 피드백 중 초기 raw signature 및 작업 store 혼선은 수용, 후속 apply-requirements 성공까지 FAIL로 변경하는 판정은 미수용. 공통 정규화와 관찰 입력을 보완하고 21+22 대상 검사 PASS, 새 Claude 업무 요청 실제 count 1→2 확인. 기존 사용자 venv·store·requirements 보존. result/p0-observation/ 참조. 최초 별도 pip 호출은 권한 거절, 이후 제품 내부 실제 pip 실행과 명확히 구분. 변경은 미커밋이며 공식 규칙·README/EVALUATION 미변경.

## P0 재현 기준 및 P1 인수 구현 결과

P0: 새로운 checkout-local Python으로 Claude3개 작업 환경 재현PASS, 같은 범위 전체93 PASS. 2번 첫 시도 권한/API 중단을 보존하고 재시도PASS, result/p0-reproduction/ 참조. 이는 단일 합성 패키지 범위다.

P1: 사용자 조건부 허가 충족 후 A cb25a62/B1760d32 인수 및 S2/S3/C4·CLI·S3/C4 조회 연결 구현. 통합 회귀130 PASS/2 SKIP. 그 뒤 추가된 CLI/조회2건을 포함한 서비스9 PASS. 이 수치를 단순 합산하지 않는다. 실Excel 시도는 FAIL_TIMEOUT으로 남겼고 이후 자동suite의 live opt-in 제외와 구분한다. Git 전송은 실제 local bare 왕복PASS, GitHub게시/ClaudeP1탐색·사람검토·Warm 종단은 NOT_RUN. 전체 Build and Test·제출 완료 아님. 사용자 README/EVALUATION·공식 규칙 보존, 현재 미커밋/미푸시.
