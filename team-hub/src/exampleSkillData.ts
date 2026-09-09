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
