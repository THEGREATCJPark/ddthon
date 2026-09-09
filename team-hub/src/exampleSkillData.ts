export const fields = [
  {key: "title", label: "어떤 스킬인가요?", max: 100, placeholder: "예: 사내 S3 스토리지 연결 오류 해결"},
  {key: "author", label: "공유한 사람", max: 30, placeholder: "이름 또는 팀명"},
  {key: "problem", label: "겪었던 문제", max: 4000, placeholder: "어떤 작업에서, 무엇이 막혔나요?"},
  {key: "cause", label: "찾아낸 원인", max: 4000, placeholder: "처음 예상과 실제 원인이 어떻게 달랐나요?"},
  {key: "applicability", label: "증상 신호 · 적용 조건", max: 4000, placeholder: "같은 해결법을 적용할 수 있는 환경과 조건"},
  {key: "procedure", label: "해결 절차", max: 6000, placeholder: "팀원이 따라 할 수 있는 순서로 작성해 주세요."},
  {key: "verification", label: "성공 확인 방법", max: 4000, placeholder: "무엇을 확인하면 해결됐다고 볼 수 있나요?"},
] as const;
export const valueFields = [
  {key: "benefit", label: "조직에 주는 도움", max: 240, placeholder: "예: 장비 PC의 업로드 장애 대응 방법을 팀이 함께 사용"},
  {key: "effect", label: "기대효과", max: 240, placeholder: "예: 같은 오류의 원인을 다시 탐색하는 시간 감소"},
] as const;
export type SkillDraft = Record<(typeof fields)[number]["key"], string> & Partial<Record<(typeof valueFields)[number]["key"], string>> & {body?: string};
export type ExampleSkill = SkillDraft & {id: string; uid: string; createdAt: number};
export type FreeSkillDraft = {title: string; body: string; author: string};
export const emptyDraft: FreeSkillDraft = {title:"", body:"", author:""};
export function validateExample(input: FreeSkillDraft): FreeSkillDraft {
  const title = input.title.trim(), body = input.body.trim(), author = input.author.trim() || "팀원";
  if (!title || title.length > 100) throw new Error("제목을 입력해 주세요. (100자 이내)");
  if (!body || body.length > 60000) throw new Error("내용을 입력해 주세요. (60,000자 이내)");
  if (author.length > 30) throw new Error("이름은 30자 이내로 입력해 주세요.");
  return {title, body, author};
}
export const featured: SkillDraft = {
  title: "사내 S3 스토리지 연결 오류 해결",
  benefit: "장비 PC의 403 오류 대응 지식을 공유해, 담당자가 바뀌어도 원인 확인과 복구에 활용합니다.",
  effect: "권한·프록시를 반복 조사하는 시행착오를 줄이고, 같은 환경의 업로드 장애에 더 빠르게 대응할 수 있습니다.",
  author: "팀원 B · 실제 개발 경험 공유",
  problem: "장비 PC를 모니터링해 파일을 사내 S3 호환 스토리지(S3Drive)로 자동 업로드하는 프로그램에서, 특정 PC만 403 오류가 발생했습니다. access key·secret key·endpoint·bucket과 권한을 확인하고 프록시도 조사했지만 원인은 다른 곳에 있었습니다.",
  cause: "그 PC의 시계가 어긋나 요청 서명이 거부됐습니다. 이 사례의 오류는 RequestTimeTooSkewed였습니다. 403이라는 증상만 보고 권한 문제로 접근하면 시간 오차를 놓칠 수 있습니다.",
  applicability: "Skill: s3-compatible-storage-access · version 1.0.0\n적용 환경: 사내 S3 호환 스토리지 + boto3\n증상 신호: s3-access-fail:403 / s3-access-fail:connection / s3-access-fail:endpoint\n시간 보정은 서버 응답과 시각 차이로 시간 오차를 확인한 경우에 해당합니다.",
  procedure: "1. access_key, secret_key, bucket, endpoint를 확인합니다. target_key는 선택입니다. 자격증명은 코드에 직접 넣지 않고 환경에 맞는 설정·시크릿 관리 방식을 사용합니다.\n\n2. boto3 클라이언트 생성 시 사내 스토리지의 endpoint_url을 명시합니다.\n\n3. 연결 후에도 403이 지속되면 오류 응답과 서버·로컬 시각 차이를 확인합니다. 403만으로 시간 오차라고 단정하지 않습니다.\n\n4. 공유된 사례에서는 ntplib로 서버 시각을 받아 botocore의 서명 시각만 보정했습니다. 시스템 시계는 변경하지 않았습니다.",
  verification: "버킷 리스팅 성공 여부와 대상 key 조회 성공 여부를 확인합니다.\n이 페이지에는 경험 기반 후보를 소개합니다. 실행 코드나 독립 Replay 결과가 첨부된 검증 완료 Skill은 아닙니다.",
};

export const bigdataqueryExample: SkillDraft = {
  title: "자연어로 사내 DB 조회 · bigdataquery 활용",
  author: "팀원 공유 · 활용 사례",
  benefit: "코딩·SQL이 어려운 DS 직원이 필요한 데이터를 자연어로 요청하고, 사내 DB 조회에 필요한 환경 설정과 실행 절차를 함께 활용합니다.",
  effect: "SQL 작성과 Python 환경 준비의 진입 장벽을 낮추고, 반복되는 설치·조회 문제의 해결 경험을 다음 요청에 재사용할 수 있습니다.",
  problem: "대상: 코딩 및 SQL을 어려워하는 모든 DS 직원.\n사내 DB 접속용 Python 라이브러리 bigdataquery를 사용하는 데 어려움이 있고, 다양한 조건을 반영한 SQL 작성도 쉽지 않습니다.\n\n요청 예시: ‘제조 진행이력 테이블에서 XX075030 step의 최근 30일간 데이터 뽑아줘.’\n자연어 요청을 SQL query로 바꾼 뒤 bigdataquery를 통해 실제 데이터를 추출하는 활용 사례입니다.",
  cause: "SQL 작성뿐 아니라 시스템 환경 설치 오류, Python 버전·패키지 환경 불일치, 요청한 테이블·조건 컬럼의 존재 여부 확인까지 여러 단계에서 막힐 수 있습니다.",
  applicability: "사내 DB 조회에 bigdataquery를 사용하는 Python 환경.\n설치 오류와 해결 방법, 실행 가능한 환경 구성, 테이블·컬럼 확인 절차를 재사용할 환경 지식으로 축적합니다.",
  procedure: "1. 사용에 필요한 시스템 환경을 준비합니다. 설치 중 발생하는 오류 예시와 해결 방법을 확인합니다.\n\n2. 필요한 Python 버전과 현재 버전이 일치하는지, pip 업그레이드가 필요한지 확인합니다. 기존 환경에서 실행이 불가능하면 uv나 conda를 활용해 실행 가능한 가상환경을 구성합니다.\n\n3. bigdataquery를 import하고, 질문에 포함된 테이블과 조건 컬럼이 존재하는지 확인합니다. 없으면 LIKE 검색 등으로 유사 테이블을 찾아 요청 의도와 맞는지 확인합니다.\n\n4. 확인한 테이블·컬럼을 기준으로 자연어의 조건을 SQL에 반영하고, bigdataquery의 getData 함수로 실제 데이터를 추출합니다.",
  verification: "요청한 테이블·조건 컬럼을 사용했는지, XX075030 step과 최근 30일 조건이 조회에 반영됐는지 확인합니다.\n이 항목은 공유받은 활용 사례를 정리한 Skill 후보입니다. 이 웹에서 사내 DB 조회를 실행하거나 결과를 검증한 기록은 아닙니다.",
};

export const datalakeExample: SkillDraft = {
  title: "Datalake(Impala) 테이블 적재 전 파일 포맷 검사",
  author: "팀원 공유 · 실제 적재 경험",
  benefit: "사내 Datalake·Impala 적재 규칙을 공유해, 파일 구조와 컬럼명을 적재 전에 점검하고 원래 데이터 단위를 묶을 식별 컬럼을 준비합니다.",
  effect: "적재 거부 후 두세 번씩 재변환하는 시행착오를 줄이고, 웨이퍼·로트·측정 세션별 데이터 재구성 누락을 예방할 수 있습니다.",
  problem: "사내 Datalake에 테이블을 적재하고 Impala로 연계하는 작업에서, 파일 포맷이 맞지 않아 변환 작업을 두 번 세 번 반복했습니다. 데이터 자체는 문제가 없었고 적재 절차도 따랐지만, Datalake가 수용하는 파일 형태와 헤더 컬럼 규칙을 사전에 알지 못해 매번 거부된 뒤에야 무엇이 잘못됐는지 확인하는 과정을 거쳤습니다.",
  cause: "두 가지 제약을 사전에 인지하지 못했습니다.\n\n첫째, 헤더 컬럼 명명 규칙입니다. 이 사내 환경에서는 컬럼명에 언더바(_)를 제외한 특수문자를 사용할 수 없어 원본 컬럼명이 반복적으로 거부됐습니다.\n\n둘째, Datalake는 한 행이 하나의 데이터입니다. 웨이퍼 맵 같은 2차원 구조도 적재 시에는 행 단위로 평탄화됩니다. 같은 단위끼리 다시 묶으려면 wf_id 같은 공통 식별 컬럼이 모든 행에 있어야 합니다. 이 식별 정보 없이 적재하면 원래 단위로 되돌릴 수 없습니다.",
  applicability: "Skill: datalake-impala-ingest-format · version 1.0.0\n적용 환경: 사내 Datalake + Impala 연계 적재\n증상 신호: datalake-ingest-fail:schema / datalake-ingest-fail:column / datalake-ingest-fail:format\n\n적재 대상 파일을 사전에 검사해 규칙 위반을 미리 걸러내는 경우에 해당합니다.",
  procedure: "1. 파일 구조를 통일합니다. 첫 행은 헤더 컬럼, 그 아래부터 rawdata가 이어지는 단일 테이블 형태로 만듭니다.\n\nX    Y    Status\n0    0    Good\n0    1    Bad\n0    2    Good\n1    0    Good\n\n2. 헤더 컬럼명을 검사합니다. 언더바(_)를 제외한 특수문자 사용 여부를 확인하고 위반 컬럼은 규칙에 맞게 정규화합니다. 원본과 변환 후 컬럼명의 대응 관계를 남겨 이후 조회 시 참조할 수 있게 합니다.\n\n3. 행 그룹 식별 컬럼을 확인합니다. 같은 웨이퍼·로트·측정 세션에 속한 행들을 다시 묶을 수 있도록 wf_id 같은 공통 식별 값을 모든 행에 포함합니다. 원본에 없으면 적재 전에 추가합니다.\n\n4. 변환 결과를 적재 전에 검증합니다. 실패 후 재변환하는 대신, 적재 시도 전에 규칙 위반을 먼저 확인합니다.",
  verification: "변환된 파일이 규칙 검사를 통과하는지, 적재 후 Impala에서 테이블 조회가 정상 동작하는지, 식별 컬럼으로 원래 단위 재구성이 가능한지 확인합니다.\n\n이 페이지에는 경험 기반 후보를 소개합니다. 실행 코드나 독립 Replay 결과가 첨부된 검증 완료 Skill은 아닙니다.",
};
