import {
  lazy,
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  CheckCheck,
  ChevronRight,
  CircleHelp,
  Flag,
  GitBranch,
  Github,
  LayoutDashboard,
  ListTodo,
  Menu,
  MessageSquare,
  Plus,
  RefreshCw,
  Search,
  Target,
  Users,
  X,
} from "lucide-react";
import { fetchIssues, fetchSnapshot } from "./api";
import { drafts, goals } from "./content";
import {
  activeIssues,
  checklist,
  cleanTitle,
  formatDate,
  KIND_NAMES,
  kindOf,
  matches,
  REPO_URL,
  STATUS_NAMES,
  statusOf,
  trackOf,
  type Issue,
  type Kind,
  type Snapshot,
  type Status,
} from "./domain";
import { Composer, Help, IssueDetail, Modal } from "./Modal";
import LiveFlow from "./LiveFlow";
import { useFlowState } from "./useFlowState";
import { STAGES, stageOf, stageProgress, type StageId } from "./stages";
const DiagramTab = lazy(() => import("./Diagram"));
const tabs = [
  { id: "dashboard", name: "대시보드", icon: LayoutDashboard },
  { id: "board", name: "진행 보드", icon: ListTodo },
  { id: "goals", name: "목표", icon: Target },
  { id: "discussions", name: "의견", icon: MessageSquare },
  { id: "diagrams", name: "순서도", icon: GitBranch },
];
function readTab() {
  const id = location.hash.slice(1);
  return tabs.some((t) => t.id === id) ? id : "dashboard";
}
function Avatar({ name }: { name: string }) {
  return (
    <span className="avatar" title={name}>
      {name.slice(0, 2).toUpperCase()}
    </span>
  );
}
function Empty({
  title,
  action,
  onAction,
}: {
  title: string;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      {action && (
        <button className="button" onClick={onAction}>
          <Plus size={18} />
          {action}
        </button>
      )}
    </div>
  );
}
function IssueCard({
  issue,
  onOpen,
}: {
  issue: Issue;
  onOpen: (i: Issue) => void;
}) {
  const check = checklist(issue.body);
  return (
    <button className="issue-card" onClick={() => onOpen(issue)}>
      <div className="issue-top">
        <span className={`tag track-${trackOf(issue).toLowerCase()}`}>
          {trackOf(issue)}
        </span>
        <span>#{issue.number}</span>
      </div>
      <h3>{cleanTitle(issue.title)}</h3>
      {check.total > 0 && (
        <div className="check-summary">
          <CheckCheck size={16} />
          {check.done}/{check.total}
        </div>
      )}
      <div className="issue-bottom">
        <div>
          {issue.assignees.length ? (
            issue.assignees.map((a) => <Avatar name={a.login} key={a.login} />)
          ) : (
            <span className="unassigned">
              <Users size={15} />
              미배정
            </span>
          )}
        </div>
        <span>
          <MessageSquare size={15} />
          {issue.comments}
        </span>
      </div>
    </button>
  );
}
export default function App() {
  const flow = useFlowState();
  const [tab, setTab] = useState(readTab);
  const [mobile, setMobile] = useState(false);
  const [query, setQuery] = useState("");
  const [track, setTrack] = useState("전체");
  const [owner, setOwner] = useState("전체");
  const [statusFilter, setStatusFilter] = useState("전체");
  const [stageFilter, setStageFilter] = useState("전체");
  const [diagramMode, setDiagramMode] = useState("live");
  const [snapshot, setSnapshot] = useState<Snapshot>({
    generatedAt: null,
    issues: [],
    comments: {},
  });
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncState, setSyncState] = useState("연결 중");
  const [syncedAt, setSyncedAt] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [detail, setDetail] = useState<Issue | null>(null);
  const [composer, setComposer] = useState<{
    kind: Kind;
    title?: string;
    body?: string;
    stage?: StageId;
  } | null>(null);
  const [help, setHelp] = useState(false);
  const [toast, setToast] = useState("");
  const [stageDetail, setStageDetail] = useState<StageId | null>(null);
  const busy = useRef(false);
  const snapshotRef = useRef(snapshot);
  const hasLive = useRef(false);
  const refresh = useCallback(async () => {
    if (busy.current) return;
    busy.current = true;
    setLoading(true);
    try {
      const data = await fetchIssues();
      setIssues(activeIssues(data));
      setSyncedAt(new Date().toISOString());
      setSyncState("동기화됨");
      setError("");
      hasLive.current = true;
    } catch (e) {
      const saved = snapshotRef.current;
      if (!hasLive.current && saved.generatedAt) {
        setIssues(activeIssues(saved.issues));
        setSyncedAt(saved.generatedAt);
      }
      setSyncState(
        hasLive.current
          ? "이전 조회"
          : saved.generatedAt
            ? "저장본"
            : "연결 오류",
      );
      setError(
        `${e instanceof Error ? e.message : "연결하지 못했습니다."} ${hasLive.current ? "마지막 조회 결과입니다." : saved.generatedAt ? "배포 시점 저장본입니다." : "GitHub 원본을 확인해 주세요."}`,
      );
    } finally {
      busy.current = false;
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    let active = true;
    fetchSnapshot()
      .then((data) => {
        if (active) {
          snapshotRef.current = data;
          setSnapshot(data);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (active) void refresh();
      });
    const timer = setInterval(() => {
      if (!document.hidden) void refresh();
    }, 300000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [refresh]);
  useEffect(() => {
    const change = () => {
      setTab(readTab());
      setQuery("");
    };
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 4500);
    return () => clearTimeout(timer);
  }, [toast]);
  function navigate(id: string) {
    location.hash = id;
    setTab(id);
    setQuery("");
    setMobile(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function showBoard(status = "전체") {
    setStatusFilter(status);
    setTrack("전체");
    setOwner("전체");
    setStageFilter("전체");
    navigate("board");
  }
  function addStage(stage: StageId) {
    setStageDetail(null);
    setComposer({ kind: "task", stage });
  }
  const current = tabs.find((t) => t.id === tab)!;
  const tasks = issues.filter((i) => kindOf(i) === "task");
  const done = tasks.filter((i) => statusOf(i) === "done").length;
  const doing = tasks.filter((i) => statusOf(i) === "doing");
  const blockers = tasks.filter((i) => statusOf(i) === "blocked");
  const percent = tasks.length ? Math.round((done / tasks.length) * 100) : 0;
  const discussions = issues.filter((i) => kindOf(i) === "discussion");
  const sharedGoals = issues.filter((i) => kindOf(i) === "goal");
  const owners = [
    ...new Set(tasks.flatMap((i) => i.assignees.map((a) => a.login))),
  ];
  const filtered = tasks.filter(
    (i) =>
      matches(i, query) &&
      (track === "전체" || trackOf(i) === track) &&
      (statusFilter === "전체" || statusOf(i) === statusFilter) &&
      (stageFilter === "전체" || stageOf(i) === stageFilter) &&
      (owner === "전체" ||
        (owner === "미배정"
          ? !i.assignees.length
          : i.assignees.some((a) => a.login === owner))),
  );
  const statusOrder: Status[] = ["todo", "doing", "blocked", "done"];
  return (
    <div className="app">
      <a href="#main-content" className="skip-link">
        본문으로 이동
      </a>
      {mobile && (
        <button
          className="sidebar-shade"
          aria-label="메뉴 닫기"
          onClick={() => setMobile(false)}
        />
      )}
      <aside className={`sidebar ${mobile ? "mobile-open" : ""}`}>
        <a
          className="brand"
          href="#dashboard"
          onClick={() => navigate("dashboard")}
        >
          <span className="brand-mark">∞</span>
          <strong>디디톤</strong>
        </a>
        <div className="project-name">Agent SkillLoop</div>
        <nav aria-label="주 메뉴">
          {tabs.map((t) => (
            <button
              key={t.id}
              className={`nav-item ${tab === t.id ? "active" : ""}`}
              aria-current={tab === t.id ? "page" : undefined}
              onClick={() => navigate(t.id)}
            >
              <t.icon size={22} />
              <span>{t.name}</span>
              {t.id === "discussions" &&
                discussions.filter((i) => i.state === "open").length > 0 && (
                  <b>{discussions.filter((i) => i.state === "open").length}</b>
                )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <a
            className="nav-item"
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
          >
            <Github size={21} />
            <span>GitHub</span>
            <ArrowUpRight size={17} />
          </a>
          <button className="nav-item" onClick={() => setHelp(true)}>
            <CircleHelp size={21} />
            <span>사용 가이드</span>
          </button>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div>
            <button
              className="icon-button mobile-toggle"
              aria-label="메뉴 열기"
              onClick={() => setMobile(true)}
            >
              <Menu size={24} />
            </button>
            <span>TEAM WORKSPACE</span>
          </div>
          <div className="topbar-right">
            <span className={`dot ${error ? "amber" : "green"}`} />
            <span title={formatDate(syncedAt)}>{syncState}</span>
            <a
              className="repo-badge"
              href={REPO_URL}
              target="_blank"
              rel="noreferrer"
            >
              <Github size={19} />
              ddthon
              <ArrowUpRight size={16} />
            </a>
          </div>
        </header>
        <main id="main-content">
          {tab === "dashboard" && (
            <div className="event-banner">
              <img
                src={`${import.meta.env.BASE_URL}images/ddthon-banner.png`}
                width="1024"
                height="434"
                alt="제4회 디디톤 · DS S/W Developer Hackathon. Humans set the direction. AI brings the speed."
                fetchPriority="high"
              />
            </div>
          )}
          <div className="page-heading">
            <h1>{current.name}</h1>
            <div className="heading-actions">
              <button
                className="button refresh"
                aria-label="새로고침"
                onClick={refresh}
                disabled={loading}
              >
                <RefreshCw size={19} className={loading ? "spin" : ""} />
              </button>
              <button
                className="button primary"
                onClick={() =>
                  setComposer({
                    kind:
                      tab === "goals"
                        ? "goal"
                        : tab === "discussions"
                          ? "discussion"
                          : tab === "diagrams"
                            ? "diagram"
                            : "task",
                  })
                }
              >
                <Plus size={20} />
                {tab === "goals"
                  ? "목표 추가"
                  : tab === "discussions"
                    ? "의견 쓰기"
                    : tab === "diagrams"
                      ? "순서도 공유"
                      : "작업 추가"}
              </button>
            </div>
          </div>
          {error && (
            <div className="sync-warning" role="alert">
              {error}
              <a href={`${REPO_URL}/issues`} target="_blank" rel="noreferrer">
                GitHub 원본 ↗
              </a>
            </div>
          )}
          {tab !== "diagrams" && (
            <div className="search-row">
              <label className="search-box">
                <Search size={20} />
                <input
                  aria-label="작업·의견 검색"
                  placeholder="검색"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
                {query && (
                  <button
                    className="icon-button"
                    aria-label="검색 지우기"
                    onClick={() => setQuery("")}
                  >
                    <X size={18} />
                  </button>
                )}
              </label>
              {tab === "dashboard" && (
                <span className="summary-count">
                  완료 {done} / {tasks.length}
                  <strong>{percent}%</strong>
                </span>
              )}
            </div>
          )}
          {tab === "dashboard" && query ? (
            <section className="panel">
              <div className="panel-heading">
                <h2>검색 결과</h2>
              </div>
              <div className="card-grid">
                {issues
                  .filter((i) => matches(i, query))
                  .map((i) => (
                    <IssueCard key={i.number} issue={i} onOpen={setDetail} />
                  ))}
              </div>
              {!issues.some((i) => matches(i, query)) && (
                <Empty title="검색 결과 없음" />
              )}
            </section>
          ) : (
            tab === "dashboard" && (
              <>
                <section className="stats">
                  {[
                    {
                      name: "전체 작업",
                      value: tasks.length,
                      status: "전체",
                      icon: ListTodo,
                    },
                    {
                      name: "진행 중",
                      value: doing.length,
                      status: "doing",
                      icon: RefreshCw,
                    },
                    {
                      name: "도움 필요",
                      value: blockers.length,
                      status: "blocked",
                      icon: Flag,
                    },
                    {
                      name: "완료",
                      value: done,
                      status: "done",
                      icon: CheckCheck,
                    },
                  ].map((s) => (
                    <button
                      key={s.name}
                      className={`stat ${s.status}`}
                      onClick={() => showBoard(s.status)}
                    >
                      <div className="stat-top">
                        <span>{s.name}</span>
                        <s.icon size={24} />
                      </div>
                      <div className="stat-number">
                        {s.value}
                        <ArrowUpRight size={24} />
                      </div>
                    </button>
                  ))}
                </section>
                <LiveFlow
                  issues={issues}
                  onStage={setStageDetail}
                  flow={flow}
                />
                <div className="dashboard-work">
                  <section className="panel">
                    <div className="panel-heading">
                      <h2>
                        진행 중{" "}
                        <span className="heading-count">{doing.length}</span>
                      </h2>
                      <button
                        className="text-button"
                        onClick={() => showBoard("doing")}
                      >
                        전체 보기
                        <ArrowRight size={17} />
                      </button>
                    </div>
                    {doing.length ? (
                      <div className="compact-cards">
                        {doing.slice(0, 4).map((i) => (
                          <IssueCard
                            key={i.number}
                            issue={i}
                            onOpen={setDetail}
                          />
                        ))}
                      </div>
                    ) : (
                      <Empty
                        title="진행 중인 작업 없음"
                        action="작업 추가"
                        onAction={() => setComposer({ kind: "task" })}
                      />
                    )}
                  </section>
                  <section className="panel">
                    <div className="panel-heading">
                      <h2>
                        <Flag size={22} />
                        도움 필요
                      </h2>
                      <span className="heading-count">{blockers.length}</span>
                    </div>
                    {blockers.length ? (
                      <div className="compact-cards">
                        {blockers.slice(0, 4).map((i) => (
                          <IssueCard
                            key={i.number}
                            issue={i}
                            onOpen={setDetail}
                          />
                        ))}
                      </div>
                    ) : (
                      <Empty title="막힌 작업 없음" />
                    )}
                  </section>
                </div>
                {tasks.length === 0 && (
                  <section className="panel starter-panel">
                    <div className="panel-heading">
                      <h2>추천 작업</h2>
                      <span className="tag neutral">미등록 초안</span>
                    </div>
                    <div className="starter-list">
                      {drafts.map((d, index) => (
                        <button
                          key={d.title}
                          onClick={() =>
                            setComposer({
                              kind: "task",
                              title: d.title,
                              body: d.detail,
                              stage: (
                                [
                                  "requirements",
                                  "p0",
                                  "p1",
                                  "design",
                                  "sharing",
                                  "qa",
                                ] as StageId[]
                              )[index],
                            })
                          }
                        >
                          <span className="tag">{d.track}</span>
                          <strong>{d.title}</strong>
                          <Plus size={20} />
                        </button>
                      ))}
                    </div>
                  </section>
                )}
              </>
            )
          )}
          {tab === "board" && (
            <>
              <div className="board-controls">
                <div className="filter-pills">
                  {["전체", "P0", "P1", "공통", "공유", "QA"].map((t) => (
                    <button
                      key={t}
                      aria-pressed={track === t}
                      className={track === t ? "selected" : ""}
                      onClick={() => setTrack(t)}
                    >
                      {t}
                    </button>
                  ))}
                </div>
                <div className="select-filters">
                  <select
                    aria-label="단계 필터"
                    value={stageFilter}
                    onChange={(e) => setStageFilter(e.target.value)}
                  >
                    <option value="전체">모든 단계</option>
                    {STAGES.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                  <select
                    aria-label="담당자 필터"
                    value={owner}
                    onChange={(e) => setOwner(e.target.value)}
                  >
                    <option value="전체">모든 담당자</option>
                    <option>미배정</option>
                    {owners.map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                  {statusFilter !== "전체" && (
                    <button
                      className="filter-clear"
                      onClick={() => setStatusFilter("전체")}
                    >
                      {STATUS_NAMES[statusFilter as Status]}
                      <X size={15} />
                    </button>
                  )}
                </div>
              </div>
              <div className="kanban">
                {statusOrder
                  .filter((s) => statusFilter === "전체" || statusFilter === s)
                  .map((s) => (
                    <section className={`kanban-column ${s}`} key={s}>
                      <div className="column-heading">
                        <h2>
                          <i className={`legend-dot ${s}`} />
                          {STATUS_NAMES[s]}
                          <span>
                            {filtered.filter((i) => statusOf(i) === s).length}
                          </span>
                        </h2>
                        {s === "todo" && (
                          <button
                            className="icon-button"
                            aria-label="할 일 추가"
                            onClick={() => setComposer({ kind: "task" })}
                          >
                            <Plus size={21} />
                          </button>
                        )}
                      </div>
                      <div className="column-content">
                        {filtered
                          .filter((i) => statusOf(i) === s)
                          .map((i) => (
                            <IssueCard
                              key={i.number}
                              issue={i}
                              onOpen={setDetail}
                            />
                          ))}
                        {!filtered.some((i) => statusOf(i) === s) && (
                          <p className="column-empty">작업 없음</p>
                        )}
                      </div>
                    </section>
                  ))}
              </div>
            </>
          )}
          {tab === "goals" && (
            <>
              <div className="goals-grid">
                {goals
                  .filter((g) =>
                    `${g.id} ${g.subtitle}`
                      .toLowerCase()
                      .includes(query.toLowerCase()),
                  )
                  .map((g) => {
                    const progress = stageProgress(
                      issues,
                      g.id.toLowerCase() as StageId,
                    );
                    return (
                      <section
                        className={`panel goal-detail ${g.color}`}
                        key={g.id}
                      >
                        <div className="goal-detail-top">
                          <span className="goal-id">{g.id}</span>
                          <span>
                            {progress.done}/{progress.total} 작업 완료
                          </span>
                        </div>
                        <h2>{g.subtitle}</h2>
                        <div className="progress-track">
                          <div
                            style={{
                              width: `${progress.total ? (progress.done / progress.total) * 100 : 0}%`,
                            }}
                          />
                        </div>
                        <ul>
                          {g.checks.map((c) => (
                            <li key={c}>
                              <span className="unchecked" />
                              {c}
                            </li>
                          ))}
                        </ul>
                        <button
                          className="button"
                          onClick={() =>
                            setStageDetail(g.id.toLowerCase() as StageId)
                          }
                        >
                          관련 작업
                          <ArrowRight size={18} />
                        </button>
                        <span className="goal-evidence-note">
                          시연 결과는 별도 검증
                        </span>
                      </section>
                    );
                  })}
              </div>
              <section className="panel">
                <div className="panel-heading">
                  <h2>팀 목표</h2>
                  <button
                    className="text-button"
                    onClick={() => setComposer({ kind: "goal" })}
                  >
                    <Plus size={18} />
                    추가
                  </button>
                </div>
                {sharedGoals.filter((i) => matches(i, query)).length ? (
                  <div className="card-grid">
                    {sharedGoals
                      .filter((i) => matches(i, query))
                      .map((i) => (
                        <IssueCard
                          key={i.number}
                          issue={i}
                          onOpen={setDetail}
                        />
                      ))}
                  </div>
                ) : (
                  <Empty
                    title="등록된 목표 없음"
                    action="목표 추가"
                    onAction={() => setComposer({ kind: "goal" })}
                  />
                )}
              </section>
            </>
          )}
          {tab === "discussions" && (
            <section className="panel">
              <div className="panel-heading">
                <h2>
                  전체 의견{" "}
                  <span className="heading-count">
                    {discussions.filter((i) => matches(i, query)).length}
                  </span>
                </h2>
              </div>
              {discussions.filter((i) => matches(i, query)).length ? (
                <div className="discussion-list">
                  {discussions
                    .filter((i) => matches(i, query))
                    .map((i) => (
                      <button key={i.number} onClick={() => setDetail(i)}>
                        <Avatar name={i.user.login} />
                        <div>
                          <strong>{cleanTitle(i.title)}</strong>
                          <p>
                            {i.user.login} · {formatDate(i.updated_at)}{" "}
                            {i.state === "closed" ? "· 종료" : ""}
                          </p>
                        </div>
                        <span>
                          <MessageSquare size={20} />
                          {i.comments}
                        </span>
                        <ChevronRight size={20} />
                      </button>
                    ))}
                </div>
              ) : (
                <Empty
                  title={query ? "검색 결과 없음" : "아직 의견이 없습니다"}
                  action="첫 의견 쓰기"
                  onAction={() => setComposer({ kind: "discussion" })}
                />
              )}
            </section>
          )}
          {tab === "diagrams" && (
            <>
              <div className="diagram-tabs">
                <button
                  className={diagramMode === "live" ? "selected" : ""}
                  onClick={() => setDiagramMode("live")}
                >
                  개발 흐름
                </button>
                <button
                  className={diagramMode === "notes" ? "selected" : ""}
                  onClick={() => setDiagramMode("notes")}
                >
                  아이템 설명 · Mermaid
                </button>
              </div>
              {diagramMode === "live" ? (
                <LiveFlow
                  issues={issues}
                  onStage={setStageDetail}
                  flow={flow}
                />
              ) : (
                <Suspense fallback={<p role="status">불러오는 중…</p>}>
                  <DiagramTab
                    issues={issues}
                    toast={setToast}
                    onShare={(title, body) =>
                      setComposer({ kind: "diagram", title, body })
                    }
                  />
                </Suspense>
              )}
            </>
          )}
          <footer className="footer">
            <span>디디톤 · Team Hub</span>
            <a
              href={`${REPO_URL}/tree/codex/team-hub/team-hub`}
              target="_blank"
              rel="noreferrer"
            >
              소스
              <ArrowUpRight size={15} />
            </a>
          </footer>
        </main>
      </div>
      {stageDetail && (
        <Modal
          title={STAGES.find((s) => s.id === stageDetail)!.name}
          onClose={() => setStageDetail(null)}
        >
          <div className="stage-summary">
            <span
              className={`status ${stageProgress(issues, stageDetail).status}`}
            >
              {stageProgress(issues, stageDetail).status === "empty"
                ? "미등록"
                : STATUS_NAMES[
                    stageProgress(issues, stageDetail).status as Status
                  ]}
            </span>
            <span>
              {stageProgress(issues, stageDetail).done}/
              {stageProgress(issues, stageDetail).total} 완료
            </span>
            <button
              className="button primary"
              onClick={() => addStage(stageDetail)}
            >
              <Plus size={18} />
              작업 연결
            </button>
          </div>
          <div className="stage-task-list">
            {stageProgress(issues, stageDetail).tasks.map((i) => (
              <IssueCard
                key={i.number}
                issue={i}
                onOpen={(issue) => {
                  setStageDetail(null);
                  setDetail(issue);
                }}
              />
            ))}
          </div>
          {!stageProgress(issues, stageDetail).total && (
            <Empty title="연결된 작업 없음" />
          )}
        </Modal>
      )}
      {composer && (
        <Composer
          key={JSON.stringify(composer)}
          kind={composer.kind}
          initialTitle={composer.title}
          initialBody={composer.body}
          initialStage={composer.stage}
          onClose={() => setComposer(null)}
        />
      )}{" "}
      {detail && (
        <IssueDetail
          issue={issues.find((i) => i.number === detail.number) || detail}
          cachedComments={snapshot.comments[String(detail.number)] || []}
          onClose={() => setDetail(null)}
        />
      )}{" "}
      {help && <Help onClose={() => setHelp(false)} />}{" "}
      {toast && (
        <div className="toast" role="status">
          <Check size={18} />
          {toast}
        </div>
      )}
    </div>
  );
}
