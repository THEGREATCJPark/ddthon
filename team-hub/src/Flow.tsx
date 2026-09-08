import { useEffect, useRef, useState } from "react";
import { Check, Link as LinkIcon } from "lucide-react";
import { Modal } from "./Modal";
import {
  STAGES,
  STATUS,
  decodeProgress,
  emptyProgress,
  encodeProgress,
  type StageId,
  type StageStatus,
} from "./workspace";
const KEY = "nowhere.progress.v4";
function initial() {
  const shared = decodeProgress(
    new URL(location.href).searchParams.get("flow"),
  );
  if (shared) return shared;
  try {
    return decodeProgress(localStorage.getItem(KEY)) || emptyProgress();
  } catch {
    return emptyProgress();
  }
}
export default function Flow() {
  const [progress, setProgress] = useState(initial);
  const [selected, setSelected] = useState<StageId | null>(null);
  const [svg, setSvg] = useState("");
  const [error, setError] = useState("");
  const [storageFailed, setStorageFailed] = useState(false);
  const [share, setShare] = useState("");
  const [copied, setCopied] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let active = true;
    fetch(`${import.meta.env.BASE_URL}archify/development.svg?v=aidlc-v4`, {
      cache: "no-cache",
    })
      .then((r) => {
        if (!r.ok) throw Error();
        return r.text();
      })
      .then((s) => {
        if (active) setSvg(s);
      })
      .catch(() => {
        if (active)
          setError("순서도를 불러오지 못했습니다. 새로고침해 주세요.");
      });
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem(KEY, encodeProgress(progress));
      setStorageFailed(false);
    } catch {
      setStorageFailed(true);
    }
    const url = new URL(location.href);
    if (url.searchParams.has("flow")) {
      url.searchParams.set("flow", encodeProgress(progress));
      history.replaceState(null, "", url);
    }
  }, [progress]);
  useEffect(() => {
    if (!ref.current || !svg) return;
    ref.current.innerHTML = svg;
    const graphic = ref.current.querySelector("svg")!;
    graphic.querySelector("[data-legend]")?.remove();
    graphic.setAttribute("role", "group");
    graphic.removeAttribute("aria-labelledby");
    graphic.setAttribute("aria-label", "AI-DLC 활용 개발 진행 순서도");
    const laneLabels = [
      "01 / INCEPTION",
      "02 / CONSTRUCTION · 공통 기반",
      "CONSTRUCTION · U1 / U2 / U3 병렬 진행",
      "03 / BUILD & TEST",
      "통합 시연",
    ];
    graphic.querySelectorAll("text.t-dim").forEach((label, index) => {
      if (index < laneLabels.length) label.textContent = laneLabels[index];
    });
    for (const stage of STAGES) {
      const node = graphic.querySelector<SVGGElement>(
        `[data-node-id="${stage.id}"]`,
      );
      if (!node) continue;
      const label = node.querySelector("text[data-node-label]");
      if (label) label.textContent = stage.name;
      node.dataset.status = String(progress[stage.id]);
      node.setAttribute("role", "button");
      node.setAttribute("tabindex", "0");
      node.setAttribute(
        "aria-label",
        `${stage.name} · ${STATUS[progress[stage.id]]} · 상태 변경`,
      );
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
              12,
          ),
        );
        lamp.setAttribute("cy", String(Number(rect.getAttribute("y")) + 12));
        lamp.setAttribute("r", "4");
        lamp.classList.add("lamp");
        node.append(lamp);
      }
      node.addEventListener("click", () => setSelected(stage.id));
      node.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          setSelected(stage.id);
        }
      });
    }
    graphic.querySelectorAll("[data-edge-to]").forEach((edge) => {
      const id = edge.getAttribute("data-edge-to") as StageId;
      if (id in progress)
        edge.setAttribute("data-status", String(progress[id]));
    });
    // Crop only the renderer's outside margin; every node and lane stays in view.
    const boxes = Array.from(
      graphic.querySelectorAll<SVGGraphicsElement>(
        ".c-lane, [data-node-id], [data-edge-to]",
      ),
    ).map((el) => el.getBBox());
    const x = Math.min(...boxes.map((b) => b.x)),
      y = Math.min(...boxes.map((b) => b.y));
    const bounds = {
      x,
      y,
      width: Math.max(...boxes.map((b) => b.x + b.width)) - x,
      height: Math.max(...boxes.map((b) => b.y + b.height)) - y,
    };
    graphic.setAttribute(
      "viewBox",
      `${bounds.x - 20} ${bounds.y - 15} ${bounds.width + 40} ${bounds.height + 30}`,
    );
  }, [svg, progress]);
  async function copy() {
    const url = new URL(location.href);
    url.searchParams.delete("release");
    url.searchParams.set("flow", encodeProgress(progress));
    url.hash = "flow";
    setShare(url.href);
    setCopied(false);
    try {
      await navigator.clipboard.writeText(url.href);
      setCopied(true);
    } catch {}
  }
  const current = STAGES.filter(
    (s) => progress[s.id] === 1 || progress[s.id] === 2,
  );
  return (
    <section className="flow-page">
      <div className="page-heading">
        <div>
          <h2>AI-DLC 활용 개발 진행 순서도</h2>
          <p>박스를 눌러 각 단계의 진행 상태를 표시하세요.</p>
        </div>
        <button className="button" onClick={copy}>
          <LinkIcon size={18} />
          상태 링크 공유
        </button>
      </div>
      <div className="flow-panel">
        <div className="flow-top">
          <div className="current-stages">
            {current.length ? (
              current.map((s) => (
                <button
                  key={s.id}
                  className={`current s${progress[s.id]}`}
                  onClick={() => setSelected(s.id)}
                >
                  <i />
                  {s.name}
                  <span>{STATUS[progress[s.id]]}</span>
                </button>
              ))
            ) : (
              <span className="muted">진행 중인 단계를 선택해 주세요</span>
            )}
          </div>
          <div className="legend">
            {STATUS.map((s, i) => (
              <span key={s}>
                <i className={`s${i}`} />
                {s}
              </span>
            ))}
          </div>
        </div>
        {error ? (
          <p role="alert" className="notice">
            {error}
          </p>
        ) : (
          <div className="flow-canvas flow-expanded" ref={ref} />
        )}
        <button
          className={`qa-crosscut s${progress.q1}`}
          onClick={() => setSelected("q1")}
        >
          <strong>{STAGES.find((s) => s.id === "q1")!.name}</strong>
          <span>전 Construction 과정 횡단 ─────────→</span>
          <b>{STATUS[progress.q1]}</b>
        </button>
        <div className="flow-note">
          <span>
            {storageFailed
              ? "현재 화면에만 표시 · 브라우저 저장 불가"
              : "내 브라우저에 저장 · 팀원에게는 상태 링크로 공유"}
          </span>
          <a
            href={`${import.meta.env.BASE_URL}archify/development.html`}
            target="_blank"
            rel="noreferrer"
          >
            Archify ↗
          </a>
        </div>
      </div>
      {selected && (
        <Modal
          title={STAGES.find((s) => s.id === selected)!.name}
          onClose={() => setSelected(null)}
        >
          <p className="stage-description">
            {STAGES.find((s) => s.id === selected)!.description}
          </p>
          <div
            className="status-picker"
            aria-label="진행 상태 선택"
            role="group"
          >
            {STATUS.map((name, i) => (
              <button
                key={name}
                className={`s${i}`}
                aria-pressed={progress[selected] === i}
                onClick={() => {
                  setProgress((p) => ({ ...p, [selected]: i as StageStatus }));
                  setSelected(null);
                }}
              >
                <i />
                {name}
                {progress[selected] === i && <Check size={18} />}
              </button>
            ))}
          </div>
        </Modal>
      )}
      {share && (
        <Modal
          title={copied ? "상태 링크를 복사했어요" : "상태 링크 공유"}
          onClose={() => setShare("")}
        >
          <p>
            지금 표시한 상태를 전달합니다. 변경 후에는 새 링크를 공유하세요.
          </p>
          <input
            className="share-input"
            aria-label="상태 공유 링크"
            readOnly
            value={share}
            onFocus={(e) => e.target.select()}
          />
        </Modal>
      )}
    </section>
  );
}
