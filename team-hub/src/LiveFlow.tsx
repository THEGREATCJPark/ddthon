import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, GitBranch, Minus, Plus } from "lucide-react";
import { STATUS_NAMES, type Issue } from "./domain";
import { STAGES, stageProgress, type StageId } from "./stages";
let diagram: Promise<string> | null = null;
function source() {
  return (diagram ||= fetch(
    `${import.meta.env.BASE_URL}archify/development.svg`,
  )
    .then((r) => {
      if (!r.ok) throw new Error("순서도를 불러오지 못했습니다.");
      return r.text();
    })
    .catch((e) => {
      diagram = null;
      throw e;
    }));
}
export default function LiveFlow({
  issues,
  onStage,
}: {
  issues: Issue[];
  onStage: (id: StageId) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState("");
  const [error, setError] = useState("");
  const [zoom, setZoom] = useState(1);
  useEffect(() => {
    let active = true;
    source()
      .then((s) => {
        if (active) setSvg(s);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    const root = ref.current;
    if (!root || !svg) return;
    // Only checked-in SVG from the pinned Archify renderer enters this DOM.
    root.innerHTML = svg;
    const graphic = root.querySelector("svg")!;
    graphic.setAttribute("viewBox", "28 40 795 374");
    graphic.setAttribute("lang", "ko");
    graphic.setAttribute("role", "group");
    graphic.setAttribute("aria-label", "작업 상태가 연결된 팀 개발 순서도");
    graphic.querySelector("[data-legend]")?.remove();
    for (const stage of STAGES) {
      const progress = stageProgress(issues, stage.id);
      const node = graphic.querySelector<SVGGElement>(
        `[data-node-id="${stage.id}"]`,
      );
      if (!node) continue;
      const statusName =
        progress.status === "empty" ? "미등록" : STATUS_NAMES[progress.status];
      node.setAttribute("data-status", progress.status);
      node.setAttribute(
        "aria-label",
        `${stage.name} · ${statusName} · ${progress.done}/${progress.total} 완료. 관련 작업 보기`,
      );
      node.removeAttribute("aria-pressed");
      const sublabel = node.querySelector('[data-detail="context"]');
      if (sublabel)
        sublabel.textContent = progress.total
          ? `${statusName} · ${progress.done}/${progress.total}`
          : "작업 연결 +";
      const rect = node.querySelector("rect.c-mask");
      if (rect) {
        const lamp = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "circle",
        );
        lamp.setAttribute(
          "cx",
          String(
            Number(rect.getAttribute("x")) +
              Number(rect.getAttribute("width")) -
              8,
          ),
        );
        lamp.setAttribute("cy", String(Number(rect.getAttribute("y")) + 8));
        lamp.setAttribute("r", "3");
        lamp.classList.add("stage-lamp");
        node.append(lamp);
      }
      node.addEventListener("click", () => onStage(stage.id));
      node.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onStage(stage.id);
        }
      });
    }
    // A highlighted connector reflects only its destination's mapped task status.
    graphic.querySelectorAll("[data-edge-to]").forEach((edge) => {
      const id = edge.getAttribute("data-edge-to") as StageId;
      if (STAGES.some((s) => s.id === id))
        edge.setAttribute("data-status", stageProgress(issues, id).status);
    });
  }, [svg, issues, onStage]);
  const active = STAGES.filter((s) =>
    ["doing", "blocked"].includes(stageProgress(issues, s.id).status),
  );
  return (
    <section className="panel live-flow">
      <div className="panel-heading">
        <h2>
          <GitBranch size={22} />팀 개발 흐름
        </h2>
        <div className="flow-tools">
          <button
            className="icon-button"
            aria-label="순서도 축소"
            disabled={zoom <= 1}
            onClick={() => setZoom(Math.max(1, zoom - 0.25))}
          >
            <Minus size={18} />
          </button>
          <span>{Math.round(zoom * 100)}%</span>
          <button
            className="icon-button"
            aria-label="순서도 확대"
            disabled={zoom >= 2}
            onClick={() => setZoom(Math.min(2, zoom + 0.25))}
          >
            <Plus size={18} />
          </button>
          <a
            className="icon-button"
            aria-label="Archify 원본 열기"
            href={`${import.meta.env.BASE_URL}archify/development.html`}
            target="_blank"
            rel="noreferrer"
          >
            <ArrowUpRight size={18} />
          </a>
        </div>
      </div>
      <div className="flow-status-bar">
        <div className="now-stages">
          {active.length ? (
            active.map((s) => (
              <button
                key={s.id}
                onClick={() => onStage(s.id)}
                className={`current-stage ${stageProgress(issues, s.id).status}`}
              >
                <span className="dot" />
                {s.name}
              </button>
            ))
          ) : (
            <span>진행 중인 작업 없음</span>
          )}
        </div>
        <div className="flow-legend">
          {(["todo", "doing", "blocked", "done"] as const).map((s) => (
            <span key={s}>
              <i className={`legend-dot ${s}`} />
              {STATUS_NAMES[s]}
            </span>
          ))}
        </div>
      </div>
      {error ? (
        <p className="sync-warning" role="alert">
          {error}
        </p>
      ) : (
        <div className="live-flow-canvas">
          <div
            className="live-archify"
            ref={ref}
            style={{ width: `${zoom * 100}%` }}
          />
        </div>
      )}
      <div className="flow-bottom">
        <span>노드 선택 → 연결된 작업</span>
        <a
          href="https://github.com/tt-a1i/archify"
          target="_blank"
          rel="noreferrer"
        >
          Archify ↗
        </a>
      </div>
    </section>
  );
}
