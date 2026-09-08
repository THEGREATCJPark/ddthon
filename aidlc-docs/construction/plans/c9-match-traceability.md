# C9 진입점 + `match` CLI — 추적성 기록 (구현 후 기록, 소급 아님)

- **작성 성격**: **이 문서는 구현 이후(2026-09-08T10:28:56Z)에 작성된 추적성 기록이다.** 사전에 Code Plan/승인을 완료했던 것처럼 **소급 작성하지 않는다.** 이미 구현된 결과에 대한 **검토**와, 앞으로의 수정 계획을 구분해 기록한다.
- **목적**: 공식 AI-DLC(Code Generation = Part 1 Plan → 승인 → Part 2 Generation) 기준으로, C9(`.claude/skills/skillloop/SKILL.md`)와 `skillloop match` CLI 구현에 대응하는 **Code Plan·승인 근거의 소재와 누락**을 확인한다.

## 1. 대응하는 설계·승인 추적성

| 산출물 | 설계 근거(사전 승인됨) | Code Plan 아티팩트 | 사용자 승인(대화/audit) | 구현 상태 |
|---|---|---|---|---|
| **C5 `match.py`(모듈)** | components.md C5, component-methods.md C5 | **있음** — `plans/p0-u0u1-code-generation-plan.md`(S7, A 소유) | P0 Code Plan 승인(2026-09-08) | 구현·검증 완료(A 인계, `e07af72`) |
| **`skillloop match`(CLI 서브커맨드)** | FR-SURF-2(동사 예시 search), FR-MATCH-1~3 | **없음(누락)** | audit 2026-09-08(직전 턴 지시): "승인된 계약 호출하는 최소 CLI 연결 포함… 변경 파일·호출 흐름을 최소 계획에 기록하고 진행" | 구현·검증 완료(`810c9f6`), 전체 66 passed |
| **C9 `.claude/skills/skillloop/SKILL.md`** | components.md C9, component-methods.md C9, unit-of-work.md U0("C9 wrapper 통합 지점"), AD-Q6 | **없음(누락)** | audit 2026-09-08(직전 턴): "C9는 아래 최소 방향으로 조정해 구현을 승인" | 구현 완료(`810c9f6`) |
| **U3 C10/C11/C12** | u3-minimal-design.md | **있음** — `plans/u3-minimal-design.md`(§4 Code Plan) | U3 Code Plan 승인(2026-09-08) | 구현·검증 완료(`25ecfe5`) |
| **statusLine 연결(`.claude/settings.json`)** | FR-UI-1 | 해당 없음(제품 코드 아닌 프로젝트 설정) | audit 2026-09-08 | 설정 연결 완료(`34b0945`), 하단 바 표시=사용자 확인 대기 |

## 2. 누락 사실(지금 시점 기록)

- **C9 SKILL.md·`match` CLI는 공식 Code Generation의 Part 1(Code Plan 아티팩트) 없이 Part 2(구현)가 수행되었다.** 근거는 **대화/audit에 기록된 사용자 승인·지시**였고, 계획 내용은 audit·`aidlc-state.md` 산문에만 기록되어 있었으며 **`construction/plans/`의 별도 Code Plan 문서로는 존재하지 않았다.**
- 이 문서로 그 **누락 사실과 현재 구현 상태**를 기록한다. 기존 사용자 승인·실제 구현 이력(`810c9f6`, 66 passed, 실제 `match` 실행 결과)은 **보존**한다.

## 3. 구현 결과 검토(이미 구현됨)

- `skillloop/cli.py` `cmd_match` — 승인된 C5 `match.search` **호출만**(읽기전용; 적용·검증·카운트 없음; 매칭 로직 미복제). 실측: `match --signature pip-install-fail:skillloop-demo-pkg` → `MATCH fix-skillloop-demo-pkg-install@1.0.0(fit=2)`; 미관련 신호 → NO_MATCH.
- `.claude/skills/skillloop/SKILL.md` — 데모/실제 업무 요청 구분, run-p0 오용 금지, 원격 자동실행 금지·게시 게이트 유지.
- `tests/test_cli_match.py` 3건(MATCH/NO_MATCH/읽기전용). 전체 66 passed.
- **평가**: 구현은 승인 범위(얇은 연결·로직 미복제·카운트 경로 미추가)와 정합. **범위 초과·되돌림 없음.** 위 누락은 아티팩트 부재이지 구현 결함이 아니다.

## 4. 앞으로의 수정(있다면)

- 별도 코드 수정은 이 기록만으로 발생시키지 않는다. **P0 자연어 수용 검증의 남은 작업**은 `p0-nl-acceptance-plan.md`(검토 요청, 착수 전)로 분리한다.
