# P0 재현 안내

지원 범위는 로컬 합성 skillloop-demo-pkg==1.0.0의 기존 해결 Skill 재사용이다. 임의 패키지/실제 사내 proxy 인증/원격 Skill 자동 실행은 지원 완료 범위가 아니다. 실제 pip 설치·import와 카운트는 실행 결과로 판단한다.

## 준비

Windows Python 3.10+ 및 Claude Code가 필요하다. 저장소 전체를 새 위치에 받는다. 최초 제품 의존성 설치는 패키지 공급원 접근이 필요하지만 합성 업무 실행은 외부 인터넷을 사용하지 않는다. 예시는 PowerShell이다.

```powershell
cd <받은-저장소>
.\scripts\prepare-p0.ps1 -Destination <새-작업폴더> -Python python
cd <새-작업폴더>
claude
```

준비 도구는 저장소의 .venv에 제품을 설치하고, 별도 작업 폴더에 작업 venv·합성 requirements·실패 공급원 설정·기존 Skill·실적 0·Claude 진입점/상태줄 연결을 만든다. 기존 작업 폴더는 덮어쓰지 않는다. Codex 설치나 이전 Codex 세션 폴더는 필요 없다. fixture를 사용하는 checkout 기반 시연이므로 제품 wheel만 복사한 단독 설치와 구분한다.

## 업무 요청

Claude에 “이 프로젝트 requirements.txt의 패키지를 설치해줘”만 입력한다. 필요한 실행 권한 확인에는 대상이 작업 Python/제품 Python인지 확인하고 허용한다. 오류·stderr나 정답 Skill 문자열은 사용자 요청에 넣지 않는다.

기대 결과: 기존 공급원 설치 실패 → 실제 관찰 정규화 → 기존 Skill MATCH → 같은 작업 venv 설치/버전/import PASS → 실제 재사용 0→1, 후보 +0. 같은 설치 완료 환경에서 재요청하면 추가 실적은 0이다.

제품 CLI로 같은 경로를 재현할 때는 작업 폴더의 skillloop-work.json에 있는 product_python/work_python/requirements/store/usage를 apply-requirements 인자로 전달한다. 실행 중 환경을 초기화하거나 run-p0로 대체하지 않는다.

## 한계

자동 실행 승인은 정확한 로컬 합성 descriptor에 묶여 있다. 다른 identity/내용에 승인을 자동 승계하지 않는다. 코드의 예제 결합을 일반화하려면 적용·검증·승인 계약을 함께 변경해야 하며, 검사를 삭제해 통과시키면 안 된다. 세 번의 재현 PASS는 동일 지원 범위의 재현성이지 다른 패키지 복구 능력의 증거가 아니다.
