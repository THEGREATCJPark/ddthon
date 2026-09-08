import { mkdir, writeFile } from "node:fs/promises";
import { activeIssues } from "../src/domain.ts";
const repo = "THEGREATCJPark/ddthon";
async function getAll(path) {
  const items = [];
  for (let page = 1; page <= 100; page++) {
    const headers = {
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    };
    if (process.env.GH_TOKEN)
      headers.Authorization = `Bearer ${process.env.GH_TOKEN}`;
    const response = await fetch(
      `https://api.github.com/repos/${repo}${path}${path.includes("?") ? "&" : "?"}per_page=100&page=${page}`,
      { headers, signal: AbortSignal.timeout(20000) },
    );
    if (!response.ok)
      throw new Error(`Snapshot fetch failed: HTTP ${response.status}`);
    const data = await response.json();
    items.push(...data);
    if (!response.headers.get("link")?.includes('rel="next"')) return items;
  }
  throw new Error("Snapshot exceeds pagination limit; refusing partial data.");
}
const issues = activeIssues(
  await getAll("/issues?state=all&sort=updated&direction=desc"),
);
const comments = {};
for (const issue of issues) {
  if (issue.comments > 0)
    comments[issue.number] = (
      await getAll(`/issues/${issue.number}/comments`)
    ).map((c) => ({
      id: c.id,
      body: c.body,
      user: { login: c.user.login },
      created_at: c.created_at,
      html_url: c.html_url,
    }));
}
const sanitized = issues.map((i) => ({
  number: i.number,
  title: i.title,
  body: i.body,
  state: i.state,
  state_reason: i.state_reason,
  html_url: i.html_url,
  labels: i.labels.map((l) => ({ name: l.name })),
  assignees: i.assignees.map((a) => ({ login: a.login })),
  user: { login: i.user.login },
  created_at: i.created_at,
  updated_at: i.updated_at,
  comments: i.comments,
}));
await mkdir("public/data", { recursive: true });
await writeFile(
  "public/data/snapshot.json",
  JSON.stringify(
    {
      generatedAt: new Date().toISOString(),
      issues: sanitized,
      comments,
      source: "github-actions",
    },
    null,
    2,
  ) + "\n",
);
console.log(`Snapshot contains ${sanitized.length} shared issues.`);
