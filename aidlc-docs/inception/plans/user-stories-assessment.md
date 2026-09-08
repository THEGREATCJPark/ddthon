# User Stories — 필요성 평가 (Step 1 Assessment)

**단계**: INCEPTION / User Stories — Part 1 (Planning)
**작성일**: 2026-09-08
**판정**: ✅ **EXECUTE (minimal depth)**
**근거 문서**: 승인된 `requirements.md`, `execution-plan.md`(Workflow Planning 승인), `aidlc-state.md`

> 이 문서는 User Stories 단계를 **실행할지 여부**와 **깊이**를 정한다. 상세 Unit·역할·아키텍처는 여기서 결정하지 않는다(Application Design / Units Generation).

---

## 1. 다요인 평가 (CLAUDE.md의 User Stories 조건부 기준 적용)

| 평가 요인 | 해당 여부 | 근거 |
|---|---|---|
| 신규 user-facing 기능/기능성 | ✅ 예 | Claude Code 자연어 요청 → 얇은 Agent Skill → CLI (FR-SURF-1~3). 데모·사용성 평가 대상. |
| 사용자 workflow/상호작용 변화 | ✅ 예 | P0 재사용 흐름, P1 환경 사실 확인(대화형, FR-P1-3)·검토·게시 loop. |
| 복수 user type / persona | ✅ 예 | Primary(코딩 경험 적은 사내 엔지니어) + 이해관계자(개발자/팀, 팀 리뷰어, 다음 Agent). |
| 복잡한 수용 기준 필요 | ✅ 예 | 게시 게이트(FR-P1-7 5개 조건), 카운트 규칙(§4.6), NO_MATCH 판정(FR-P1-2). |
| 교차 기능 팀 협업 | ✅ 예 | 4인 병렬 개발의 **공유 이해** 확보 필요. |
| 대외 API/서비스 변경 | ❌ 아니오 | 내부 CLI/컴포넌트 계약만. 대외 API 아님. |

**SKIP 조건 해당 여부**: 순수 내부 리팩터링/단순 버그픽스/문서 전용 변경 등 **SKIP 조건에는 해당하지 않음**.

---

## 2. 판정

**EXECUTE — minimal depth.**

- **왜 EXECUTE**: user-facing 흐름 + 복수 persona + 가치 있는 수용 기준(재사용 성공·검증, 게시 게이트, 카운트) + 4인 병렬의 공유 이해. 자동 생략은 부적절(사용자도 "자동으로 생략하지 말고 필요성을 판단" 요청).
- **왜 minimal**: 요구사항이 이미 FR/NFR ID로 상세히 확정됨. 스토리는 **requirements와 중복을 피하고 기존 FR ID를 참조**하며, 카운트·거절·미실행(NO_MATCH/NOT_RUN) 조건은 **관련 스토리의 수용 기준에 접어 넣어** 문서 팽창을 방지한다(사용자 요청).

---

## 3. 경계 (이 단계에서 하지 않는 것)

- Unit 개수·이름·사람별 할당·아키텍처·schema/API/class/branch ownership **미확정** (Application Design / Units Generation).
- seam (a)~(f)는 **후보로만** 유지. 스토리를 seam에 강제 매핑하지 않는다.
- 새 기능/NFR/clarification 추가 금지. 스토리는 승인된 요구사항의 **재표현·수용 기준화**에 한정.
- NFR-RES-2 등 동결된 문구 재수정 금지.

---

## 4. 다음 산출물

1. `story-generation-plan.md` — 스토리 생성 계획 + 최소 임베드 질문([Answer] 태그). **← 현재 작성, 승인 게이트.**
2. (계획 승인 후) `aidlc-docs/inception/user-stories/stories.md`, `personas.md` — INVEST 준수, 최소 분량.
