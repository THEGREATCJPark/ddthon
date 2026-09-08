# CJ P1 인수 구현·검토 안내

A cb25a62의 reuse_service/담당 테스트, B 1760d32의 envharness_p1/replay/담당 테스트를 출처 그대로 인수한 뒤 CJ 인수 범위에서 보완했다. handoff-files.json은 원본 commit을 기록한다. GitHub PR merge/push 완료를 주장하지 않는다. B audit/state는 handoff 파일에 보존하고 메인 audit는 append-only로 유지했다.

## 구현

- C6: digest 불일치 접근 전 FAIL, fresh read 근거 재확인. 최초 artifact 인자 없음만으로 독립성을 단정하지 않고 새 리더 호출을 검사한다.
- C7-P1: DispatchEx 전용 인스턴스 생성, 소유 workbook만 닫기, 다른 workbook이 있으면 앱 Quit 안 함. 비-Office placeholder는 실제 암호화로 표기하지 않음. 미존재 파일의 None hash 동일성을 성공으로 인정하지 않음.
- S2: 실제 직접 접근 실패와 C5 검색, NO_MATCH의 Agent 탐색 경계, 명시적 발견 procedure 실행, 3점 OLS/실제3+예상1 결과, 환경 절차만 후보화. MATCH에는 exact 실행 확인 및 S1→로컬 artifact→업무 검증→C3 기록 연결. 업무 원문·artifact 경로는 공유 이벤트에 미포함.
- S3: 후보·사람 검토·새 Replay·SHAREABLE·게시 상태 단독 소유. 승인/Replay/현재 exact ref 일치, 실패·미실행·승인 후 변경 차단, push 실패 PUBLISH_PENDING 및 재시도. 원격 전송 근거와 수신 환경 로컬 검토를 구분.
- C4: 별도 등록된 team-skill-store 미러, 내용 hash 이름 JSON 전송, C2 import/CONFLICT, C3 shared usage exact ref/event dedup, 실제 원격 확인 후 메타 기록.
- CLI: run-p1/review/replay/publish/store-init/sync. S3 lifecycle이 존재하면 U3 조회에 연결하고 store-init의 로컬 sync 설정으로 메타를 조회한다. 읽기전용 조회는 Git 작업을 실행하지 않는다.

## 실행

프로젝트 .venv에서 pip install -e ".[p1]" -r requirements-dev.txt. P1은 Windows Excel 설치·실행과 사용자 열람 상태가 필요하다.

```text
python -m skillloop run-p1 --xlsx <업무파일> --store <로컬store> --usage <로컬usage> --app-open
```

NO_MATCH라면 NEEDS_AGENT_DISCOVERY로 반환한다. CLI가 정답을 자동 선택하지 않는다. Agent가 환경 사실을 확인하고 발견한 허용 read-only procedure JSON을 --procedure로 제공해야 다음 단계로 간다. 지원 schema는 action=file-access, method=excel-com-attach, 양의 sheet/month_col/total_col이다. 이미 매칭된 Skill은 사용자가 실행에 동의한 exact digest를 --confirm-skill로 제공한다.

업무 계산·후보 생성 후 사람은 후보 내용을 검토한다. 아래 review는 표시된 digest와 결정 문구를 실제 터미널에 입력해야 기록한다. Agent가 사용자를 대신해 자동 입력하지 않는다.

```text
python -m skillloop review --store <store> --id <id> --version <version> --decision approve --reviewer <사람별칭>
python -m skillloop replay --store <store> --id <id> --version <version> --xlsx <업무파일> --app-open
python -m skillloop store-init --store <store> --mirror <새미러폴더> --remote <허용원격>
python -m skillloop publish --store <store> --id <id> --version <version> --mirror <미러폴더> --remote <허용원격>
python -m skillloop sync --store <다른store> --usage <다른usage> --mirror <다른미러폴더> --remote <허용원격>
```

재사용 이벤트 공유는 sync --push-usage로 별도 처리한다. 게시 gate와 독립이며 새 Skill을 게시해야만 실적 공유가 가능한 구조가 아니다.

## 실제 검증과 미완료

P1 무결성/대역 계약 23건, S2/S3/C4 검사 7건을 실행해 통과했다. 후자는 실제 로컬 bare Git 게시·수신·이벤트 왕복을 포함하지만 Excel reader/사람 검토는 테스트 대역이다. GitHub 원격 게시 증거로 사용하지 않는다.

이 PC에서 실제 Excel 통합도 시도했으나 COM 호출이 반환하지 않아 FAIL_TIMEOUT으로 기록하고 생성한 테스트 인스턴스만 정리했다. 해당 실행을 NOT_RUN이나 PASS로 덮어쓰지 않는다. 후속 전체 자동 회귀에서는 실제 Excel 테스트를 명시 opt-in(SKILLLOOP_RUN_EXCEL_TESTS=1)으로 분리한다. 대역 테스트 통과를 실제 Excel 성공이라고 보고하지 않는다.

남은 작업: 실제 사용자 Excel attach/독립 Replay의 시간 초과 원인 해결, Claude의 P1 발견 과정·사람 검토·GitHub 공유·다른 환경 Warm의 종단 실행, 업무 차트 표시와 제출 증거, 전체 Build and Test 마무리. 현재는 코드 결과 REVIEW REQUIRED이며 P1 전체 완료가 아니다.

최종 통합 회귀: 130 passed/2 skipped/exit0. 이후 추가한 CLI 사람 확인·S3 조회2건을 포함한 서비스9 passed. skipped는 live Excel opt-in 및 B가 통합되어 해당하지 않는 A 미연결 전제 테스트다. 실Excel 실패 원본과 별도로 기록했다. result/p1-integration/validation.json 참조. PBT Partial의 기존 round-trip/digest/정규화 검사 유지, 추가 OLS 선형 불변식 검사 통과. 확정 NFR 외 새로운 baseline extension은 활성화하지 않았다.
