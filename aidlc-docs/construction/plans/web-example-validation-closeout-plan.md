# 예시 Skill 입력 검증의 PBT 보완 계획

상태: REVIEW REQUIRED, 구현 전. 마감 검토에서 발견한 테스트 공백을 다루며 새 사용자 기능은 추가하지 않는다.

## 발견과 근거

새 웹 예시 등록은 제목·내용·작성자 길이/공백 정규화 불변조건을 가지는 순수 함수 `team-hub/src/exampleSkillData.ts:validateExample`을 사용한다. 서버 권한·길이 예제 검사는 `scripts/rules.test.mjs`에 있으나, 이 함수의 생성 기반 불변조건 검사와 JS PBT 프레임워크는 현재 package.json/test scripts에 없다. 저장소의 기존 Partial 설정은 PBT-03/07/08/09를 적용하며, Python의 Hypothesis 실행만으로 JS 함수까지 준수했다고 선언할 수 없다.

이 발견은 현재 확인한 웹 변경 부분에 한정한다. 웹 제품의 사전 승인 증거를 발견했다는 뜻이 아니며 기존 Code Plan 누락과 별개로 다룬다.

## 최소 변경과 검증

1. `team-hub/package.json`과 lockfile에 테스트 전용 fast-check를 추가하고 기존 npm test에 새 테스트 파일을 포함한다. runtime 기능/배포 자격증명/Firestore 데이터는 변경하지 않는다.
2. `team-hub/src/exampleSkillData.test.ts`에서 생성된 유효 문자열의 정규화 후 길이·필수 값·멱등성, 빈/초과 입력 거부, 작성자 기본값을 검증한다. seed=20260909를 고정하고 shrinking은 기본 활성 상태로 둔다.
3. `npm test`와 `npm run build`를 실행한다. 서버 규칙 파일이 변경되지 않으므로 기존 exact rules CI 근거를 유지하며 라이브 Firestore 쓰기는 하지 않는다.
4. 실제 결과·변경 SHA를 closeout 검토에 연결한다. 과거 테스트를 소급 생성했다고 기록하지 않는다.

이 계획은 테스트 보완의 사전 계획이다. 사용자 승인 후 수행하며, 보완 전 해당 웹 PBT는 최종 준수 판정에서 미해결로 남긴다.
