import test from "node:test";
import assert from "node:assert/strict";
import {
  activeIssues,
  checklist,
  cleanTitle,
  codeOf,
  composeUrl,
  kindOf,
  safeGithubUrl,
  section,
  statusOf,
  type Issue,
} from "./domain.ts";
const issue = (patch: Partial<Issue> = {}): Issue => ({
  number: 1,
  title: "[TASK] 시험",
  body: "",
  state: "open",
  html_url: "https://github.com/THEGREATCJPark/ddthon/issues/1",
  labels: [],
  assignees: [],
  user: { login: "demo" },
  created_at: "2026-09-08T00:00:00Z",
  updated_at: "2026-09-08T00:00:00Z",
  comments: 0,
  ...patch,
});
test("only Hub issues count; normal issues, PRs and canceled work do not inflate progress", () => {
  const work = [
    issue(),
    issue({ title: "bug" }),
    issue({ pull_request: {} }),
    issue({ state: "closed", state_reason: "not_planned" }),
    issue({ state: "closed", state_reason: "completed" }),
  ];
  assert.equal(activeIssues(work).length, 2);
  assert.equal(
    activeIssues(work).filter((i) => statusOf(i) === "done").length,
    1,
  );
});
test("labels and title prefixes both classify shared content for non-maintainers", () => {
  assert.equal(kindOf(issue({ title: "[DISCUSSION] 아이디어" })), "discussion");
  assert.equal(
    kindOf(issue({ title: "목표", labels: [{ name: "hub:goal" }] })),
    "goal",
  );
  assert.equal(cleanTitle("[DIAGRAM] 흐름"), "흐름");
});
test("blocking wins over doing and closed completed wins over stale labels", () => {
  const labels = [{ name: "status:doing" }, { name: "status:blocked" }];
  assert.equal(statusOf(issue({ labels })), "blocked");
  assert.equal(
    statusOf(issue({ labels, state: "closed", state_reason: "completed" })),
    "done",
  );
});
test("section parser preserves multiline content and stops at next heading", () => {
  const body =
    "### 트랙\nP1\n\n### 내용\n첫 줄\n둘째 줄\n\n### 완료 기준\n- [ ] 미완료\n- [x] 완료";
  assert.equal(section(body, "트랙"), "P1");
  assert.equal(section(body, "내용"), "첫 줄\n둘째 줄");
  assert.deepEqual(checklist(body), { total: 2, done: 1 });
  assert.equal(section(body, "없음"), "");
});
test("Mermaid source extraction preserves newlines", () => {
  assert.equal(
    codeOf("설명\n```mermaid\nflowchart LR\n A --> B\n```"),
    "flowchart LR\n A --> B",
  );
  assert.equal(codeOf("없음"), "");
});
test("GitHub compose roundtrips Korean, Markdown and hostile query characters", () => {
  const body = "내용 & #?\n- [ ] 테스트";
  const url = new URL(composeUrl("task", "A & B?", body));
  assert.equal(url.searchParams.get("body"), body);
  assert.equal(url.searchParams.get("title"), "[TASK] A & B?");
  assert.equal(url.searchParams.get("labels"), "hub:task");
});
test("external and script links cannot replace trusted repository links", () => {
  const fallback = "https://github.com/THEGREATCJPark/ddthon";
  for (const bad of [
    "javascript:alert(1)",
    "https://github.com.evil.test/a",
    "https://github.com/another/repo/issues/1",
  ])
    assert.equal(safeGithubUrl(bad), fallback);
  assert.equal(safeGithubUrl(`${fallback}/issues/1`), `${fallback}/issues/1`);
});
import { stageOf, stageProgress } from "./stages.ts";
test("stage mapping uses explicit stage before track and never guesses an unknown stage", () => {
  assert.equal(
    stageOf(issue({ body: "### 트랙\nP0\n\n### 단계\ndesign" })),
    "design",
  );
  assert.equal(
    stageOf(issue({ body: "### 단계\nunknown\n\n### 트랙\nP0" })),
    null,
  );
  assert.equal(stageOf(issue({ body: "### 트랙\nP1" })), "p1");
  assert.equal(stageOf(issue()), null);
});
test("unregistered stage stays dark; finished subset does not light an entire stage as completed", () => {
  assert.equal(stageProgress([], "p0").status, "empty");
  const body = "### 단계\np0";
  const data = [
    issue({ body, state: "closed", state_reason: "completed" }),
    issue({ body }),
  ];
  assert.deepEqual(
    { ...stageProgress(data, "p0"), tasks: [] },
    { status: "todo", total: 2, done: 1, tasks: [] },
  );
});
test("active and blocked tasks illuminate their exact stage, canceled tasks are excluded", () => {
  const body = "### 단계\np1";
  const work = [issue({ body, labels: [{ name: "status:doing" }] })];
  assert.equal(stageProgress(work, "p1").status, "doing");
  assert.equal(stageProgress(work, "p0").status, "empty");
  work.push(issue({ body, labels: [{ name: "status:blocked" }] }));
  assert.equal(stageProgress(work, "p1").status, "blocked");
  work.push(issue({ body, state: "closed", state_reason: "not_planned" }));
  assert.equal(stageProgress(work, "p1").total, 2);
});
test("stage completion requires every mapped task completed, and reopened work removes green state", () => {
  const body = "### 단계\nqa";
  const data = [issue({ body, state: "closed", state_reason: "completed" })];
  assert.equal(stageProgress(data, "qa").status, "done");
  data[0].state = "open";
  assert.equal(stageProgress(data, "qa").status, "todo");
});
