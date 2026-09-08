import {
  kindOf,
  section,
  statusOf,
  trackOf,
  type Issue,
  type Status,
} from "./domain.ts";
export const STAGES = [
  { id: "requirements", name: "요구사항", track: "공통" },
  { id: "design", name: "설계 · 통합 규약", track: "공통" },
  { id: "p0", name: "P0 재사용", track: "P0" },
  { id: "p1", name: "P1 경험 축적", track: "P1" },
  { id: "sharing", name: "팀 Skill 공유", track: "공유" },
  { id: "integration", name: "통합", track: "공통" },
  { id: "qa", name: "독립 검증", track: "QA" },
  { id: "submission", name: "시연 · 제출", track: "QA" },
] as const;
export type StageId = (typeof STAGES)[number]["id"];
export function stageOf(issue: Issue): StageId | null {
  const explicit =
    section(issue.body, "단계") ||
    issue.labels.find((l) => l.name.startsWith("stage:"))?.name.slice(6);
  if (explicit)
    return (
      STAGES.find((s) => s.id === explicit || s.name === explicit)?.id || null
    );
  const track = trackOf(issue);
  return track === "P0"
    ? "p0"
    : track === "P1"
      ? "p1"
      : track === "공유"
        ? "sharing"
        : track === "QA"
          ? "qa"
          : null;
}
export function stageProgress(
  issues: Issue[],
  stage: StageId,
): { status: Status | "empty"; total: number; done: number; tasks: Issue[] } {
  const tasks = issues.filter(
    (i) =>
      kindOf(i) === "task" &&
      stageOf(i) === stage &&
      !(i.state === "closed" && i.state_reason === "not_planned"),
  );
  const done = tasks.filter((i) => statusOf(i) === "done").length;
  const status = !tasks.length
    ? "empty"
    : tasks.some((i) => statusOf(i) === "blocked")
      ? "blocked"
      : done === tasks.length
        ? "done"
        : tasks.some((i) => statusOf(i) === "doing")
          ? "doing"
          : "todo";
  return { status, total: tasks.length, done, tasks };
}
