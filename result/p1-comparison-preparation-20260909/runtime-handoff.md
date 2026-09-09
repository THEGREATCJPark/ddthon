# P1 비교 준비 r2 — 런타임 정합 완료

메인 PC는 Python 3.13.14, Claude Code 2.1.266, openpyxl3.1.5 / msoffcrypto-tool5.4.2 / cryptography46.0.6 / pywin32311 / matplotlib3.10.8로 정합했습니다. 전체 전이 의존성은 runtime-lock.txt에 있습니다. 원래 제품 환경은 바꾸지 않았습니다.

별도 데이터 Excel 실검사 PASS, 준비검사20 PASS. 이것은 모델 측정이나 원본 입력 열람 성공이 아닙니다.

적용 전 PC에서 필요한 회신은 (1) 보호된 공통 기록기/Agent 격리 구성과 실제 점검 근거, (2) 원본 입력 키의 안전한 운영자 전달과 정확한 3파일 열람, (3) 이 lock 및 Excel/CLI 버전과 공통 protocol 확인입니다. 키/원본 로그는 Agent에게 주지 마세요.

기존 README.md의 첫 준비 시점 Python 불일치 기록은 역사로 보존했습니다. 현재 버전은 receipts/local-runtime-aligned.json이 우선합니다. r1 ZIP은 변경하지 않았습니다.

메인 PC 준비 점검 명령(모델 미호출):

```powershell
& '.\operator\runtime\Scripts\python.exe' .\tools\p1_comparison.py doctor --root .
```

다른 PC는 자체 Python3.13.14 venv에 runtime-lock.txt를 설치하고 그 Python으로 같은 doctor를 실행하세요. ZIP에 Python 실행환경 자체는 넣지 않았습니다. doctor는 원본 키/기록기/최종 양쪽 동결 전 PREPARED_NOT_READY(exit2)를 유지합니다.
