export const STAGES = [
  {
    id: "inception",
    name: "INCEPTION · 아이템 기획",
    description:
      "AI-DLC의 시작 단계입니다. 해결할 문제, 사용자, 성공 기준과 시연 범위를 함께 정합니다.",
  },
  {
    id: "u1",
    name: "U1 · Python 설치",
    description:
      "CONSTRUCTION 병렬 작업 · 설치가 막히면 팀이 이미 해결한 방법을 찾아 적용합니다.",
  },
  {
    id: "u2",
    name: "U2 · Excel 분석",
    description:
      "CONSTRUCTION 병렬 작업 · 합성 제약 환경의 Excel을 분석하고 새 해결법을 남깁니다.",
  },
  {
    id: "u3",
    name: "U3 · 협업 Web",
    description:
      "CONSTRUCTION 병렬 작업 · 진행 순서도, 의견, 딴지와 시연 화면을 하나의 Web으로 연결합니다.",
  },
  {
    id: "evaluation",
    name: "평가 담당 · 팀원 1명",
    description:
      "구현과 분리된 팀원 한 명이 U1·U2·U3 결과와 시연 흐름을 확인하고 피드백합니다.",
  },
  {
    id: "demo",
    name: "통합 시연",
    description:
      "평가를 통과한 U1·U2·U3를 연결해 Agent SkillLoop의 전체 흐름을 보여줍니다.",
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
  return `v3.${STAGES.map((s) => p[s.id]).join("")}`;
}
export function decodeProgress(value: string | null): Progress | null {
  if (!value || !/^v3\.[0-3]{6}$/.test(value)) return null;
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
