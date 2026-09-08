# U1 — Business Logic Model (Functional Design, minimal)

**단계**: CONSTRUCTION / Functional Design / U1 (P0 재사용 실행)
**작성일**: 2026-09-08
**소유**: A 최호길. **17:30 실제 샘플 실행 목표**의 핵심 경로.

---

## 1. 책임
설치 실패 관찰 → (C5) 결정적 검색·매칭·근거 → (S1) 절차 적용 → clean 환경에서 실제 설치 **검증** → 성공만 카운트. UI·게시·집계 없음.

## 2. C5 SkillSearchMatcher (계약 4 구현)
```
search(observation: FailureObservation, store) -> SearchOutcome
  candidates = [d for d in store.list() if satisfies(d.applicability, observation)]
  if not candidates: return NO_MATCH(reason="유효 후보 없음")
  ranked = stable_sort(candidates, key=(signal_fit desc, version desc, id asc))
  selected = ranked[0]                       # 결정적 동점 규칙
  return MATCH(ref=selected.ref, rationale=..., ranked_candidates=ranked)
# 내부 오류/시간초과/미호출은 ERROR/TIMEOUT/NOT_INVOKED로 반환
```
- 결정성: 동일 입력 → 동일 출력. `satisfies`·정렬·동점 규칙 모두 결정적.

## 3. S1 ReuseService (시나리오 비의존)
```
apply_and_verify(selected_descriptor, observation, env) -> ApplicationResult
  assert env.is_clean(observation.target_pkg)          # 오판 방지 전제(clean)
  run_id = new_execution_id()                          # 새 논리적 실행 = 새 run_id
                                                        # (재검증/재시도/재시작은 기존 run_id 재사용)
  cfg = selected_descriptor.procedure                   # 적용 설정은 절차에서 취득(정답 index 강제 아님)
  execute(cfg)                                          # 절차가 지정한 index/옵션으로 실제 pip install
  r = { pip_exit_code, installed_check, version_check, import_check(합성 시) }
  is_real_success = all(성공 조건 RU2)
  return ApplicationResult(..., index_source=cfg.index, is_real_success, run_id)
```
- 성공 시 상위(run-p0)가 **`C3.record_actual_reuse(evidence{run_id,...})`** 호출(카운트 쓰기 주체=C3). run_id는 **실행 단위** dedup.
- run_id의 구체 생성·보존 방식(예: 실행 시작 시 발급, 재시도 시 전달)은 Code Plan.

## 4. 데이터 흐름 (U0 run-p0 안에서의 U1 구간, 텍스트)
```
observation ── C5.search ──▶ SearchOutcome
                               ├ MATCH  ── S1.apply_and_verify ──▶ ApplicationResult
                               │                                    ├ is_real_success=true → (U0) 카운트 +1
                               │                                    └ false → 검증 실패(카운트 없음)
                               ├ NO_MATCH → 카운트 없음
                               └ ERROR/TIMEOUT/NOT_INVOKED → 상태 출력
```

## 5. 텍스트 대안
표·의사코드·순서 목록만 사용(다이어그램 없음, content-validation 준수).

## 6. U0에 요청하는 계약(P0 착수 전 확정 필요)
- 계약 1(digest·직렬화), 계약 3(record_actual_reuse·build_evidence·run_id dedup), 계약 4(SearchOutcome/Applicability), envharness_p0(setup_failing/allow/is_clean).
- 이 최소셋이 서면 U1은 U0 나머지 구현을 기다리지 않고 병렬 착수.

## 7. 남은 결정(Code Plan)
- `stable_run_id` 구성 요소, `signal_fit` 산식 상세, pip 실행 방식(subprocess/격리), 합성 패키지 정의.
