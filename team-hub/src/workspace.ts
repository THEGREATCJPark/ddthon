export const STAGES = [
  {
    id: "inception",
    name: "INCEPTION · 아이템 기획 · 공동",
    description:
      "요구사항 → Workflow → User Stories → Application Design → Units Generation",
  },
  {
    id: "u0",
    name: "U0 · 공통 계약·통합 기반 · 박찬준님",
    description: "Skill / Store / Usage / CLI / 공통 계약 동결",
  },
  {
    id: "u1",
    name: "U1 · P0 기존 Skill 재사용 실행 · 최호길님",
    description: "검색 → 적용 → 실제 검증 → reuse +1",
  },
  {
    id: "u2",
    name: "U2 · P1 새 경험 축적·게시 · 한석훈님",
    description: "탐색 → 후보화 → 검토 → Replay → Git 게시",
  },
  {
    id: "u3",
    name: "U3 · 조직 Skill 집계·표현 · 박찬준님",
    description: "상태줄 · 대시보드 · usage 공유",
  },
  {
    id: "build",
    name: "BUILD & TEST · 공동",
    description: "P0/P1 통합 · 실제 실행 · 종단 검증 · 증거 확보",
  },
  {
    id: "demo",
    name: "통합 시연",
    description: "Agent SkillLoop",
  },
  {
    id: "q1",
    name: "Q1 · 독립 QA / 사용성 / 실행 증거 · 윤여훈님",
    description:
      "윤여훈님이 전 Construction 과정에서 독립 QA, 사용성, 실행 증거를 확인합니다.",
  },
] as const;
export type StageId = (typeof STAGES)[number]["id"];
export const STATUS = ["대기", "진행 중", "막힘", "완료"] as const;
export type StageStatus = 0 | 1 | 2 | 3;
export type Progress = Record<StageId, StageStatus>;
export function emptyProgress(): Progress {
  return Object.fromEntries(STAGES.map((s) => [s.id, 0])) as Progress;
}
export function encodeProgress(p: Progress) {
  return `v4.${STAGES.map((s) => p[s.id]).join("")}`;
}
export function decodeProgress(value: string | null): Progress | null {
  if (!value || !/^v4\.[0-3]{8}$/.test(value)) return null;
  return Object.fromEntries(
    STAGES.map((s, i) => [s.id, Number(value[i + 3])]),
  ) as Progress;
}
export type Board = "team" | "challenge";
export type Message = {
  id: string;
  board: Board;
  body: string;
  name: string;
  parentId: string;
  createdAt: number;
  sample?: boolean;
  mine?: boolean;
};
export const SAMPLE: Message = {
  id: "sample-challenge",
  board: "challenge",
  name: "익명의 다른 팀",
  body: "이거 그냥 해결 방법을 문서에 적어두면 되는 거 아닌가요? Skill로 만들었을 때 뭐가 더 좋은지 데모에서 보여줘야 할 것 같아요.",
  parentId: "",
  createdAt: 0,
  sample: true,
};
export function messageInput(board: Board, body: string, name: string) {
  const cleaned = body.trim();
  if (!cleaned || cleaned.length > 1000)
    throw new Error("의견은 1~1,000자로 적어주세요.");
  const author = board === "challenge" ? "익명의 다른 팀" : name.trim();
  if (!author || author.length > 20)
    throw new Error("이름은 1~20자로 적어주세요.");
  return { body: cleaned, name: author };
}
