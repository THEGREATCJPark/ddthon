import { REPO, type Issue, type Comment, type Snapshot } from "./domain";
const API = `https://api.github.com/repos/${REPO}`;
export async function fetchPages<T>(
  path: string,
  signal?: AbortSignal,
): Promise<T[]> {
  const items: T[] = [];
  for (let page = 1; page <= 30; page++) {
    const response = await fetch(
      `${API}${path}${path.includes("?") ? "&" : "?"}per_page=100&page=${page}`,
      {
        headers: { Accept: "application/vnd.github+json" },
        signal: signal
          ? AbortSignal.any([signal, AbortSignal.timeout(15000)])
          : AbortSignal.timeout(15000),
      },
    );
    if (!response.ok)
      throw new Error(
        response.status === 403 || response.status === 429
          ? "GitHub 조회 한도에 도달했습니다."
          : `GitHub 연결 오류 (${response.status})`,
      );
    const data: T[] = await response.json();
    items.push(...data);
    if (!response.headers.get("link")?.includes('rel="next"')) return items;
  }
  throw new Error(
    "데이터가 조회 범위를 초과했습니다. GitHub 원본을 확인해 주세요.",
  );
}
export const fetchIssues = () =>
  fetchPages<Issue>("/issues?state=all&sort=updated&direction=desc");
export const fetchComments = (number: number, signal?: AbortSignal) =>
  fetchPages<Comment>(`/issues/${number}/comments`, signal);
export async function fetchSnapshot(): Promise<Snapshot> {
  const response = await fetch(
    `${import.meta.env.BASE_URL}data/snapshot.json`,
    { cache: "no-cache", signal: AbortSignal.timeout(10000) },
  );
  if (!response.ok) throw new Error("저장된 데이터가 없습니다.");
  return response.json();
}
