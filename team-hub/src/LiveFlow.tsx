import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, GitBranch, Minus, Plus } from "lucide-react";
import { STATUS_NAMES, type Issue } from "./domain";
import { STAGES, stageProgress, type StageId } from "./stages";
import { Modal } from "./Modal";
import { encodeFlow, FLOW_STATUSES } from "./manualFlow";
import type { useFlowState } from "./useFlowState";
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
  flow,
}: {
  issues: Issue[];
  onStage: (id: StageId) => void;
  flow: ReturnType<typeof useFlowState>;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState("");
  const [error, setError] = useState("");
  const [zoom, setZoom] = useState(1);
  const [selected, setSelected] = useState<StageId | null>(null);
  const [shareLink, setShareLink] = useState("");
  const [copied, setCopied] = useState(false);
  const manual = flow.state.mode === "manual";
  const statusFor = (id: StageId) =>
    manual ? flow.state.stages[id] : stageProgress(issues, id).status;
  const selectStage = (id: StageId) => (manual ? setSelected(id) : onStage(id));
  async function share() {
    const url = new URL(location.href);
    url.searchParams.set("flow", encodeFlow(flow.state));
    url.hash = "diagrams";
    setShareLink(url.href);
    setCopied(false);
    try {
      await navigator.clipboard.writeText(url.href);
      setCopied(true);
    } catch {
      /* Selectable URL remains available. */
    }
  }
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
    graphic.setAttribute(
      "aria-label",
      manual
        ? "수동 상태를 표시한 팀 개발 순서도"
        : "GitHub 작업 상태가 연결된 팀 개발 순서도",
    );
    graphic.querySelector("[data-legend]")?.remove();
    for (const stage of STAGES) {
      const progress = stageProgress(issues, stage.id);
      const node = graphic.querySelector<SVGGElement>(
        `[data-node-id="${stage.id}"]`,
      );
      if (!node) continue;
      const status = statusFor(stage.id);
      const statusName = status === "empty" ? "미등록" : STATUS_NAMES[status];
      node.setAttribute("data-status", status);
      node.setAttribute(
        "aria-label",
        manual
          ? `${stage.name} · ${statusName}. 상태 변경`
          : `${stage.name} · ${statusName} · ${progress.done}/${progress.total} 완료. 관련 작업 보기`,
      );
      node.removeAttribute("aria-pressed");
      const sublabel = node.querySelector('[data-detail="context"]');
      if (sublabel)
        sublabel.textContent = manual
          ? statusName
          : progress.total
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
      node.addEventListener("click", () => selectStage(stage.id));
      node.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectStage(stage.id);
        }
      });
    }
    // Highlight only the destination's status in the selected source.
    graphic.querySelectorAll("[data-edge-to]").forEach((edge) => {
      const id = edge.getAttribute("data-edge-to") as StageId;
      if (STAGES.some((s) => s.id === id))
        edge.setAttribute("data-status", statusFor(id));
    });
  }, [svg, issues, onStage, flow.state]);
  const active = STAGES.filter((s) =>
    ["doing", "blocked"].includes(statusFor(s.id)),
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
      <div className="flow-mode-bar">
        <div className="flow-mode" role="group" aria-label="순서도 상태 출처">
          <button
            aria-pressed={!manual}
            onClick={() => flow.setState((s) => ({ ...s, mode: "github" }))}
          >
            GitHub 연동
          </button>
          <button
            aria-pressed={manual}
            onClick={() => flow.setState((s) => ({ ...s, mode: "manual" }))}
          >
            직접 표시
          </button>
        </div>
        {manual && (
          <button className="button" onClick={share}>
            상태 링크 복사
          </button>
        )}
        <span className="flow-source">
          {manual
            ? flow.storageError
              ? "현재 화면만 유지 · 저장 불가"
              : "이 브라우저에 저장 · 링크로 공유"
            : "연결된 GitHub 작업 기준"}
        </span>
      </div>
      <div className="flow-status-bar">
        <div className="now-stages">
          {active.length ? (
            active.map((s) => (
              <button
                key={s.id}
                onClick={() => selectStage(s.id)}
                className={`current-stage ${statusFor(s.id)}`}
              >
                <span className="dot" />
                {s.name}
              </button>
            ))
          ) : (
            <span>
              {manual
                ? "노드를 눌러 현재 단계를 표시하세요"
                : "진행 중인 작업 없음"}
            </span>
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
        <span>
          {manual ? "노드 선택 → 상태 변경" : "노드 선택 → 연결된 작업"}
        </span>
        <a
          href="https://github.com/tt-a1i/archify"
          target="_blank"
          rel="noreferrer"
        >
          Archify ↗
        </a>
      </div>
      {selected && (
        <Modal
          title={STAGES.find((s) => s.id === selected)!.name}
          onClose={() => setSelected(null)}
        >
          <div
            className="manual-status-picker"
            role="group"
            aria-label="단계 상태 선택"
          >
            {FLOW_STATUSES.map((status) => (
              <button
                key={status}
                className={`manual-status ${status}`}
                aria-pressed={flow.state.stages[selected] === status}
                onClick={() => {
                  flow.setState((s) => ({
                    ...s,
                    stages: { ...s.stages, [selected]: status },
                  }));
                  setSelected(null);
                }}
              >
                <i className={`legend-dot ${status}`} />
                {STATUS_NAMES[status]}
              </button>
            ))}
          </div>
          <div className="manual-modal-footer">
            <span>수동 표시 · GitHub 작업 상태는 유지됩니다</span>
            <button
              className="button"
              onClick={() => {
                const id = selected;
                setSelected(null);
                onStage(id);
              }}
            >
              연결된 작업
            </button>
          </div>
        </Modal>
      )}
      {shareLink && (
        <Modal
          title={copied ? "상태 링크를 복사했습니다" : "상태 링크 공유"}
          onClose={() => setShareLink("")}
        >
          <p>
            지금 표시한 상태를 전달합니다. 이후 변경은 새 링크로 공유하세요.
          </p>
          <label className="share-link-label">
            공유 링크
            <input
              readOnly
              aria-label="상태 공유 링크"
              value={shareLink}
              onFocus={(e) => e.target.select()}
            />
          </label>
        </Modal>
      )}
    </section>
  );
}
