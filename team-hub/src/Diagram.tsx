import { useEffect, useId, useRef, useState } from "react";
import {
  Code2,
  Copy,
  Download,
  Expand,
  GitBranch,
  Plus,
  RotateCcw,
} from "lucide-react";
import { diagrams } from "./content";
import { cleanTitle, codeOf, kindOf, REPO_URL, type Issue } from "./domain";
let mermaidPromise: Promise<(typeof import("mermaid"))["default"]> | null =
  null;
function getMermaid() {
  return (mermaidPromise ||= import("mermaid").then((m) => {
    m.default.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      suppressErrorRendering: true,
      maxTextSize: 15000,
      maxEdges: 150,
      theme: "base",
      themeVariables: {
        fontFamily: "system-ui, sans-serif",
        primaryColor: "#eef2f8",
        primaryTextColor: "#102449",
        primaryBorderColor: "#bbc7d8",
        lineColor: "#64748b",
        secondaryColor: "#fff5df",
        tertiaryColor: "#f7f8fb",
      },
      flowchart: { htmlLabels: false, curve: "basis", padding: 18 },
    });
    return m.default;
  }));
}
export function Mermaid({ code }: { code: string }) {
  const id = useId().replace(/:/g, "");
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let cancelled = false;
    const timer = setTimeout(async () => {
      try {
        setError("");
        setLoading(true);
        if (code.length > 15000)
          throw new Error("다이어그램은 15,000자 이하로 작성해 주세요.");
        if (!code.trim()) throw new Error("Mermaid 코드를 입력해 주세요.");
        if (/%%\s*\{|^\s*---/m.test(code))
          throw new Error("설정 지시문 없이 다이어그램 본문만 입력해 주세요.");
        const mermaid = await getMermaid();
        const { svg } = await mermaid.render(
          `diagram-${id}-${crypto.randomUUID()}`,
          code,
        );
        if (!cancelled && ref.current) ref.current.innerHTML = svg;
      } catch (e) {
        if (!cancelled) {
          setError(
            e instanceof Error
              ? e.message.split("\n").slice(0, 4).join("\n")
              : "문법을 확인해 주세요.",
          );
          if (ref.current) ref.current.innerHTML = "";
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 350);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [code, id]);
  return (
    <>
      <div
        className="mermaid-view"
        ref={ref}
        style={error ? { display: "none" } : undefined}
        role="img"
        aria-label="Mermaid 순서도"
      />
      {loading && (
        <p className="diagram-message" role="status">
          순서도를 그리고 있어요…
        </p>
      )}
      {error && (
        <div className="diagram-error" role="alert">
          <strong>순서도를 그릴 수 없어요</strong>
          <pre>{error}</pre>
          <span>
            코드를 수정하면 다시 그립니다. 아래 단계 설명도 확인할 수 있습니다.
          </span>
        </div>
      )}
    </>
  );
}
export default function DiagramTab({
  issues,
  onShare,
  toast,
}: {
  issues: Issue[];
  onShare: (title: string, body: string) => void;
  toast: (message: string) => void;
}) {
  const shared = issues
    .filter((i) => kindOf(i) === "diagram" && i.state === "open")
    .map((i) => ({
      id: `issue-${i.number}`,
      name: cleanTitle(i.title),
      tag: `팀 공유 #${i.number}`,
      description: "팀이 GitHub에 공유한 다이어그램입니다.",
      steps: ["공유된 코드와 GitHub 원문에서 세부 설명을 확인하세요."],
      code: codeOf(i.body),
    }));
  const all = [...diagrams, ...shared];
  const [selected, setSelected] = useState("loop");
  const [editor, setEditor] = useState(false);
  const [code, setCode] = useState(diagrams[0].code);
  const [zoom, setZoom] = useState(false);
  const current = all.find((d) => d.id === selected) || all[0];
  function select(id: string) {
    const item = all.find((d) => d.id === id)!;
    setSelected(id);
    setCode(item.code);
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      toast("Mermaid 코드를 복사했습니다.");
    } catch {
      setEditor(true);
      toast("편집 창에서 코드를 선택해 복사해 주세요.");
    }
  }
  function download() {
    const blob = new Blob([code], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${current.id}.mmd`;
    a.click();
    URL.revokeObjectURL(url);
  }
  return (
    <div className="diagram-layout">
      <div className="diagram-library">
        <div className="section-eyebrow">FLOW LIBRARY</div>
        <h3>아이디어를 한눈에</h3>
        <p className="muted small">같은 그림을 보며 이야기하세요.</p>
        <div className="diagram-choices">
          {all.map((d) => (
            <button
              className={d.id === current.id ? "chosen" : ""}
              key={d.id}
              onClick={() => select(d.id)}
            >
              <GitBranch size={18} />
              <span>
                {d.name}
                <small>{d.tag}</small>
              </span>
            </button>
          ))}
        </div>
        {current.id.startsWith("issue-") && (
          <a
            className="text-button"
            href={`${REPO_URL}/issues/${current.id.slice(6)}`}
            target="_blank"
            rel="noreferrer"
          >
            GitHub 원문 · 수정 / 댓글
          </a>
        )}
        <div className="side-note">
          <Code2 size={18} />
          <strong>팀의 아이디어도 추가하세요</strong>
          <p>
            코드를 수정하고 GitHub에 공유하면 다른 팀원도 같은 그림을 볼 수
            있어요.
          </p>
        </div>
      </div>
      <div className="diagram-main">
        <div className="panel diagram-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">{current.tag}</span>
              <h2>{current.name}</h2>
            </div>
            <button
              className="icon-button"
              aria-label="순서도 크게 보기"
              onClick={() => setZoom(!zoom)}
            >
              <Expand size={18} />
            </button>
          </div>
          <p className="diagram-description">{current.description}</p>
          <div className={`diagram-canvas ${zoom ? "expanded" : ""}`}>
            <Mermaid code={code} />
            <div className="canvas-caption">
              <span className="dot green" /> Mermaid · 목표 흐름
            </div>
          </div>
          <div className="diagram-toolbar">
            <button className="text-button" onClick={() => setEditor(!editor)}>
              <Code2 size={16} />
              {editor ? "코드 접기" : "코드 편집"}
            </button>
            <div>
              <button
                className="icon-button"
                aria-label="코드 복사"
                onClick={copy}
              >
                <Copy size={16} />
              </button>
              <button
                className="icon-button"
                aria-label="Mermaid 파일 다운로드"
                onClick={download}
              >
                <Download size={16} />
              </button>
              <button
                className="button primary small-button"
                onClick={() =>
                  onShare(
                    current.name,
                    `### 설명\n${current.description}\n\n### 순서도\n\`\`\`mermaid\n${code}\n\`\`\`\n\n### 논의할 점\n`,
                  )
                }
              >
                <Plus size={15} />
                팀에 공유
              </button>
            </div>
          </div>
          {editor && (
            <div className="code-editor">
              <div>
                <label htmlFor="mermaid-code">Mermaid 코드</label>
                <button
                  className="text-button"
                  onClick={() => setCode(current.code)}
                >
                  <RotateCcw size={14} />
                  원본으로
                </button>
              </div>
              <textarea
                id="mermaid-code"
                value={code}
                maxLength={15000}
                onChange={(e) => setCode(e.target.value)}
                spellCheck={false}
              />
              <p className="muted small">
                편집 내용은 아직 공유되지 않았습니다. ‘팀에 공유’ 후 GitHub에서
                등록을 완료하세요.
              </p>
            </div>
          )}
        </div>
        <div className="panel step-panel">
          <h3>말로 풀어보면</h3>
          <div className="flow-steps">
            {current.steps.map((s, i) => (
              <div key={s}>
                <span>{String(i + 1).padStart(2, "0")}</span>
                <p>{s}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
