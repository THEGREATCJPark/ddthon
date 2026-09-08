# Services — Agent SkillLoop

**단계**: INCEPTION / Application Design — Part 2
**작성일**: 2026-09-08
**근거**: `components.md`, `component-methods.md`, `application-design-plan.md`(AD-Q3)

> 여기서 "서비스"는 **애플리케이션 내부 논리 서비스(오케스트레이션)** 이며 **네트워크 서비스·메시지 브로커가 아니다**(AD-Q5). CLI(C8)가 서비스를 호출하고, 서비스가 컴포넌트를 조율한다. 상세 규칙은 Functional Design.

---

## S1 — ReuseService (Skill 재사용 오케스트레이션 — **시나리오 비의존**)
**책임**: 현재 문제에 **맞는** 검증된 Skill을 적용하고 **그 Skill의 직접 효과**를 검증(US-P0-1). **P0 pip 설치는 하나의 특수 시나리오일 뿐**, S1은 문제 유형에 종속되지 않는다.

**핵심 계약(변경) — 시나리오 분기는 매칭된 Skill의 applicability로 결정**
```
apply_and_verify(match: Match, problem: ProblemContext) -> ReuseResult
  # match.applicability(문제 유형)에 따라 적용·검증 방식이 정해진다.
  #   - pip-install 유형(P0): 허용 index/옵션으로 실제 설치 + 설치 효과 검증(import/존재)
  #   - file-access 유형(P1 등): 허용 read-only 절차 적용 + "접근 효과" 검증(파일 내용 획득)
  # ReuseResult = {applied, verify: VerificationResult, applied_ref{id,ver,digest}}
  # ★ Excel/파일접근 Skill을 찾았을 때 pip 흐름으로 들어가지 않는다(문제 유형이 pip가 아니므로).

verify(problem, applied) -> VerificationResult   # S1이 수행 — "Skill 직접 효과" 검증
  # {ok: bool, kind: INSTALL_EFFECT|ACCESS_EFFECT|..., evidence, is_real_success}
  # 상세 검증 알고리즘은 Functional Design.
```

**P0 종단(특수 시나리오)**
```
run_p0(problem):
  1. env = EnvHarness.setup_pip_env()                 # 이중 mock index (C7)
  2. attempt_direct_install() -> 실패 관찰             # FR-P0-1
  3. outcome = SkillSearchMatcher.search(query)        # C5, 실제 검색·기록
  4. match = 첫 applicable 후보 (check_applicability)  # 근거 제시, 오선택/유형혼동 방지
  5. r = apply_and_verify(match, problem)              # pip-install 유형 → 설치+효과검증 (FR-P0-3)
  6. if r.verify.is_real_success:
        UsageTracker.record_actual_reuse(id, ver, r.verify.evidence)   # C3, +1 (실제 성공만)
  7. return ReuseReport{states, match_rationale, verify, usage}
```
**규칙 흡수**: 실제 성공만 카운트(FR-USAGE-1), retry/재검색 중복 집계 금지(FR-USAGE-2), DEMO_SEED 구분(FR-USAGE-3). 원격 Skill 자동 실행 금지(적용은 명시적, NFR-SEC-4).

---

## S2 — ExperienceService (P1 업무 완료 + 후보화 오케스트레이션)
**책임**: 새 문제를 해결(US-P1-1~3)하고 **환경 접근 절차만** 후보 descriptor로 만든다.

**핵심 계약(변경) — 업무 결과 검증은 S2 책임**
```
verify_work_result(result, facts) -> WorkVerification    # S2가 수행 — "P1 업무 결과" 검증
  # 기준월/외삽/표시가 FR-P1-5 기준을 충족했는지. S1의 Skill 효과검증(파일 접근 성공)과 구분.
  # {ok: bool, kind: WORK_RESULT, evidence(예: 사용된 3개월·기준월·예상값), }
  # 상세 알고리즘은 Functional Design.
```

**흐름**
```
run_p1(xlsx):
  1. obs = EnvHarness.attempt_direct_parse(xlsx)              # 실제 parser 실행 관찰 → 실패 관찰 (FR-P1-1)
  2. outcome = SkillSearchMatcher.search(query)               # 실제 검색·범위/질의/결과 기록
       - if outcome.status in {ERROR, TIMEOUT, NOT_INVOKED}: 별도 오류 상태 (≠ NO_MATCH)
       - if applicable 후보(파일접근 유형) 존재:
             r = S1.apply_and_verify(match, problem)          # ★ 파일접근 유형 재사용 (pip 흐름 아님)
             if r.verify.is_real_success:
                 UsageTracker.record_actual_reuse(...)         # 재사용 성공 카운트 (S1 경유)
             content = r.가져온 파일내용                        # 재사용으로 접근 성공
             reused = True
       - else NO_MATCH 로 진행 → 3~4 로 Agent 탐색
  3. facts = ask_environment_facts(user)                      # 대화형 (FR-P1-3) — Agent 관찰 시작
  4. (NO_MATCH 경우) Agent 가 허용 read-only 대안을 탐색·선택·코드작성·실행 (FR-P1-4)
       - EnvHarness 는 환경 사실만 제공, 정답 절차 공급 안 함
       - content = Agent 실행 결과로 획득한 파일 내용
  5. result = compute_ols_forecast(content); wv = verify_work_result(result, facts)  # 업무 완료+검증 (FR-P1-5)
       - 기준월=마지막 완료월+1, 3점 OLS(x=1..3→x=4), 음수 0 clamp, 실제3+예상1 구분 표시
  6. ★ 재사용/신규 발견 분기 (중복 후보 방지):
       - if reused and 새 절차 발견 없음:  candidate 생성하지 않음 (이미 게시된 절차 재사용)
       - if NO_MATCH 였고 새 환경 접근 절차를 발견함:  candidate = build_candidate_procedure(alt)
             - 환경 절차만, 계산식·생산량 값·차트 로직 제외 (FR-P1-6, NFR-SEC-1)
             - 기존 등록 절차와 dedup(digest) → 동일하면 새 후보 만들지 않음
  7. return WorkReport{reused, work_verification: wv}  (+ candidate 있으면 제안 상태로 S3 이관)
```
**책임 구분(명확화)**: **S1.verify() = 재사용한 Skill의 직접 효과 검증**(파일 접근 성공 여부), **S2.verify_work_result() = 요청한 P1 업무 결과 검증**(FR-P1-5 충족 여부). 재사용에 성공해도 **요청 업무 결과까지 완료·검증**한다.
**경계**: 업무 계산 결과·원본 데이터는 candidate/공유 자산에 포함하지 않는다(NFR-SEC-1). OLS 등 세부 계산은 Functional Design.

---

## S3 — PublishPipeline (검토·독립 Replay·게시 게이트) — AD-Q3
**책임**: 후보의 **상태 전이와 게시 결정을 한곳에서** 관리. CLI·sync가 이 게이트를 **우회할 수 없다**.

**상태(명확히 구분 — 로컬 확정 ≠ 원격 게시 완료)**:
`PROPOSED → UNDER_REVIEW → (APPROVED|REJECTED) → REPLAYED(PASS|FAIL|NOT_RUN) → (LOCALLY_APPROVED|BLOCKED) → (PUBLISHED | PUBLISH_PENDING)`
- **LOCALLY_APPROVED**: 게이트 충족 + 로컬 저장 완료. **아직 원격 게시 아님.**
- **PUBLISHED**: 원격 push 성공 확인까지 완료.
- **PUBLISH_PENDING**: 게이트는 충족했으나 원격 push 실패(재시도 필요). 로컬 상태·재시도 근거 보존.
- **BLOCKED**: 게이트 미충족(거절/FAIL/NOT_RUN/미완료).

**흐름**
```
review(candidate, decision):    # 사람 검토 (PER-2)
   record approval/rejection bound to EXACT candidate {id, version, digest}

replay(candidate):
   r = ReplayVerifier.replay(candidate, env)   # C6 독립 실행, 실제 결과

publish(candidate):
   # (1) 게이트 판정 (FR-P1-7)
   gate 모두 충족해야 진행:
     (a) approved_ref{id,ver,digest} == replayed_ref{id,ver,digest} == candidate 현재 ref
     (b) 해당 exact candidate 에 사람 승인 존재
     (c) ReplayResult.verdict == PASS
     (d) verdict in {FAIL, NOT_RUN} 또는 미완료 -> BLOCKED (게시 금지)
     (e) 승인 후 내용/version/digest 변경 시 -> 기존 승인 무승계, 재검토·재Replay 대상
   if not gate: state = BLOCKED; return

   # (2) 로컬 확정 (원격과 분리) — 여기서 "공유 가능(SHAREABLE)"이 확정됨
   SkillStore.save(candidate)                  # C2, 무결성/dedup. 성공 시 state = LOCALLY_APPROVED
       # LOCALLY_APPROVED = 게이트 충족(정확한 후보 사람 승인 + 독립 Replay PASS + digest 동일성) → SHAREABLE

   # (3) 원격 게시 시도 (별도 단계 — 순환 조건 없음)
   bundle = SkillStore.export_bundle(scope=SHAREABLE)          # ★ 게이트 충족 공유 대상(SHAREABLE) = descriptor 게시 자격
       # SHAREABLE 기준 = 사람 승인 + 독립 Replay PASS + digest 동일성. "원격 전송 완료 여부"와 무관.
       # → 최초 게시 대상도 SHAREABLE 이므로 export 됨(PUBLISHED 를 전제하지 않아 순환 없음). 실패 후 재시도도 가능.
   res = GitSyncAdapter.push_descriptors(bundle)   # 대상 = team-skill-store branch (범위 변경). 로컬 DB 미전송(FR-SYNC-5)
   if res.ok:   state = PUBLISHED                # 원격 push 성공 확인까지 완료
   else:        state = PUBLISH_PENDING          # ★ PUBLISHED 로 보고하지 않음
                # 로컬 LOCALLY_APPROVED(=SHAREABLE) 유지 + res.retryable/error 등 재시도 근거 보존 (NFR-RES-3)
```
> **★ Skill 게시 자격과 재사용 이벤트 공유 자격은 서로 다르다(범위 변경 정정)**: S3.publish 는 **descriptor 게시(SHAREABLE 게이트)** 만 다룬다. **재사용 이벤트 공유는 S3.publish 에 포함되지 않으며** 별도 sync 경로에서 처리한다(아래 §재사용 이벤트 공유). 그렇지 않으면 "새 Skill을 게시하지 않고 남의 Skill을 재사용만 한 환경"은 실적을 영영 공유할 수 없다.

### S3 상태 조회 계약 (읽기 전용 — C10 이 사용)
```
# S3 는 후보/검토/Replay/게시 상태의 유일 소유자·writer.
# 상태는 SkillStore 의 명시적 lifecycle-state 저장 계약으로 영속되며, 상태 전이 판단은 S3 만 수행.
query_lifecycle_state(candidate_ref{id,version,digest}) -> LifecycleState (읽기 전용)
list_lifecycle_states(filter) -> list[LifecycleState] (읽기 전용)
  # LifecycleState = {ref, state: PROPOSED|UNDER_REVIEW|APPROVED|REJECTED|REPLAYED(...)|
  #                          LOCALLY_APPROVED|PUBLISHED|PUBLISH_PENDING|BLOCKED,
  #                   local_review_evidence, remote_publish_evidence}
```
- **C10 은 이 읽기전용 계약으로만 상태를 조회**한다. 상태를 **추정하거나 게시 판단을 재구현하지 않는다.**
- **원격 게시본 구분**: import 로 받은 게시본은 `remote_publish_evidence`(원격 게시 근거)와 `local_review_evidence`(수신 환경의 검토 상태)를 **구분해 표시**하며, **수신 환경의 승인·Replay 기록을 만들어내지 않는다**(AD-Q4). 로컬 검토 상태가 없으면 "원격 게시(다른 환경 근거)"로만 표시한다.
**규칙 흡수(Q-D)**: 거절·보류·Replay FAIL/NOT_RUN/미완료 시 게시 금지. **원격 push 실패를 PUBLISHED 로 보고하지 않는다.** **export 대상은 "원격 전송 완료(PUBLISHED)"가 아니라 "게이트 충족 공유 대상(SHAREABLE)"로 판정**하므로 최초 게시가 배제되는 순환 조건이 없다. **원격에서 받은 상태 문자열만으로 검증 완료(로컬 승인·Replay 기록)를 만들어내지 않는다**(AD-Q4). import는 로컬 승인/Replay 상태를 원격 문자열로 대체하지 않는다.

---

## 재사용 이벤트 공유 (범위 변경 — Skill 게시와 독립된 sync 경로)
- **자격 구분**: **Skill 게시(SHAREABLE 게이트)** 와 **재사용 이벤트 공유(VERIFIED_REUSE)** 는 별개다. 재사용 이벤트는 (a) 정확한 Skill 참조 + (b) 실제 적용·검증 성공 근거 + (c) 비-DEMO 이면 공유 자격이 있으며, **그 Skill 의 로컬 승인·독립 Replay 를 요구하지 않는다.**
- **왕복 흐름(중복 없이 1회 반영)**: A가 승인·Replay로 Skill 게시 → B가 검증하여 import → **B가 실제 적용·검증 성공** → `sync --push`가 `UsageTracker.export_shared_usage(VERIFIED_REUSE)` → `GitSyncAdapter.push_shared_usage(...)`로 B의 이벤트 공유 → A가 `pull` → `UsageTracker.import_shared_usage`가 **정확한 Skill 참조·실제 성공 근거를 검증**하고 **event_id 기준 dedup**으로 **조직 실적에 한 번만** 반영(FR-USAGE-4). 이 경로는 **S3.publish 를 거치지 않는다**(새 Skill 게시 아님).
- **경로 소유**: 이벤트 export/import·검증·dedup=C3, 전송=C4(`push_shared_usage`/`pull`). CLI `sync`가 진입점이며 **게시 게이트를 우회하지 않는다**(descriptor 는 이미 SHAREABLE 인 것만 전송, 신규 게시는 S3.publish).

## 조직 집계·표현 (범위 변경 — 읽기전용 파생, 오케스트레이션 밖)
- **집계 read-model**: `OrgAggregator.build_snapshot()`가 C2(공유 게시)·C3(실제 재사용, 공유 import 포함)·C4.last_sync를 읽고, **후보/검토/Replay/게시 상태는 S3 의 읽기전용 계약(`list_lifecycle_states`/`query_lifecycle_state`)으로만 조회**한다(추정·게이트 재구현 금지). 단일 스냅샷 산출(FR-ORG-1~5, FR-UI-3). 게시 판단·usage 쓰기·저장·sync 없음. 원격 게시 근거(`remote_publish_evidence`)와 로컬 검토 상태(`local_review_evidence`)를 분리 표시(AD-Q4).
- **표현 표면**: `StatuslineRenderer`(FR-UI-1)와 `DashboardServer`(FR-UI-2, localhost 읽기전용)는 **동일 스냅샷**을 소비한다. 상태 변경 액션 없음(NFR-SEC-2). 실제 실적/`DEMO_SEED` 구분 유지(FR-USAGE-3).
- **소유 규칙**: usage 쓰기·검증·dedup=C3, 전송·last-sync=C4, 게시 상태 전이·상태 조회 계약=S3, 집계·표현=C10~C12(읽기전용). 서로의 소유 상태를 직접 수정하지 않는다(NFR-INT-1).

---

## 서비스 ↔ 컴포넌트 의존 요약
| 서비스 | 사용 컴포넌트 |
|---|---|
| S1 ReuseService | C7 EnvHarness, C5 Matcher, C2 SkillStore, C3 UsageTracker |
| S2 ExperienceService | C7 EnvHarness, C5 Matcher, C1 SkillDescriptor (+ 필요 시 S1) |
| S3 PublishPipeline | C6 ReplayVerifier, C2 SkillStore, C4 GitSyncAdapter.push_descriptors, C1 (+ 읽기전용 상태 조회 계약 제공: C10 이 사용) |
| 재사용 이벤트 공유(sync 경로, 게시와 독립) | C8 sync → C3 export/import_shared_usage(검증·dedup) + C4 push_shared_usage/pull |
| (집계·표현, 서비스 아님) | C10 OrgAggregator ← C2, C3, C4.last_sync, **S3 상태 조회(읽기전용)** → C11 상태줄 / C12 대시보드 (읽기전용) |

**호출 진입점**: C8 CLI → S1/S2/S3, 그리고 `sync` → C3/C4(재사용 이벤트 공유). C9 Wrapper → C8 CLI. (AD-Q6) 상태줄·대시보드는 C10 스냅샷 소비(읽기전용).
