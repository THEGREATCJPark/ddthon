# P0 자연어 수용 검증 — 최소 수정 Code Plan (검토 요청, 착수 전)

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
