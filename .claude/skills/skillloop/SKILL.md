---
name: skillloop
description: >-
  Agent SkillLoop 진입점. 사용자가 requirements.txt 패키지 설치·사용 확인을 요청하거나,
  Excel/XLSX 문서 읽기·생산량 분석·예측 추세선 작성을 요청하거나,
  (1) 설치·환경 실패를 겪어 "고쳐달라"고 하거나,
  (2) 명시적으로 P0 재사용 데모를 요청하거나, (3) 조직의 Skill 재사용 현황/상태줄/대시보드를
  보고 싶어 할 때 사용한다. 자연어 해석은 Claude가 하고, 검색·적용·검증·카운트 같은 제품 로직은
  기존 CLI(`python -m skillloop ...`)와 서비스에 그대로 둔다. 이 Skill은 얇은 진입점일 뿐
  제품 로직을 복제하지 않는다.
---

# SkillLoop — Agent 진입점 (C9)

원칙: **자연어 해석은 Claude가, 제품 로직(매칭·적용·검증·카운트)은 기존 CLI/서비스가.**
별도의 키워드 매핑 코드는 두지 않는다. 모든 동작은 사용자가 동일한 `python -m skillloop ...`
명령으로 **단독 재현**할 수 있어야 한다(FR-SURF-3).

## 요청 유형 구분 (중요)

### 1) 명시적 P0 재사용 데모
사용자가 "P0 데모", "run-p0", "재사용 데모 보여줘"처럼 **데모를 명시**한 경우에만:
```
python -m skillloop run-p0
```
- 이것은 **자체완결 데모**다(합성 실패를 스스로 만들어 적용·검증·카운트).
- 보고는 실제 출력의 `reuse=N (counted=..., reason=...)` 그대로. **"실제 업무에 적용했다"고 말하지 않는다.**

### 2) 실제 설치/업무 요청
작업 프로젝트에 `skillloop-work.json`이 있으면 먼저 읽어 제품 Python과 **작업 Python**,
requirements, store, usage 경로를 확인한다. 이 파일은 환경 연결 정보이며 해결 절차가 아니다.
requirements 파일을 실제로 읽고 아래 명령으로 **그 작업 환경**의 설치를 요청한다.

```text
<product_python> -m skillloop apply-requirements --requirements <requirements> --python <work_python> --store <store> --usage <usage>
```

- 일반 pip 설치를 먼저 시도해도 된다. 실패 후에는 위 명령으로 실제 관찰·C5 검색·S1 적용/검증·C3 기록을 이어간다.
- CLI는 기존 공급 경로로 실제 설치를 시도하며, 패키지 공급 실패를 관찰한 경우에만 검색한다.
- 현재 이 연결의 지원 범위는 합성 `skillloop-demo-pkg==1.0.0` 한 건이다. 범위 밖 입력은 거절하며 다른 패키지로 바꾸지 않는다.
- 작업 venv를 만들거나 교체·삭제하지 않는다. 답을 찾기 위해 제품 소스/fixture를 뒤지거나 허용 index를 직접 고르지 않는다.
- 완료 후 **같은 work_python**으로 별도 프로세스에서 import와 importlib.metadata.version을 확인한다.
- 실제 install exit, 선택된 Skill과 digest, 검증 결과, counted/reason을 근거로 보고한다.
  INSTALL_OK_NO_REUSE는 설치 성공일 뿐 Skill 재사용은 아니다. 동일 실행을 재시도하면 출력된 run_id를 전달한다.
- 자동 실행 범위는 정확히 승인된 로컬 합성 Skill뿐이다. CONFIRMATION_REQUIRED이면 멈추고 사용자 확인을 받는다.
- 이는 합성 환경에서 실제 업무 요청을 수용한 결과이며, 임의의 사내 패키지나 원격 공유까지 검증한 것으로 말하지 않는다.
- 연결 파일이 없거나 현재 지원 범위 밖이면 다음 일반 탐색/검색 원칙을 따른다. 임의 경로나 데모를 대입하지 않는다.

위 작업 연결 파일이 있는 지원 대상 요청에서는 **apply-requirements가 관찰·검색까지 수행하므로 별도의 match를 먼저 호출하지 않는다.** 앞의 흐름을 수행한 뒤 아래 일반 검색 절차를 다시 수행하지 않는다.

작업 연결 파일이 없는 일반 업무에서 별도 검색이 필요한 경우에만:
1. 실제 실패와 대상·환경을 확인한다.
2. pip 공급 실패는 실제 stderr를 UTF-8 파일로 보존하고, 실제 종료코드와 요청 대상을 제품에 전달한다.
   match --pip-stderr <실제-stderr-파일> --exit-code <실제-종료코드> --target <요청-패키지> --store <작업-store>
   정규화·분류는 제품이 수행한다. Agent가 오류를 canonical 문자열로 조립하거나 정답 Skill 이름을 지정하지 않는다.
3. stderr/종료코드를 만들어내지 않는다. 원문 오류를 --signature에 넣지 않는다. 기본 데모 store를 다른 작업의 store라고 가정하지 않는다.
4. 검색만으로 적용·검증·카운트 성공을 주장하지 않는다. 지원 범위 밖의 복구는 미구현으로 구분한다.

### 3) 조직 현황 / 상태
```
python -m skillloop status       # 네 줄 요약(하단 상태줄과 동일 소스)
python -m skillloop dashboard    # http://127.0.0.1:8765/ 로컬 읽기전용 대시보드
```
- 게시(PUBLISHED)는 lifecycle 조회(계약7)가 연결됐을 때만. 미연결이면 "확인 불가/상태 조회 미연결"로
  표시하며 0건·특정 상태로 **추정하지 않는다**. 실제 재사용과 DEMO_SEED를 구분해 읽는다.

### 4) XLSX 환경 제약과 새 경험(P1)

- 사용자 작업 파일·허용된 접근 범위·실행 중인 애플리케이션 등의 환경 사실을 확인한다. 원본 암호를 요구하거나 후보에 포함하지 않는다.
- `run-p1 --xlsx <작업파일> --store <store> --usage <usage>`가 실제 직접 접근과 검색을 수행한다. 애플리케이션이 열려 있음을 확인한 경우에만 `--app-open`을 전달한다.
- `NEEDS_AGENT_DISCOVERY`이면 환경 사실을 근거로 허용 read-only 대안을 탐색한다. 성공을 연출하거나 harness에서 정답 절차를 가져오지 않는다. 발견한 절차를 명시적 procedure JSON으로 전달할 때만 `--procedure <파일>`로 재실행한다. 현재 실행 어댑터는 승인된 P1 Excel 시나리오 범위이며 다른 방법을 지원한다고 주장하지 않는다.
- MATCH 후 `CONFIRMATION_REQUIRED`는 exact Skill의 실행에 대한 사용자 확인이 필요하다는 뜻이다. 동의받은 digest만 `--confirm-skill`로 전달한다. 그 결과로 실제 업무 계산까지 검증해야 한다.
- 후보 생성은 게시가 아니다. 사람이 내용을 검토하는 review CLI의 확인 입력을 Agent가 대신 자동 입력하지 않는다. 명시적 사람 검토 이후 replay, publish 순으로 진행하며 FAIL/NOT_RUN/미완료를 성공으로 바꾸지 않는다.
- P1 전체 자연어 탐색·사람 승인·원격 게시가 실제로 실행되지 않았다면 해당 장면은 NOT_RUN으로 보고한다.

## 안전·게이트 (항상 유지)
- **원격 Skill 자동 실행 금지**(NFR-SEC-4): 원격/타 환경에서 온 Skill은 **명시적 사용자 확인 후에만** 실행.
- **게시 게이트 유지**: 검증 없이 SHAREABLE/PUBLISHED로 승격하지 않는다.
- **비밀·원본 업무 데이터**를 Skill/출력에 포함하지 않는다(합성만, NFR-SEC-1).

## 사용자 안내 방식
- 사용자에게는 한국어로 현재 작업과 관찰 결과를 짧게 설명한다.
- “actual install request”, “supported scope”, “harness” 같은 내부 분류를 진행 멘트로 반복하지 않는다.
- 예: “현재 프로젝트의 Python 환경과 requirements.txt를 확인했습니다. 기존 설정으로 설치해 보겠습니다.”
- 실패 후에는 관찰된 원인과 기존 해결 경험을 확인한다는 목적을 설명한다. 실행하지 않은 검색·적용을 했다고 말하지 않는다.
- 합성 범위·미구현·권한 거부 등 결과 해석에 필요한 한계는 숨기지 않는다. 성공 결과만 간결히 정리한다.


## P1 현재 업무와 공유 환경 절차의 분리 (승인 정정)
- workspace `.skillloop/context.json`이 있으면 제공된 환경 설명으로 참고한다. 표시는 `사내환경 · NASCA(가상)`이다. metadata는 실제 관찰/원인 진단/실행 승인이 아니다.
- 실제 직접 읽기 실패를 확인한 뒤 환경 설명과 함께 짧게 안내한다. 특정 보안 제품이 실패 원인이라고 단정하지 않는다.
- 해결 방법은 환경 metadata에서 제공하지 않는다. NO_MATCH 뒤 실제 환경을 조사하고 대안을 발견한다. 허용 실행 방법은 CLI --help와 실제 오류로 확인한다.
- 접근 결과 `NEEDS_TASK_MAPPING`은 로컬 artifact의 문서 값/시트/UsedRange를 읽고 현재 업무의 월/생산량 열과 시작 행을 판단하라는 뜻이다. 로컬 task-mapping JSON을 `--task-mapping`으로 전달한다. 이 정보를 shared procedure에 넣지 않는다.
- 업무가 완료되면 chart_ref의 실제3+예상1 PNG를 사용자에게 보여준다. 공유 후보에는 업무 값·열·시트·차트·암호를 넣지 않는다.
