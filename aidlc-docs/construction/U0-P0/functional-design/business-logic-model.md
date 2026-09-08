# U0 P0 — Business Logic Model (Functional Design, minimal)

**단계**: CONSTRUCTION / Functional Design / U0 P0 필수
**작성일**: 2026-09-08
**목적**: P0 병렬 착수에 필요한 **최소 계약·규칙·데이터 흐름**을 기술 비의존으로 확정. (엔티티=domain-entities.md, 규칙=business-rules.md)

---

## 1. U0 P0 필수 책임
P0 임계 경로(US-P0-1)가 서기 위한 공통 토대: 직렬화·digest(C1), 로컬 저장·CONFLICT(C2), 카운트·증거(C3), 환경 재현(envharness_p0), 실행 진입점(cli.run-p0 골격). U1이 **호출 계약**으로만 사용.

## 2. 동결 계약 (P0 최소 = 1·3·4 + 로컬 저장·환경)

### 계약 1 — SkillDescriptor 직렬화 + digest
```
serialize(descriptor) -> json_bytes           # canonical
deserialize(json_bytes) -> descriptor
compute_digest(content_without_digest) -> sha256_hex
```
불변식: round-trip 동일, digest는 불변 content만 대상(R1).

### 계약 2 — SkillStore (로컬 JSON)
```
get(id, version) -> descriptor | None
list() -> [descriptor]
put(descriptor) -> {result: STORED | DEDUP | CONFLICT, reason?}
```
CONFLICT/DEDUP 판정 = R2. **C2는 카운트·usage를 쓰지 않는다**(DEDUP은 usage 병합·변경 없음). 카운트 쓰기는 계약 3(C3) 단독.

### 계약 3 — UsageTracker(카운트 + ReuseEvidence) — **재사용 기록의 유일한 쓰기 주체**
```
build_evidence(skill_ref, verification, run_id, demo_seed) -> ReuseEvidence
record_actual_reuse(evidence) -> {counted: bool, reason}
    # is_real_success & !demo_seed & (run_id가 새 논리적 실행) 일 때만 counted
    # 동일 run_id 재기록(재검증/재시도/재시작) → no-op
current_count(id, version) -> int
```
run_id는 **실행(execution) 단위** 식별(R3, E4). 같은 문제의 다른 환경 재사용은 다른 run_id → 각각 +1.

### 계약 4 — SearchOutcome/Applicability 반환 규격
E3(SearchOutcome), E2(Applicability). C5가 구현, U0는 규격만 소유.

### 환경 계약 — envharness_p0
```
prepare() -> None           # 실패 index + 허용 index 둘 다 준비(정답 강제 아님)
setup_failing() -> ctx      # 대상 패키지 없는 index
setup_allow() -> ctx        # 무해한 패키지 있는 index (적용 여부는 descriptor.procedure가 결정)
is_clean(target_pkg) -> bool  # 대상 패키지 미설치 확인(오판 방지)
```
> harness는 index를 **제공**할 뿐, 어느 index/옵션을 쓸지는 **선택된 descriptor.procedure**가 결정한다(정합화 3).

## 3. 데이터 흐름 — run-p0 (텍스트)
```
cli.run-p0
  → envharness_p0.prepare()            # 실패 index + 허용 index 둘 다 준비(정답 강제 아님)
  → envharness_p0.setup_failing() → (실제 pip install 시도 → 실패 관찰)
  → C5.search(실패 신호) → SearchOutcome
     ├ MATCH   → S1.apply(selected_descriptor)   # U1: 적용 설정은 선택된 descriptor.procedure에서 취득
     │           → 검증(clean 전제 + pip 종료코드 + 설치/버전 + 합성 import)
     │             ├ 성공 → C3.record_actual_reuse(evidence{run_id,...}) → "재사용 성공, reuse=N"
     │             └ 실패 → "적용했으나 검증 실패"(카운트 없음)
     ├ NO_MATCH → "적용 가능한 Skill 없음"(카운트 없음)
     └ ERROR/TIMEOUT/NOT_INVOKED → 해당 상태 출력(성공 위장 금지)

# 주의: MATCH가 곧바로 "정답 환경(allow index)"을 강제 선택하지 않는다.
# harness는 두 index를 제공만 하고, 실제 적용 설정(어느 index/옵션을 쓸지)은
# 검색·선택된 descriptor의 procedure가 결정한다. 검증 기준(실제 실패·설치·버전·import)은 유지.
```

## 4. 텍스트 대안(다이어그램 없음)
본 모델은 표·의사코드·순서 목록으로만 표현하며 Mermaid/ASCII 다이어그램을 포함하지 않는다(content-validation 준수).

## 5. 남은 결정(Code Plan으로 이월)
- JSON 파일 레이아웃·경로, 라이브러리 선택, CLI 인자 문자열, pip 호출 방식(subprocess 등), run_id 생성 방식의 구체 구현.

## P0 자연어 수용 개정 2 — 사용자 승인 반영

C7 준비는 업무 요청 전에 수행한다. C8 apply-requirements는 기존 작업 venv와 requirements를 받아 실제 pip 설치를 관찰하고 C5 → S1 → C3를 호출한다. venv 생성/교체, seed, 패키지 제거를 실행 경로에서 하지 않는다. 첫 설치 성공은 재사용 0, 실패 후 S1 검증 성공만 +1이다. 동일 실행 id는 유지하며 작업 환경은 보존한다. 지원 범위는 skillloop-demo-pkg==1.0.0 한 건이며 그 밖의 입력은 거절한다. 알려진 승인 로컬 합성 descriptor의 exact digest만 무인 수용 범위다. 기존 run-p0와 A 소유 계약은 유지한다.

## P0 관찰/검색 결함 정합화
C8의 실제 pip exit/stderr/요청 대상은 공통 관찰 변환을 거쳐 기존 FailureObservation으로 전달한다. 패키지 이름/버전 분리 및 이름 구분자 정규화는 Skill identity나 해결 경로 선택과 독립이다. 공급 실패에서 보고된 대상과 요청 대상이 일치할 때만 안정 신호를 생성한다. 성공·타 대상·기타 오류는 공급 실패로 변환하지 않는다. 외부에서 관찰을 전달하는 read-only match는 stderr 파일/종료코드/대상/실제 store를 명시한다. 기존 canonical signal 계약과 A matcher는 유지한다.
