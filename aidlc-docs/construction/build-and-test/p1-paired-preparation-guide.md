# P1 비교 측정 준비 및 적용 전 PC 인계

## 현재 범위

사용자의 2026-09-09 준비 승인에 따라 기존 CONSTRUCTION / Build & Test를 계속한다. 제품 요구사항, 게시 승인, 기존 시연 폴더, 웹은 변경하지 않았다. 새 비교 측정용 Code Plan은 `construction/plans/p1-paired-measurement-preparation-plan.md`다.

준비 폴더: `C:\Users\cik61\Desktop\P1-Paired-Preparation-20260909`.
이 폴더는 **운영자용**이다. `operator/`에 정답 자료와 출처가 있으므로 측정 Agent가 접근할 수 있는 계정/VM에 전체를 복사하지 않는다. 작업 폴더에는 회차의 XLSX 하나만 넣는다. task/boundary는 실행기에서 전달하고, Warm 조건에만 treatment의 정확한 UTF-8 원문을 주입한다.

현재 상태는 PREPARED_NOT_READY다. `doctor`는 실제 실행기/기록기 격리가 연결되지 않은 상태를 READY로 만들지 않는다. 완료 플래그만 바꾸거나 과거 SAFETY_STOP 실행기를 되살리지 않는다.

## 완료된 준비

- 원본 ZIP 79개 payload와 manifest, v2 입력 3개 및 task/boundary hash 확인.
- 새로운 study ID. 과거 v1/v2 로그와 조건은 그대로 보존하고 새 결과와 합산하지 않음.
- 측정 전 Excel read-only 열림이라는 공통 조건 보존. 도중에 사용자가 문서를 여는 제품 영상과 구분.
- 실제 제품 descriptor 및 원본 사람 검토/독립 Replay/게시 근거를 운영자 자료로 보존.
- standalone 절차 문서 작성. 원본 descriptor와 다른 파생 문서임을 표시하고 두 hash 기록.
- 별도 준비 데이터로 실제 Excel 암호화/BadZipFile/정확한 열린 workbook 접근/데이터 일치/원본 불변 검증. Agent 측정이나 파생 문서의 자동 로드 검증은 아님.
- 독립 행/일별 OLS 계산 검증 및 chart/safety 수동 검토 연결. 다른 설명된 예측법은 REVIEW_REQUIRED로 남기고 소급 OLS 강제하지 않음.
- 과거 실행기/reference 구현은 복사하거나 실행하지 않음. 원본 XLSX만 새 운영자 입력으로 추출.

## 적용 전 PC에 전달할 내용

기존 AI-DLC Build & Test를 유지하고, 이 준비 kit를 공통 기준 초안으로 검토하세요. Cold 모델 3회는 아직 실행하지 않습니다.

1. `protocol.json`, `readiness.json`, `receipts/required-evidence.json`을 확인하세요. 기존 v2 결과를 새 study 결과로 이관하지 마세요. main PC의 Python/라이브러리 차이는 `readiness.json`에 있으므로 양쪽 버전을 실제로 맞춘 뒤 동결해야 합니다.
2. 최우선은 격리입니다. 기록기와 원본 로그/정답 자료를 Agent 권한 밖에 두고, Agent와 Excel은 같은 대화형 Windows 세션에서 동작하게 하세요. 별도 PID나 prompt만으로 격리됐다고 하지 마세요. 다른 계정 또는 VM을 실제로 구성할 권한이 없다면 그 사실을 회신하세요.
3. **실모델 없이** 통제된 probe로 Agent 측의 기록기 종료 시도가 거부되고, 원본 로그 수정/정답 접근이 거부되며, Agent 종료 후에도 외부 수집 결과가 남는지 확인하세요. 프로세스 이름 전체 종료 명령을 쓰지 말고 disposable probe의 정확한 PID만 대상으로 합니다. SID/세션/ACL·probe 실행 근거를 남기세요. 확인 전에는 live recorder bridge를 승인하지 않습니다.
4. v2 원본 XLSX 3개를 양쪽에서 열 수 있는 운영자 키를 안전한 별도 채널로 준비하세요. DPAPI vault를 그대로 보내도 다른 계정에서는 사용할 수 없습니다. 키를 Agent 대화, 공유 Git, 결과 ZIP에 넣지 마세요. 키 전달이 불가하면 양쪽에 동일한 새 입력 세트를 생성하고 새 입력 hash로 동결합니다. 임의로 nowhere를 시도하지 않습니다.
5. 정확한 입력을 읽기 전용으로 열 수 있다는 사전점검 영수증을 양쪽에서 확보하세요. 이 작업은 setup이며 모델 측정 시간이 아닙니다. Excel 전체 종료/다른 문서 종료는 금지합니다.
6. `treatment/environment-procedure.md`는 제품 descriptor에서 유도된 새 텍스트입니다. `operator/derived-skill-provenance.json`과 `operator/derived-skill-mechanical-validation.json`을 함께 확인하세요. 원본 게시 승인이 이 문서까지 자동 승계됐다고 표시하지 마세요. 현재 모델 미호출 조건에서는 문서의 기계적 절차 검증까지만 완료했습니다.
7. 실제 보호된 recorder bridge, CLI의 Skill/MCP/이력 차단 및 Warm 원문 주입을 연결하고 **가짜 stdout을 내는 준비용 child**로 시간·중단·로그 수집을 확인하세요. 동일 실행기를 양쪽에서 사용하고 hash를 전달하세요. 기존 paused runner를 복사하여 사용하지 마세요.
8. 최종 회신: 실제 계정/세션·기록기 보호 증거, 입력 hash와 열람 증거, 실제 모델/CLI/Python/Excel/library 버전, 공통 runner hash, 파생 Skill hash. 패스워드/토큰은 제외하세요. main과 동결 후 사용자의 측정 시작 지시에 따라 Cold 3회/Warm 3회를 진행합니다.

## 운영자 명령

아래 명령은 모델을 호출하지 않는다. portable kit에서는 `python`을 실제 점검할 Python 실행파일로 바꿀 수 있다.

```powershell
python .\tools\p1_comparison.py doctor --root .
```

exit 2와 PREPARED_NOT_READY는 현재 정상적인 차단 결과다. 이를 PASS로 바꾸기 위한 플래그는 없다. live run 명령은 아직 제공하지 않는다.

## 업무 결과 검증

원본 transcript를 보존한 후, 운영자가 event ID를 인용해 제출 데이터와 예측법을 `submission.json`으로 추출한다. Agent에게 새 출력 schema를 강요해 기존 업무 prompt를 몰래 변경하지 않는다. 다른 예측법은 독립 검산 후 검증기를 확장하고 양쪽 공통 hash를 재동결한다.

`evidence.json`에는 외부에서 측정한 원본 before/after hash·mtime, transcript SHA, 안전 검토자/event ID, 차트 SHA와 실제/예측 series·기간·단위·라벨·계산법 검토를 기록한다. 자기 신고만으로 안전을 입증하지 않는다. 차트가 존재하거나 PNG가 유효하다는 이유만으로 의미 검토가 통과하지 않는다.

```powershell
python .\tools\p1_comparison.py verify-result --oracle .\operator\trial-1.json --submission .\review\submission.json --evidence .\review\evidence.json --chart .\runs\chart.png
```

샘플 schema는 `templates/`에 있다. 모든 미확인 값은 null/REVIEW_REQUIRED로 유지한다. final usage가 없으면 missing이다. wall time은 정상 종료·timeout·안전 중단·마지막 관측 하한을 분리한다. 이 비교는 WARM_SKILL_ONLY이며 full-product 검색/Registry/재사용 실적 증거가 아니다.

## 다음 실제 차단

이 PC는 Windows 11 Home, 비관리자 세션이다. 신규 계정/VM/다른 권한의 recorder는 이 작업에서 생성하지 않았다. 원본 입력 키는 ZIP에 없고, 설치된 Python은 3.14.0인 반면 과거 공통 조건은 3.13.14다. 이 세 가지를 해결하기 전에는 양쪽 설정 완료나 모델 측정 준비 완료로 보고하지 않는다.
