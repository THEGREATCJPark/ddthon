export const STAGES = [
  {
    id: "plan",
    name: "아이템 기획",
    description: "어떤 문제를 해결할지, 시연에서 무엇을 보여줄지 정합니다.",
  },
  {
    id: "python",
    name: "Python 설치 시나리오",
    description: "P0 · 설치가 막히면 팀이 이미 해결한 방법을 찾아 적용합니다.",
  },
  {
    id: "excel",
    name: "Excel 설치 시나리오",
    description:
      "P1 · 처음 만난 문제를 해결하고, 다음에도 쓸 수 있는 방법으로 남깁니다.",
  },
  {
    id: "share",
    name: "팀에 해결법 공유",
    description: "한 사람이 알아낸 해결법을 다른 팀원에게 전달합니다.",
  },
  {
    id: "verify",
    name: "실제로 되는지 확인",
    description: "다른 환경에서도 같은 방법이 통하는지 확인합니다.",
  },
  {
    id: "demo",
    name: "시연 준비",
    description: "Python과 Excel 시나리오를 처음부터 끝까지 보여줍니다.",
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
  return `v2.${STAGES.map((s) => p[s.id]).join("")}`;
}
export function decodeProgress(value: string | null): Progress | null {
  if (!value || !/^v2\.[0-3]{6}$/.test(value)) return null;
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
