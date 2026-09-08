# User Stories — Agent SkillLoop (MVP)

**단계**: INCEPTION / User Stories — Part 2
**깊이**: minimal
**작성일**: 2026-09-08
**형식**: INVEST + Given/When/Then, 각 수용 기준에 **FR/NFR ID 태그**
**근거**: 승인된 `requirements.md`, 승인된 `story-generation-plan.md`(Q-A=A 5 stories, Q-C=A GWT+ID, Q-D=A 조건은 수용 기준에 흡수)

> **경계**: 스토리는 승인된 요구사항의 재표현·수용 기준화다. 요구사항 원문을 반복하지 않고 **FR ID로 참조**한다. Unit·역할·아키텍처·schema/API는 여기서 정하지 않는다. seam (a)~(f)는 후보로만 유지.
> **주체 규약**: "Agent"는 업무 수행 주체(검색·적용·설치·읽기·계산·후보화 실행), 사용자(PER-1)는 요청·환경 사실 확인, PER-2는 검토·게시 판단.

---

## US-P0-1 — 검증된 Team Skill 재사용으로 설치 성공 (P0)

**As** PER-1(사내 엔지니어) / 재사용 관점 PER-3,
**I want** `requirements.txt` 설치가 사내 제약으로 실패할 때 검증된 Team Skill이 자동으로 검색·적용되기를,
**so that** 처음부터 디버깅하지 않고 실제 설치를 성공시키고 재사용 실적을 남긴다.

**참조**: FR-SURF-1~3, FR-P0-1~4, FR-MATCH-1~3, FR-USAGE-1~3, NFR-SEC-4

**Acceptance Criteria**
- **AC-1** — GIVEN 공개 모의 index에 대상 패키지가 없고 허용된 사내 모의 index에만 무해한 wheel이 있는 상태에서, WHEN PER-1이 자연어로 설치를 요청하면, THEN Agent가 얇은 Skill→CLI로 실제 pip 설치를 시도해 **먼저 실패**를 재현한다. `[FR-SURF-1, FR-P0-1, FR-P0-2]`
- **AC-2** — GIVEN 설치 실패 상태에서, WHEN Agent가 결정적 키워드·태그 검색으로 후보를 만들고 **applicability를 확인**하면, THEN 현재 문제에 맞는 Skill만 선택되고 매칭 근거(키워드/조건)가 제시된다(무관한 Skill 오선택 방지). `[FR-MATCH-1, FR-MATCH-2, FR-MATCH-3]`
- **AC-3** — WHEN 선택된 Skill의 절차를 적용하면, THEN 허용된 index/옵션으로 **실제 설치가 성공**하고 결과가 검증된다(import/존재 확인 등 실제 효과). `[FR-P0-3]`
- **AC-4** — WHEN 원격에서 받은 Skill을 적용할 때, THEN 자동 실행하지 않고 서술적 절차를 명시적 확인 하에 수행한다. `[NFR-SEC-4]`
- **AC-5 (카운트)** — WHEN 검증된 적용이 실제 성공한 경우에만, THEN `actual_reuse += 1` 한다. 실패·단순 검색·retry는 집계하지 않으며, 시연용 `DEMO_SEED`는 실제 증가분과 **구분 표시**된다. `[FR-USAGE-1, FR-USAGE-2, FR-USAGE-3]`

---

## US-P1-1 — 직접 접근 실패 후 실제 검색과 NO_MATCH 판정 (P1)

**As** PER-1,
**I want** 보호 XLSX 직접 접근이 실패했을 때 Agent가 팀 자산을 **실제로 검색**한 뒤에만 "해결책 없음"으로 판정하기를,
**so that** 재사용 기회를 무단으로 건너뛰지 않는다.

**참조**: FR-P1-1, FR-P1-2, FR-MATCH-1~3, NFR-SEC-2

> **P1 실패 모델 확정(2026-09-08, CJ)**: "보호된 합성 XLSX"는 **Office 암호화 합성 파일**(open password로 저장 → 바이트가 OLE-CFB, OOXML zip 아님)로 구체화된다. 직접 parser 접근(openpyxl/pandas/zipfile)은 파일이 zip이 아니라 **자연 실패**(`BadZipFile`; 강제 raise·잘못된 API 아님, 평문 대조군은 동일 호출 성공 → 실패 원인=환경). 허용 대안(US-P1-2)은 **실행 중 Excel 인스턴스에 attach한 read-only 셀 읽기**. 사전조건: Excel 설치·실행 + 사용자가 파일을 열어둔 상태 + `pywin32`(NFR-RUN-1 P1 한정 예외). AC는 불변.

**Acceptance Criteria**
- **AC-1** — GIVEN 보호된 합성 XLSX(Office 암호화)에 대해, WHEN Agent가 직접 parser 접근을 시도하면, THEN **실제로 실패**한다(암호화로 zip 아님 → 자연 실패, DRM 우회·비허용 접근 없음). `[FR-P1-1, NFR-SEC-2]`
- **AC-2** — WHEN Agent가 Team Skill 및 제공 Org Knowledge를 검색하면, THEN **검색 범위·질의·결과가 기록**된다. `[FR-P1-2, FR-MATCH-1]`
- **AC-3** — GIVEN 검색이 실제 수행된 상태에서, WHEN 적용 가능한 Skill이 **하나도 없을 때만**, THEN `NO_MATCH`로 진행한다. `[FR-P1-2]`
- **AC-4** — WHEN 관련 Skill이 실제 존재하면, THEN 숨기거나 제거하지 않고 재사용 경로(US-P0-1)를 따른다. `[FR-P1-2, FR-MATCH-2]`
- **AC-5 (거절/미실행 구분)** — WHEN 검색이 미호출·오류·timeout이면, THEN 이는 `NO_MATCH`가 아니라 **별도 오류 상태**로 표시한다. `[FR-P1-2]`

---

## US-P1-2 — 허용된 대안 절차로 업무 완료 (P1)

**As** PER-1,
**I want** 환경 사실을 확인한 뒤 Agent가 허용된 read-only 대안 절차로 파일을 읽어 다음 달 예상 생산량 추세선을 산출하기를,
**so that** 직접 접근이 막혀도 업무를 완료한다.

**참조**: FR-P1-3, FR-P1-4, FR-P1-5, NFR-SEC-2

**Acceptance Criteria**
- **AC-1** — WHEN Agent가 대화형으로 환경 사실을 물으면, THEN PER-1의 입력을 받아 진행한다. `[FR-P1-3]`
- **AC-2** — GIVEN 정답 라이브러리를 고정하지 않은 상태에서, WHEN Agent가 Windows에서 **허용된 read-only 대안 절차**를 탐색하면(확정 모델: **실행 중 Excel 인스턴스 attach → 셀 read-only 읽기**, 암호 재입력·Save 없음, 원본 mtime/hash 무변경), THEN 파일 내용을 얻는다(비허용 접근 없음). `[FR-P1-4, NFR-SEC-2]`
- **AC-3 (업무 완료)** — WHEN 이전 3개 완료 월의 월별 총생산량으로 계산하면, THEN "다음 달"은 **마지막 완료 월+1**, 3점 단순 OLS(`x=1,2,3`→`x=4`), 음수는 **0 clamp**로 예상값을 산출한다. `[FR-P1-5]`
- **AC-4 (표시)** — THEN 결과에 **실제 3개월과 예상 1개월을 구분**하고 예측 대상 월·단위·예상값을 명확히 표시한다. `[FR-P1-5]`

---

## US-P1-3 — 환경 접근 절차만 새 Skill 후보로 (P1)

**As** PER-1,
**I want** 업무 계산법이 아니라 **환경 접근 절차만** 새 Skill 후보로 만들어지기를,
**so that** 업무 원문·계산 결과가 공유 자산에 새지 않는다.

**참조**: FR-P1-6, FR-SKILL-1~4, NFR-SEC-1, NFR-SEC-3, NFR-RES-1

**Acceptance Criteria**
- **AC-1** — WHEN 후보 descriptor를 만들면, THEN **환경 접근 절차만** 담고 예측 계산식·생산량 값·차트 로직·업무 원문·인증정보는 포함하지 않는다. `[FR-P1-6, FR-SKILL-3, NFR-SEC-1]`
- **AC-2** — THEN 후보는 단일 구조화 descriptor로 표현되며 **실행 스크립트 자체를 포함하지 않는다**(서술적 절차). `[FR-SKILL-1, FR-SKILL-2]`
- **AC-3 (무결성)** — WHEN 후보를 등록하면, THEN `digest`는 **불변 content identity에 대해서만** 계산되고 중복 등록은 dedup으로 방지된다. usage 변경은 digest를 바꾸지 않는다. `[FR-SKILL-4, NFR-RES-1, NFR-SEC-3]`

---

## US-P1-4 — 사람 검토·독립 Replay·게시 게이트 (P1)

**As** PER-2(팀 리뷰어),
**I want** 후보를 검토하고 독립 Replay가 통과한 **정확히 그 후보만** Git 공유 대상(이번 시연: `team-skill-store` branch)에 게시되기를,
**so that** 검증된 Skill만 팀 자산이 되고 다음 Agent가 안전하게 재사용한다.

**참조**: FR-P1-7, FR-SYNC-1~5, NFR-RES-2, NFR-RES-3, NFR-SEC-4

**Acceptance Criteria**
- **AC-1 (상태 구분)** — THEN 제안/검토/Replay/게시는 서로 **다른 상태로 명확히 구분**되어 표시된다. `[FR-P1-7]`
- **AC-2 (게시 게이트)** — WHEN 게시하려면, THEN 다음을 **모두** 충족해야 한다: 사람이 승인한 exact candidate의 content/version/digest == Replay에 사용한 candidate의 content/version/digest, 해당 exact candidate에 사람 승인 존재, 독립 Replay 실제 `PASS`. `[FR-P1-7]`
- **AC-3 (거절/보류/실패)** — WHEN Replay가 `FAIL`/`NOT_RUN`/미완료이거나 후보가 거절·보류이면, THEN **게시하지 않는다**. `[FR-P1-7]`
- **AC-4 (승인 무승계)** — WHEN 사람 승인 후 candidate의 내용/version/digest가 바뀌면, THEN 기존 승인을 승계하지 않고 **재검토·재Replay 대상**이 된다. `[FR-P1-7]`
- **AC-5 (원격 동기화)** — WHEN 게시가 확정되면, THEN **Git 공유 대상(이번 시연: 동일 저장소 `team-skill-store` branch)**에 clone/pull/push로 동기화되며, 별도 서버 없이 Git만으로 동작한다. 공유 대상에는 **descriptor + 비민감 재사용 이력만** 반영하고 **로컬 DB 파일 자체는 전달하지 않는다**. `[FR-SYNC-1, FR-SYNC-2, FR-SYNC-5]`
- **AC-6 (충돌·무결성)** — WHEN sync 시, THEN descriptor `digest`를 확인하고 **동일 `(id, version)`에 서로 다른 digest/content가 들어오는 경우만 CONFLICT**로 감지·표시하며 자동 overwrite/파괴적 병합을 금지한다(다른 version은 conflict 아님). sync 실패 시 로컬 상태를 손상시키지 않고 재시도 가능 상태를 남긴다. `[FR-SYNC-3, FR-SYNC-4, NFR-RES-2, NFR-RES-3]`
- **AC-7 (자동 실행 금지)** — THEN 게시·수신된 Skill은 자동 실행되지 않는다. `[NFR-SEC-4]`
- **AC-8 (게시 완료 표시 — 범위 변경)** — WHEN 원격 push가 성공 확인되면 THEN에만 **PUBLISHED(공유 완료)**로 표시한다. 게이트는 충족했으나 원격 전송이 실패하면 **로컬 확정(SHAREABLE) 상태를 보존**하고 재시도 근거를 남기며 PUBLISHED로 보고하지 않는다. 최초 게시와 실패 후 재시도 모두 가능하다. `[FR-P1-7, FR-SYNC-4]`

---

## US-UI-1 — 상태줄 조직 현황 (신규, 범위 변경)

**As** PER-1(사내 엔지니어) / 조직 관점 PER-3,
**I want** Claude Code 하단 상태줄에서 조직 Skill 수·내 기여·인기 Skill·재사용 현황을 간단히 보기를,
**so that** 작업 중에 팀 자산과 내 기여를 빠르게 인지한다.

**참조**: FR-UI-1, FR-UI-3, FR-USAGE-3/4, FR-ORG-1~5

**Acceptance Criteria**
- **AC-1** — WHEN 상태줄이 렌더되면, THEN 조직 Skill 수·내 기여·인기 Skill·재사용 현황을 간단히 표시한다. `[FR-UI-1]`
- **AC-2 (실적 구분)** — THEN 실제 검증 재사용 실적과 `DEMO_SEED`를 구분해 표시한다(합성 환경 실제 검증=실적, 사전 적재=DEMO_SEED). `[FR-UI-3, FR-USAGE-3, FR-USAGE-4]`
- **AC-3 (동일 기준)** — THEN 대시보드와 **동일한 집계 스냅샷**을 사용하며 마지막 동기화 기준·데이터 범위를 반영한다. `[FR-UI-3, FR-ORG-5]`

---

## US-UI-2 — 로컬 읽기전용 조직 대시보드 (신규, 범위 변경)

**As** PER-1 / PER-2 / PER-3,
**I want** 로컬 브라우저 읽기전용 대시보드에서 조직 요약·Skill 목록/검색/상세·기여 및 실제 재사용·검토/Replay/게시 상태·최근 활동을 보기를,
**so that** 팀 전체의 재사용·기여·게시 현황을 한눈에 확인한다.

**참조**: FR-UI-2, FR-UI-3, FR-ORG-1~5, FR-USAGE-3/4, NFR-SEC-1/2

**Acceptance Criteria**
- **AC-1** — WHEN 대시보드를 열면, THEN 조직 요약·Skill 목록/검색/상세·기여/재사용·검토/Replay/게시 상태·최근 활동을 표시한다. `[FR-UI-2]`
- **AC-2 (읽기전용)** — THEN 승인·게시·쓰기 등 상태 변경 액션을 제공하지 않으며 승인 대상만 read-only로 조회한다. `[FR-UI-2, NFR-SEC-2]`
- **AC-3 (조직 집계)** — THEN 공유 게시 Skill 수는 중복·버전을 구분(FR-ORG-1)하고, 팀원별 기여·재사용은 작성자(origin)·재사용자(alias) 기준(FR-ORG-2)으로, 다른 환경의 실제 재사용은 재동기화 시 중복 없이(FR-ORG-3, FR-USAGE-4) 집계한다. `[FR-ORG-1~3, FR-USAGE-4]`
- **AC-4 (상태 구분)** — THEN 로컬 후보/검토/게시대기와 원격 공유 완료(PUBLISHED=push 성공)를 구분해 표시한다. `[FR-ORG-4, FR-P1-7]`
- **AC-5 (동일 기준·범위)** — THEN 상태줄과 동일 집계 기준을 쓰고, 마지막 동기화 기준·조회 가능 데이터 범위와 실제 실적/`DEMO_SEED` 구분을 표시한다. `[FR-UI-3, FR-ORG-5, FR-USAGE-3]`
- **AC-6 (비민감)** — THEN 화면·공유 이력에 secret·원본 업무 데이터를 표시·포함하지 않는다. `[NFR-SEC-1]`

---

## 통합 위험 · 미완료 처리 (교차 참조 — 별도 스토리 아님)

- **NFR-INT-1**: 위 스토리 구현 시 공유 mutable state·공통 lifecycle 동시 수정을 최소화한다(소유 경계·계약 우선 고정은 Units Generation에서 확정).
- **RISK-1 / NFR-TEST-3**: P0 안정화 후 P1 게시까지 실제 수행이 목표다. 시간상 미완료 시 승인 없이 축소하지 않고 해당 흐름을 `PARTIAL`/`NOT_RUN`으로 정직하게 기록한다.

---

## 추적성 요약 (스토리 → FR/NFR)

| Story | Persona | 주요 FR/NFR |
|---|---|---|
| US-P0-1 | PER-1, PER-3 | FR-SURF-1~3, FR-P0-1~4, FR-MATCH-1~3, FR-USAGE-1~3, NFR-SEC-4 |
| US-P1-1 | PER-1 | FR-P1-1, FR-P1-2, FR-MATCH-1~3, NFR-SEC-2 |
| US-P1-2 | PER-1 | FR-P1-3, FR-P1-4, FR-P1-5, NFR-SEC-2 |
| US-P1-3 | PER-1 | FR-P1-6, FR-SKILL-1~4, NFR-SEC-1/3, NFR-RES-1 |
| US-P1-4 | PER-2 | FR-P1-7, FR-SYNC-1~5, NFR-RES-2/3, NFR-SEC-4 |
| US-UI-1 | PER-1, PER-3 | FR-UI-1/3, FR-USAGE-3/4, FR-ORG-1~5 |
| US-UI-2 | PER-1, PER-2, PER-3 | FR-UI-2/3, FR-ORG-1~5, FR-USAGE-3/4, NFR-SEC-1/2 |
