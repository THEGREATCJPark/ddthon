# P0 자연어 수용 검증 — 최소 수정 Code Plan (개정 2, 구현·검증 완료)

> 사용자 “어 진행해.”로 개정 2 승인. 실제 승인 수신 기록은 audit.md의 해당 이벤트를 참조한다. 아래 작성 당시 미승인 설명은 이력이며, 현재 실행 기준은 개정 2 R1–R7이다. Part 2 구현·검증 완료. 현재 코드 산출물 REVIEW REQUIRED이며 전체 제품 완료는 아니다.

> **개정 2 · 2026-09-08T10:40:03Z · Codex/Astra 인계 후 작성.** 아래 개정 2가 향후 구현의 검토 대상이다. 이 문서 하단의 초안은 비교·이력 보존용이며 실행하지 않는다. 기존 초안과 이번 개정 모두 아직 승인되지 않았다. 제품 코드·테스트·새 Agent 수용 실행은 미착수다.

## R1. 영향 판단과 승인 범위

- 근거: FR-SURF-1~3, FR-P0-1~4, FR-MATCH-1~3, FR-USAGE-1~3, US-P0-1 AC-1~5. 새로운 제품 요구가 아니라 기존 사용자 흐름의 미구현 연결을 보완한다.
- 현재 위치: CONSTRUCTION / U0-C9 및 P0 연결 / Code Generation Part 1 수정 계획 REVIEW REQUIRED. 인계는 이 계획의 구현 승인이 아니다.
- 기존 Requirements/Stories의 WHAT/WHY, Application Design의 C1~C9 책임, Unit 경계 및 C5/S1/C3 계약은 유지한다. 별도 Inception 재시작, Unit 신설, P1 일반화, UI 확장은 하지 않는다.
- Functional Design 영향: C8의 작업 대상 전달과 C7 준비 단계 분리를 R2~R4에서 구체화한다. 신규 도메인 엔티티·저장 schema·매칭/검증 알고리즘은 없다. 승인 후 U0-P0의 business-logic-model.md에 이 보완을 반영한다. A 소유 S1 설계·코드는 수정하지 않는다.
- NFR 영향: 기존 Windows/Python, 오프라인 P0, 입력 검증, 실제 검증 카운트, 원격 실행 확인, PBT Partial을 유지한다. 합성 wheel 빌드의 setuptools/wheel 의존성 누락 여부를 깨끗한 환경에서 확인하고 해당 실행·개발 의존성에 명시한다. 새 NFR이나 기술 스택은 추가하지 않는다.
- 기존 run-p0 PASS와 Agent의 데모 명령 호출 증거는 유지한다. 이것을 일반 업무 요청 수용 PASS로 승격하지 않는다.

## R2. 테스트 준비와 제품 실행의 분리

### 준비 단계 — 테스트 운영자, Agent 업무 요청 이전

1. 제품 개발 저장소와 별도의 합성 작업 디렉터리를 만들고 `requirements.txt`에 `skillloop-demo-pkg==1.0.0`을 둔다.
2. 그 작업 디렉터리의 `.venv`를 만들고 대상 패키지가 미설치임을 확인한다. **이 venv가 사용자가 설치를 요청하는 작업 환경**이며 완료 후에도 남는다.
3. 기존 C7 `prepare()`로 모의 공급 경로 2개를 준비한다. 작업용 pip의 기본 경로는 패키지가 없는 모의 경로로 구성하며 외부 index/cache로 성공하지 않게 격리한다. 전역 pip 설정은 수정하지 않는다.
4. 기존 로컬 합성 Skill과 사용량 저장소를 별도로 준비한다. 초기 실제 사용량은 0이며 성공 이력을 미리 만들지 않는다. 관련 Skill과 무관한 Skill을 함께 둬 선택 근거도 확인한다. 해결 실행 중 `_seed_store()`를 호출하지 않는다.
5. 제품 CLI 및 C9 지침을 작업 프로젝트에서 사용할 수 있게 준비한다. 작업 환경의 Python 경로·일반 pip 설정은 제공할 수 있으나, 허용 index·정답 절차를 사용자 요청이나 추가 정답 지시로 알려주지 않는다. 제품 소스 분석으로 run-p0를 찾는 테스트로 대체하지 않는다.

### 업무 실행 단계 — 새 Claude Code 세션

사용자 입력은 다음 한 문장으로 시작한다.

> 이 프로젝트 requirements.txt의 패키지를 설치하고, 실제로 사용할 수 있는지 확인해줘.

Agent가 일반 설치를 직접 시도하거나 C9를 통해 아래 명령을 호출할 수 있다. 어떤 경우에도 실제 실패의 Python 환경과 복구·검증 대상이 같아야 한다. 원격 Skill의 명시적 실행 확인 등 기존 사용자 확인 절차는 유지한다.

## R3. 제안 CLI 계약과 실행 순서

```text
skillloop apply-requirements --requirements <path> --python <existing-venv-python>
                            --store <existing-store-json> --usage <usage-json>
                            [--run-id <execution-id>]
```

`--python`은 이미 존재하는 작업용 venv를 필수로 지정한다. 제품 CLI를 실행하는 Python과 설치 대상 Python은 달라도 되며, 대상은 반드시 출력한다. 전역 Python에 암묵적으로 설치하지 않는다. 이 명령에서 venv/index 생성·교체, 패키지 삭제로 실패 유도, 작업 venv 정리를 하지 않는다.

1. **입력·환경 확인:** requirements의 빈 줄·주석을 제외한 요청을 읽는다. 이번 지원 범위는 위 합성 패키지의 정확한 버전 1건이다. 다른 패키지/버전, 추가 항목, 옵션·URL 등 지원하지 않는 입력은 명시적인 `UNSUPPORTED_REQUIREMENTS`로 종료한다. 무시하거나 합성 대상으로 바꾸지 않으며, 검색하지 않은 입력을 NO_MATCH로 표시하지 않는다. venv/Python/pip 부재도 별도 준비 오류로 반환한다.
2. **실제 실패 관찰:** 지정 Python으로 요청 requirements의 실제 설치를 시도한다. 이미 구성된 기본 공급 경로를 사용하며 CLI가 실패 경로를 새로 선택하지 않는다. 명령·대상·실제 종료코드·오류를 관찰한다. 최초 설치가 성공하면 복구를 강제하지 않고 `reuse=+0`으로 구분한다. 이미 설치된 환경도 제거·재설치하여 실적을 만들지 않는다.
3. **검색:** 실제 패키지 공급 실패에 해당하는 관찰로 C5 `search`를 호출한다. pip 자체 오류·구문 오류를 무조건 패키지 공급 실패로 바꾸지 않는다. NO_MATCH/ERROR/TIMEOUT/NOT_INVOKED를 구분한다. MATCH의 id/version/전체 digest/근거/서술적 절차를 표시한다.
4. **적용 가능성·실행 확인:** 선택된 절차의 pip action·대상과 요청이 일치하는지 확인한다. 지원하지 않는 action을 pip로 보내지 않는다. C1의 digest 검증 계약을 재사용한다. 원격에서 받은 Skill은 기존 NFR-SEC-4 확인 없이는 실행하지 않는다. 기본 라이브 사례는 준비 단계에서 승인된 로컬 합성 Skill로 제한하며, 이를 원격 공유 검증이라고 보고하지 않는다.
5. **기존 S1 호출:** 지정 Python을 기존 C7 `EnvCtx`로 전달하여 `S1.apply_and_verify(selected, obs, env, run_id)`를 호출한다. 허용 경로는 선택된 descriptor.procedure를 기존 resolver로 해석한 값이다. S1의 clean·pip·버전·import 판정을 복제하거나 우회하지 않는다. 이번 합성 대상 범위에서는 A의 P1 확장을 기다릴 필요가 없다.
6. **기존 C3 기록:** 실제 S1 성공에만 exact Skill 참조와 검증 결과를 `build_evidence`/`record_actual_reuse`로 전달한다. 사용자 입력 boolean이나 로그 문자열로 성공을 만들지 않는다. run_id는 실행 시작에 1회 발급하여 출력하고, 동일 실행의 재시도는 전달받은 값을 유지한다. 이미 완료된 환경의 재호출은 새 재사용으로 집계하지 않는다.
7. **결과 보존:** 요청 requirements, 대상 Python 경로, 설치 결과와 카운트 증거를 보고한다. 작업 venv를 삭제하지 않는다. 별도 프로세스에서 같은 Python으로 설치 버전과 import를 다시 확인할 수 있어야 한다. 로컬 절대경로·전체 로그는 공유 Skill/usage 이벤트에 넣지 않는다. 검증 실패/미해결은 성공 종료와 구분하고, 후보 생성은 0건이다.

**중복 회피 결정(제안):** 기존 `run_p0` 본문은 이번에 리팩터링하지 않는다. 새 진입점은 동일 C5/S1/C3 계약을 직접 호출하는 작은 오케스트레이션으로 둔다. 기존 pip 경로의 회귀 위험과 A 병렬 변경과의 충돌을 줄이며, 매칭·검증·카운트 알고리즘은 중복 구현하지 않는다.

## R4. 변경 파일과 소유자

모든 아래 변경은 CJ 소유이며 **승인 후에만** 수행한다.

| 파일 | 변경 목적 |
|---|---|
| `skillloop/cli.py` | 지정 환경 기반 apply-requirements 연결, 인자/실패/결과 출력. 기존 명령 동작 보존 |
| `.claude/skills/skillloop/SKILL.md` | 일반 업무 요청·실패 관찰에서 제품 호출로 연결. 올바른 대상 Python/저장소 전달, 데모 대체 금지 |
| `tests/fixtures/work/requirements.txt` | 합성 업무 입력 1건 |
| `tests/prepare_p0_work.py` | 테스트 준비 도구. 별도 작업 프로젝트·venv·기존 Skill·격리 pip 설정 구성. 실제 해결/카운트는 하지 않음 |
| `tests/test_apply_requirements.py` | 동일 환경 설치·보존, 오류 경계, 무카운트, 재시도·새 작업환경 검증 |
| `pyproject.toml`, `requirements-dev.txt` | 실제 wheel 준비에 필요한 setuptools/wheel의 실행·개발 의존성 정합화. 테스트를 위해 몰래 추가 설치하지 않음 |
| `aidlc-docs/construction/U0-P0/functional-design/business-logic-model.md` | 승인된 준비/업무 실행 분리와 C8 호출 흐름 보완 |
| `aidlc-docs/construction/P0/nfr-requirements/tech-stack-decisions.md` | 기존 빌드 의존성의 필요 위치·환경 설명 보완 |
| `aidlc-docs/construction/U0-P0/code/p0-nl-acceptance.md` | 사용법, 실제 검증 기록, 제약과 미완료 항목 |
| `result/p0-nl/` | 실제 Agent 호출 기록·환경/버전·판정·실제 화면 증거. 비밀·원본 데이터 제외 |

`match.py`, `reuse_service.py` 및 A 테스트, B 코드·테스트는 수정하지 않는다. 이들의 계약 변경이 실제로 필요해지면 해당 변경만 조율한다. README/EVALUATION의 사용자 미커밋 편집은 이번 계획에서 제외하고 사용법은 위 별도 문서로 먼저 제공한다.

## R5. Part 2 순서 — 개정 2 승인 후 실행 완료

- [x] **S1. 승인 기록·설계 정합화:** 이 개정의 명시적 승인 원문을 audit에 기록하고 R4의 관련 FD/NFR 문단을 반영. A/B 경계·기준 SHA 확인.
- [x] **S2. 깨끗한 준비 환경:** 선언 의존성만 설치한 격리 환경에서 합성 wheel 준비와 기존 테스트의 실패 원인을 확인. 필요한 의존성 선언을 반영하고 준비 도구/fixture 작성. 설치·테스트·모델 네트워크 의존성을 서로 구분.
- [x] **S3. 지정 환경 CLI 구현:** R3 순서대로 기존 계약 호출. 실행 중 venv/index 준비·seed·삭제 금지. 대상 Python 불변과 실제 종료코드 기록.
- [x] **S4. C9 연결:** 일반 업무 요청이 해당 작업 환경을 대상으로 실행되도록 지침 수정. wrapper.py 키워드 매핑기는 만들지 않음.
- [x] **S5. 관련 테스트와 회귀:** 아래 검증표 수행. run-p0 기존 동작 및 PBT 회귀 유지. 실패 원인을 해결하기 위해 테스트 기대치를 낮추지 않음.
- [x] **S6. 새 Agent 수용 실행:** 개발 대화 이력이 없는 Claude Code에서 R2의 한 문장으로 실제 사용. 도구·권한·Skill 가용성 확인. 실행 trace와 독립적인 사후 확인을 기록.
- [x] **S7. 결과 문서·검토:** 실제 증거와 미완료를 구분해 코드/결과를 검토 요청. 사용자 코드 검토 게이트를 유지. 이 결과만으로 전체 P1/제품 Build and Test 완료를 선언하지 않음.

## R6. 검증 기준 및 확장 규칙

| 검증 | 판정 근거 |
|---|---|
| 요청 환경 실제 효과 | 실패·적용·버전·import 모두 지정 Python. 완료 후 별도 프로세스로 import 가능, venv 잔존 |
| 정답 대체 방지 | 실행 단계 prepare/make_clean_venv/setup_failing/seed 미호출, requirements 불변, 사용자 프롬프트에 정답 index 없음 |
| 입력과 오류 | 다른 패키지/버전·다중 요청은 지원 범위 밖으로 표시. 빈/손상 store, 실제 0후보, 잘못된 procedure, 적용 실패, Python/pip 미준비는 각각 실패/미실행 상태와 무카운트 |
| 실적 | 최초 실제 성공 +1, 동일 run_id 재처리·이미 설치된 환경 재호출 불변, 별도 새 작업 venv의 새 성공 +1. 이벤트 exact digest 일치, 후보/store content 무변경 |
| 모델 사용 | Skill 도구 및 필요한 설치·검증 명령을 허용하는 제한된 환경. 이전처럼 Skill 도구를 빼거나 Bash를 skillloop 명령만으로 제한하여 정상 설치를 막지 않음. 전체 권한 우회 금지 |
| 라이브 증거 | 자연어 요청, 제품 Skill 사용/CLI 호출 trace, pip 실패·선택 Skill·S1 검증·C3 기록, 사후 import와 카운트. 테스트 대역 PASS와 구분 |
| 회귀·재현 | 새 checkout/깨끗한 venv의 선언 의존성 기준으로 관련 테스트와 전체 회귀. SHA/Python/설치 명령/실패·skip 수를 함께 기록 |

- **PBT Partial:** PBT-02 기존 직렬화 round-trip 회귀 유지(새 직렬화 없음). PBT-03/07은 요구 입력의 주석·공백 변화가 대상을 바꾸지 않는 불변식과 지원 외 입력을 묵살하지 않는 성질에 Hypothesis generator 적용. PBT-08 실패 seed·축소 사례를 보존, PBT-09 기존 Hypothesis 유지. PBT-01/04/05/06/10은 기존 Partial 결정상 advisory이며 무조건 범위를 확대하지 않는다. 프로세스·Agent 흐름은 실제 실행 테스트로 검증한다.
- Security/Resiliency 전체 baseline은 기존 선택대로 Disabled. 승인된 NFR-SEC/NFR-RES는 계속 적용한다.
- 현재 검증 상태: 신규 관련 14 passed, 깨끗한 snapshot 전체 80 passed/0 skipped. 새 Claude Code 자연어 Cold 요청 수용 PASS, 이미 설치된 환경 재확인 +0. 최초 권한 제한과 후속 재시도는 result/p0-nl/에 보존했다. 원격/P1/전체 제품 완료는 아님.

## R7. 검토·승인 지점

이 개정 2 전체(관련 FD/NFR 보완 범위, 파일, S1~S7 순서, 검증 기준)를 **Approve**하면 Part 2에 착수한다. **Request Changes**이면 해당 부분을 수정하고 같은 게이트에서 재검토한다. 개정 2 승인: 사용자 **“어 진행해.”**, audit 참조. 현재는 구현 결과 검토 게이트다.

---

# 이전 초안 — a22e176 보존본 (미승인, 실행 금지)

- **상태**: **REVIEW REQUIRED — 승인 전 착수하지 않는다.** 이 문서는 검토 요청이며 포괄 승인이 아니다.
- **작성일**: 2026-09-08T10:28:56Z
- **목표(사용자 지정)**: 새 Claude Code 세션이 **업무 요청만** 받고 → 요청된 작업 환경의 **실제 실패** → Skill 검색·적용 → **설치·버전·import 검증** → **C3 실적 반영**까지 확인. **`run-p0` 자체완결 데모로 대체하지 않는다.**
- **대상 요청**: "이 프로젝트 requirements.txt의 패키지를 설치하고, 실제로 사용할 수 있는지 확인해줘."
- **범위 한정**: **승인된 합성 패키지·환경(FR-P0-2)** 안에서만 검증. **임의 패키지 전체 지원·P1 일반화(RU4)는 선행 조건으로 확대하지 않는다.**

## 1. 요구 대응 + 기존 코드로 가능한 것 / 추가 필요한 것 (단정 아님, 실제 계약 확인)

| AC(US-P0-1) | 요구 | 기존 코드 | 판정 |
|---|---|---|---|
| AC-1 `[FR-SURF-1,FR-P0-1/2]` | NL 요청→얇은 Skill→CLI 실제 설치 시도→**먼저 실패 재현** | run-p0는 **자체 제작 시나리오**(TARGET_PKG 하드코딩, requirements.txt 미참조). SKILL.md는 실제 업무 요청을 run-p0로 대체 금지 | **부분 — 추가 필요**: requirements.txt를 읽어 **요청 기반**으로 실패를 관찰하는 경로 없음 |
| AC-2 `[FR-MATCH-1~3]` | 결정적 검색+applicability+근거 | `skillloop match`가 `match.search` 노출(읽기전용) | **가능(기존)** |
| AC-3 `[FR-P0-3]` | 절차 적용→**실제 설치 성공**→검증(import/존재) | `reuse_service.apply_and_verify` 존재하나 **harness TARGET_VERSION/IMPORT·index 이름에 결합**(합성 대상 전용) | **가능(합성 범위 한정)** — 단, 요청 기반 오케스트레이션은 없음 |
| AC-5 `[FR-USAGE-1~3]` | 검증 성공 시에만 `actual_reuse+=1`, DEMO 구분 | `usage.record_actual_reuse`+`build_evidence`(C3) 존재. **카운트 경로는 run-p0(자체완결)뿐** | **부분 — 추가 필요**: 관찰 기반(비데모) 적용에서 카운트할 CLI 없음. 무검증 카운트 CLI는 **금지**(FR-USAGE-2) |

**확인된 실제 차이(가정 아님)**: (1) run-p0는 requirements.txt를 읽지 않고 대상을 하드코딩하며 데모로 호출된다. (2) `apply_and_verify`는 harness 합성 상수(TARGET_VERSION/TARGET_IMPORT)와 index 이름에 결합되어 **합성 패키지에서만** 검증이 성립한다 → 요청 기반 경로도 **합성 범위로 한정**된다. (3) 검증을 거치지 않고 카운트만 올리는 CLI는 추가하지 않는다(FR-USAGE-2).

## 2. 추가 구현 (최소 수정) — 요청 기반 수용 경로

**핵심 로직(매칭·적용·검증·카운트)은 재구현하지 않고 기존 계약을 호출만 한다.** 신규는 **오케스트레이션 + 합성 작업 픽스처**뿐.

**신규 명령**: `skillloop apply-requirements --requirements <path>` (합성 범위)
1. requirements.txt 읽기(합성 픽스처: `skillloop-demo-pkg==1.0.0`).
2. 합성 작업 환경 구성: `envharness_p0.prepare()`/`make_clean_venv()`/`setup_failing()` **호출**(FR-P0-2, 기존).
3. 실제 `pip install`(failing index)로 **실제 실패 관찰**(FR-P0-1, AC-1). 대상은 requirements.txt에서 도출.
4. `match.search(obs, store)` → MATCH+근거(AC-2, 기존 C5 호출).
5. `reuse_service.apply_and_verify(selected, obs, env, run_id)` → 적용+검증(AC-3, 기존 S1 호출).
6. `is_real_success`일 때만 `usage.record_actual_reuse(build_evidence(...))` → `actual_reuse+=1`(AC-5, 기존 C3 호출). run_id는 1회 발급·재시도 dedup 유지.

**중복 회피 방안(검토 포인트)**: run-p0가 이미 2~6의 기계적 흐름을 (하드코딩 대상으로) 수행한다.
- **(a) 권장** — `cli.py`에 행위 보존 헬퍼 `_reuse_loop(env, obs, store, usage, run_id)` 추출 후 `run_p0`와 신규 명령이 공유. **run_p0 동작 불변**(기존 run-p0 e2e 회귀로 보증). 
- (b) 대안 — 신규 명령이 동일 계약을 독립 호출(오케스트레이션 소량 중복, 로직 중복은 아님).
- 선택은 검토 시 확정. (a)는 승인된 P0 코드(cli.py, CJ 소유)를 **행위 보존 범위에서만** 수정.

## 3. 변경 파일·소유자

| 파일 | 변경 | 소유자 |
|---|---|---|
| `skillloop/cli.py` | `cmd_apply_requirements` + `apply-requirements` 서브파서 (+ 선택: `_reuse_loop` 추출) | CJ |
| `tests/fixtures/work/requirements.txt`(신규) | 합성 작업 픽스처(`skillloop-demo-pkg==1.0.0`) | CJ |
| `tests/test_apply_requirements.py`(신규) | e2e: 요청→실제 실패→match→적용→검증→카운트+1; 재시도 dedup; 미관련 req→NO_MATCH·무카운트 | CJ |
| `.claude/skills/skillloop/SKILL.md` | 대상 NL 요청을 `apply-requirements`로 연결(데모/업무 구분 유지) | CJ |

**설계 영향**: 신규 컴포넌트 없음. C5/S1/C3/C7 계약 **호출만**(로직 미복제). **A/B 파일 미수정.** NFR-SEC-4(원격 자동실행 없음·로컬 합성만)·FR-P0-2 합성 index 범위 유지. P1 일반화(RU4)는 범위 밖.

## 4. 검증 절차

- `python -m pytest tests/test_apply_requirements.py -q` + **전체 회귀**(기존 run-p0 e2e 포함 **PASS 보존** — 자연어 수용 검증과 구분).
- 실측 CLI: `skillloop apply-requirements --requirements tests/fixtures/work/requirements.txt` → 실패 관찰 → MATCH → 검증 성공 → `reuse=N` 증가; 재시도 시 dedup(무증가).
- **완료 기준(US-P0-1 자연어 수용)**: 새 Claude Code 세션에 **업무 요청만** 제공 → Agent가 SKILL.md 따라 `apply-requirements` 실행 → 실제 실패→검색→적용→검증→C3 실적. **run-p0 대체 아님.** = **사용자 확인 라이브 장면.**

## 5. 경계

- 승인 전 미착수. 검증 중 문제를 발견해도 **승인 범위를 넘어 코드 수정하지 않는다.** 기존 CLI PASS 보존, workflow 재시작·되돌림 없음. 공식 규칙·외부 Reference 미변경.

## P0 관찰 계약 결함 보완 — 사용자 수정 지시 반영

사용자가 피드백을 반영한 수정을 명시 요청했다. 기존 개정 2 R3의 실제 실패 정규화 연결을 수정·재검증하며 별도 제품 범위 변경은 없다.
- [x] D1. cli.py에 실제 exit/stderr/target을 받는 공통 pip 관찰 정규화 helper를 둔다. 패키지 이름·버전 분리, 이름 표기 정규화, 공급 실패의 대상 일치 확인. Skill id/정답 index를 선택하지 않는다.
- [x] D2. apply-requirements 및 기존 실패 관찰에 helper 재사용. match의 기존 canonical signature 입력은 보존하고 --pip-stderr/--exit-code로 실제 관찰을 입력할 수 있게 연결. raw 오류를 signature로 잘못 넣으면 올바른 관찰 입력을 안내하며 NO_MATCH로 위장하지 않는다. 명시 --store 사용, A 알고리즘 무변경.
- [x] D3. .claude/skills/skillloop/SKILL.md에서 정답 canonical 문자열 예시를 제거. 관찰/분류는 제품에 맡기고 사용자 안내는 한국어 업무 표현으로 정리. 기존 작업 프로젝트의 Skill 사본도 갱신.
- [x] D4. tests/test_cli_match.py의 오류/대상/종료코드/표기 변화 검증 및 기존 P0 회귀. tests/test_apply_requirements.py 기존 실행 경계 유지. 새 테스트는 단순 matcher 복제가 아닌 실제 관찰 연결을 확인.
- [x] D5. 새 작업 venv·새 Claude 세션에서 요청 한 문장만 입력해 실패→MATCH→실제 설치→독립 import→기존 실제 실적 1→2 확인. 이미 설치된 사용자 venv를 삭제하거나 초기화하지 않는다. 결과는 result/p0-observation/ 및 state/audit에 남긴다.

현재 위치는 CONSTRUCTION의 결함 수정·재검증이다. 완료 후 코드 결과 검토 게이트를 유지한다. P1/전체 Build and Test는 아직 미완료이며 이후 세션도 동일 workflow를 따른다.

검증 완료: 대상 검사 21 passed + P0 회귀 22 passed. 새 Claude 업무 요청 실제 실적 1→2 및 두 작업 venv import 확인. result/p0-observation/ 참조. 코드 결과 REVIEW REQUIRED 유지.
