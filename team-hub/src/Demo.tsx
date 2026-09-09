import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  FlaskConical,
  RotateCcw,
  Send,
} from "lucide-react";

import { SCENARIOS, demoCounts, type Scenario, type DemoStep } from "./demoScenarios";

const pause = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function DemoCounter({ value, initial, unit }: { value: number; initial: number; unit: string }) {
  const increased = value > initial;
  return (
    <span key={value} className={`demo-counter ${increased ? "counter-increased" : ""}`} role="status">
      <b>{value}{unit}</b>
      {increased && <em className="counter-gain" aria-label={`${value - initial} 증가`}>+{value - initial}</em>}
    </span>
  );
}

function Turn({ item }: { item: DemoStep }) {
  return (
    <article className="claude-turn">
      {item.prompt && (
        <div className="claude-user">
          <span>❯</span>
          <p>{item.prompt}</p>
        </div>
      )}
      <div className="claude-response">
        <h3 className="demo-step-title">{item.title}</h3>
        {item.answer.slice(0, 1).map((line) => (
          <p key={line}>{line}</p>
        ))}
        {item.tools?.map((tool) => (
          <div
            key={tool.name}
            className={`claude-tool ${tool.tone || ""} ${tool.name.startsWith("SkillLoop.") ? "skillloop-intervention" : ""}`}
          >
            <strong>● {tool.name}</strong>
            {tool.output.map((line) => (
              <code
                className={/20 → 21|0 → 1/.test(line) ? "reuse-highlight" : ""}
                key={line}
              >
                ⎿ {line}
              </code>
            ))}
          </div>
        ))}
        {item.chart && <figure className="demo-result-chart">
          <img src={`${import.meta.env.BASE_URL}evidence/${item.chart}`} alt={item.chart === "p1-cold.png" ? "실제 세 달 생산량 1200, 1350, 1500과 다음달 예상 1650" : "다른 문서 실제 생산량 2100, 2250, 2400과 다음달 예상 2550"} />
          <figcaption>보관한 실제 실행 차트 · 이 화면에서는 재계산하지 않습니다</figcaption>
        </figure>}
        {item.answer.slice(1).map((line) => (
          <p key={line}>{line}</p>
        ))}
      </div>
    </article>
  );
}

export default function Demo({
  initialScenario,
}: {
  initialScenario: Scenario;
}) {
  const [scenario, setScenario] = useState<Scenario>(initialScenario);
  const [completed, setCompleted] = useState(0);
  const [phase, setPhase] = useState<"idle" | "typing" | "answering">("idle");
  const [draft, setDraft] = useState("");
  const runId = useRef(0);
  const busy = phase !== "idle";
  useEffect(() => () => { runId.current += 1; }, []);
  const history = useRef<HTMLDivElement>(null);
  const steps = SCENARIOS[scenario];
  const finished = completed === steps.length;

  useEffect(() => {
    setScenario(initialScenario);
    reset();
  }, [initialScenario]);

  useEffect(() => {
    const panel = history.current;
    const latest = panel?.querySelector<HTMLElement>(".demo-conversation:last-of-type");
    if (panel) panel.scrollTop = latest ? latest.offsetTop - panel.offsetTop : 0;
  }, [completed]);

  const demoState = useMemo(() => demoCounts(scenario, completed), [scenario, completed]);

  function reset() {
    runId.current += 1;
    setPhase("idle");
    setDraft("");
    setCompleted(0);
  }

  function choose(next: Scenario) {
    location.hash = `demo-${next}`;
    setScenario(next);
    reset();
  }

  async function runNext() {
    if (busy || finished) return;
    const token = ++runId.current;
    const item = steps[completed];
    setPhase("typing");
    for (let i = 1; i <= item.prompt.length; i += 1) {
      await pause(24);
      if (token !== runId.current) return;
      setDraft(item.prompt.slice(0, i));
    }
    await pause(500);
    if (token !== runId.current) return;
    setPhase("answering");
    await pause(450);
    if (token !== runId.current) return;
    setCompleted((value) => value + 1);
    setDraft("");
    setPhase("idle");
  }

  function previous() {
    if (busy) return;
    setCompleted((value) => Math.max(value - 1, 0));
  }

  const primaryLabel = finished
    ? scenario === "p0" ? "P1 시연 시작" : "전체 시연 다시 보기"
    : phase === "typing" ? "요청 표시 중…" : phase === "answering" ? "과정 표시 중…" : "다음 단계";

  return (
    <section className="demo-page claude-demo" data-demo-state="memory-only">
      <div className="demo-heading">
        <div>
          <div className="section-kicker">MANUAL SIMULATION</div>
          <h2>Claude Code에서 보는 Agent SkillLoop</h2>
        </div>
        <div className="simulation-badge">
          <FlaskConical size={16} />
          설명용 시뮬레이션
        </div>
      </div>
      <p className="demo-intro">
        실제 구현 흐름을 따라가는 설명용 시연입니다. 다음 단계 버튼은 설명만 진행하며, 설치·게시·실적을 실행하거나 변경하지 않습니다.
      </p>
      <div className="demo-tabs" role="tablist" aria-label="시연 시나리오">
        <button
          role="tab"
          aria-selected={scenario === "p0"}
          onClick={() => choose("p0")}
        >
          <b>P0</b>
          <span>Python 설치 · 기존 Skill 재사용</span>
        </button>
        <button
          role="tab"
          aria-selected={scenario === "p1"}
          onClick={() => choose("p1")}
        >
          <b>P1</b>
          <span>Excel 분석 · 새로운 Skill 발견</span>
        </button>
      </div>

      <div className="demo-storyline">
        {(scenario === "p0"
          ? ["업무 요청", "공급 실패", "팀 경험 적용", "설치 검증·재사용"]
          : ["NO_MATCH·사용자 환경 확인", "탐색·차트·후보", "검토·Replay", "Git 게시·다음 팀원 재사용"]
        ).map((text, i) => (
          <span key={text}>
            {i > 0 && <b>→</b>}
            {text}
          </span>
        ))}
      </div>
      <div className="claude-window">
        <div className="claude-titlebar">
          <div>
            <i />
            <span>Claude Code</span>
            <em>SIMULATION</em>
          </div>
          <div className="claude-window-actions">
            <span>─</span>
            <span>□</span>
            <span>×</span>
          </div>
        </div>
        <div className="claude-sessionbar">
          <div>
            <svg className="claude-mascot" viewBox="0 0 80 56" role="img" aria-label="Claude 마스코트" shapeRendering="crispEdges">
              <path fill="currentColor" d="M10 4h60v16h10v16H68v16h-8V36H48v16h-8V36H28v16h-8V36H10V28H0V16h10Z" />
              <path fill="#201f1c" d="M22 14h7v10h-7zM51 14h7v10h-7z" />
            </svg>
            <div className="claude-identity">
              <strong>Claude Code <small>v2.1.263</small></strong>
            </div>
          </div>
          <div className="claude-progress">
            <span>{scenario.toUpperCase()}</span>
            <b>{completed}</b> / {steps.length}
          </div>
        </div>

        <div className="claude-history" ref={history} aria-live="polite">
          {completed === 0 && (
            <div className="claude-welcome">
              <div className="claude-logo">✻</div>
              <div>
                <strong>Claude Code</strong>
                <span>Agent SkillLoop demo</span>
                <small>업무 요청 뒤 Agent가 해결합니다. 다음 단계로 과정을 확인하세요.</small>
              </div>
            </div>
          )}
          {steps.slice(0, completed).map((item, index) => (
            <div className="demo-conversation" key={index}>
              <Turn item={item} />
            </div>
          ))}
          {finished && (
            <div className="claude-complete">
              <Check size={17} />
              {scenario.toUpperCase()} 시연 완료 · 실제 실행 결과가 아닌 설명용
              상태입니다.
            </div>
          )}
        </div>

        <div className={`claude-composer ${phase}`}>
          <span>❯</span>
          <textarea
            aria-label="Claude Code 프롬프트"
            readOnly
            value={draft}
            placeholder={
              finished
                ? "시연이 완료되었습니다."
                : "다음 단계에서 요청 또는 Agent 진행을 표시합니다"
            }
          />
          <button
            aria-label="다음 단계 보기"
            disabled={busy || finished}
            onClick={runNext}
          >
            <Send size={16} />
          </button>
        </div>
        <div className="claude-statusbar skillloop-terminal-status">
          <div>🧠 SkillLoop · 설명용 현황 | 📚 사용 가능 Skill <DemoCounter value={demoState.available} initial={1} unit="개" /> (기존 로컬 승인 1개 포함)</div>
          <div>✨ 미게시 후보 {demoState.candidates}개 · 이번에 새로 팀 게시 <DemoCounter value={demoState.published} initial={0} unit="개" /></div>
          <div>🔥 실제 검증 재사용 흐름 <DemoCounter value={demoState.reused} initial={0} unit="회" /> · {scenario === "p0" ? "새 후보 0개" : `다음 팀원의 중복 후보 ${demoState.warm ? "0개" : "아직 재사용 전"}`}</div>
          <div className="skillloop-evidence">위 숫자는 설명용 상태 · 실제 로컬/팀 실적 변경 없음</div>
        </div>
      </div>
      <p className="demo-publish-note">
        후보 생성은 게시가 아닙니다. 정확한 내용의 사람 검토와 독립 Replay PASS 뒤 공유하며,
        새 Agent는 가져온 Skill의 실행을 확인받습니다. 현재 P1은 지원된 Excel 접근 어댑터 범위입니다.
      </p>
      <p className="demo-evidence-links">
        실제 실행 기록: <a href="https://github.com/THEGREATCJPark/ddthon/blob/main/result/p0-reproduction/README.md" target="_blank" rel="noreferrer">P0 자연어 3개 사례</a>
        {" · "}<a href="https://github.com/THEGREATCJPark/ddthon/blob/main/result/p1-acceptance/README.md" target="_blank" rel="noreferrer">P1 Cold 3회·Git 공유·Warm</a>
        {" · "}<a href="https://github.com/THEGREATCJPark/ddthon/tree/team-skill-store" target="_blank" rel="noreferrer">실제 공용 Skill 저장소</a>
      </p>

      <div className="demo-controls claude-controls">
        <button
          className="button"
          disabled={busy || completed === 0}
          onClick={previous}
        >
          <ArrowLeft size={17} />
          이전
        </button>
        <button
          className="reset-demo"
          onClick={reset}
        >
          <RotateCcw size={15} />
          처음부터
        </button>
        <span className="demo-boundary-inline">
          실제 Claude·SkillLoop 실행 및 검증 증거가 아닙니다.
        </span>
        <button
          className="button primary claude-next"
          disabled={busy}
          onClick={
            finished ? () => choose(scenario === "p0" ? "p1" : "p0") : runNext
          }
        >
          {primaryLabel}
          {finished ? (
            <ArrowRight size={17} />
          ) : (
            <span className="enter-key">↵</span>
          )}
        </button>
      </div>
    </section>
  );
}
