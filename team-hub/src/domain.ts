export const REPO = "THEGREATCJPark/ddthon";
export const REPO_URL = `https://github.com/${REPO}`;
export type Kind = "task" | "goal" | "discussion" | "diagram";
export type Status = "todo" | "doing" | "blocked" | "done";
export interface Issue {
  number: number;
  title: string;
  body: string | null;
  state: string;
  state_reason?: string | null;
  html_url: string;
  labels: { name: string }[];
  assignees: { login: string }[];
  user: { login: string };
  created_at: string;
  updated_at: string;
  comments: number;
  pull_request?: unknown;
}
export interface Comment {
  id: number;
  body: string;
  user: { login: string };
  created_at: string;
  html_url: string;
}
export interface Snapshot {
  generatedAt: string | null;
  issues: Issue[];
  comments: Record<string, Comment[]>;
  source?: string;
}
export const KIND_NAMES: Record<Kind, string> = {
  task: "작업",
  goal: "목표",
  discussion: "의견",
  diagram: "다이어그램",
};
export const STATUS_NAMES: Record<Status, string> = {
  todo: "할 일",
  doing: "진행 중",
  blocked: "도움 필요",
  done: "완료",
};
export function kindOf(issue: Issue): Kind | null {
  if (issue.pull_request) return null;
  for (const kind of ["task", "goal", "discussion", "diagram"] as Kind[]) {
    if (
      issue.labels.some((l) => l.name === `hub:${kind}`) ||
      issue.title.toUpperCase().startsWith(`[${kind.toUpperCase()}]`)
    )
      return kind;
  }
  return null;
}
export function statusOf(issue: Issue): Status {
  if (issue.state === "closed")
    return issue.state_reason === "not_planned" ? "todo" : "done";
  if (issue.labels.some((l) => l.name === "status:blocked")) return "blocked";
  if (issue.labels.some((l) => l.name === "status:doing")) return "doing";
  return "todo";
}
export function activeIssues(issues: Issue[]) {
  return issues.filter(
    (i) =>
      kindOf(i) && !(i.state === "closed" && i.state_reason === "not_planned"),
  );
}
export function cleanTitle(title: string) {
  return title.replace(/^\[(TASK|GOAL|DISCUSSION|DIAGRAM)\]\s*/i, "");
}
export function section(body: string | null, heading: string) {
  const lines = (body || "").split("\n");
  const start = lines.findIndex((l) => l.trim() === `### ${heading}`);
  if (start < 0) return "";
  const end = lines.findIndex((l, i) => i > start && l.startsWith("### "));
  return lines
    .slice(start + 1, end < 0 ? undefined : end)
    .join("\n")
    .trim();
}
export function trackOf(issue: Issue) {
  return section(issue.body, "트랙") || "공통";
}
export function checklist(body: string | null) {
  const all = (body || "").match(/^\s*- \[[ xX]\]/gm) || [];
  return {
    total: all.length,
    done: all.filter((l) => /\[[xX]\]/.test(l)).length,
  };
}
export function codeOf(body: string | null) {
  return (body || "").match(/```mermaid\s*\n([\s\S]*?)```/i)?.[1]?.trim() || "";
}
export function safeGithubUrl(url: string) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" &&
      parsed.hostname === "github.com" &&
      parsed.pathname.startsWith(`/${REPO}/`)
      ? url
      : REPO_URL;
  } catch {
    return REPO_URL;
  }
}
export function composeUrl(kind: Kind, title: string, body: string) {
  const params = new URLSearchParams({
    title: `[${kind.toUpperCase()}] ${title.trim()}`,
    body,
    labels: `hub:${kind}`,
  });
  return `${REPO_URL}/issues/new?${params}`;
}
export function matches(issue: Issue, query: string) {
  return `${issue.title} ${issue.body || ""} ${issue.assignees.map((a) => a.login).join(" ")}`
    .toLowerCase()
    .includes(query.toLowerCase());
}
export function formatDate(value: string | null) {
  if (!value) return "아직 없음";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "날짜 미상";
  return new Intl.DateTimeFormat("ko-KR", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Seoul",
  }).format(d);
}
