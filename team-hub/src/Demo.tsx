import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  FlaskConical,
  RotateCcw,
  Send,
} from "lucide-react";

type Scenario = "p0" | "p1";
type ToolRun = { name: string; output: string[]; tone?: "error" | "success" };
type DemoStep = {
  title: string;
  prompt?: string;
  answer: string[];
  tools?: ToolRun[];
};

const P0: DemoStep[] = [
  {
    title: "Proxy 실패",
    prompt: "이 프로젝트의 requirements.txt 설치를 진행해줘.",
    answer: ["필요한 패키지를 일반적인 방법으로 설치해 보겠습니다."],
    tools: [
      {
        name: "Bash(python -m pip install -r requirements.txt)",
        output: ["ProxyError: 사내 Proxy 연결 실패", "exit code 1"],
        tone: "error",
      },
    ],
  },
  {
    title: "Team Skill 발견",
    answer: [
      "현재 사내 환경으로 판단됩니다. 같은 명령을 반복하지 않고 팀에 검증된 해결 방법이 있는지 Agent SkillLoop에서 확인하겠습니다.",
    ],
    tools: [
      {
        name: "SkillLoop.search(error: proxy-error, environment: python)",
        output: [
          "FOUND  Python 사내 패키지 설치 방법",
          "STATUS Published · 적용 조건 일치",
          "시연 기준 적용 20회",
        ],
        tone: "success",
      },
    ],
  },
  {
    title: "Skill 적용·설치 성공",
    answer: [
      "현재 환경에 적용 가능한 Skill입니다. Skill을 활용해 사내 Proxy 설정을 적용하고 설치를 다시 진행합니다.",
    ],
    tools: [
      {
        name: "SkillLoop.apply(Python 사내 패키지 설치 방법)",
        output: ["proxy configuration applied"],
        tone: "success",
      },
      {
        name: "Bash(python -m pip install -r requirements.txt)",
        output: ["Successfully installed requirements", "exit code 0"],
        tone: "success",
      },
    ],
  },
  {
    title: "재사용 20 → 21",
    answer: [
      "설치 결과를 확인했습니다. 검증된 Team Skill 재사용으로 기록합니다.",
      "기존 Team Skill을 재사용해 해결했습니다. 새로운 Skill은 만들지 않고 실제 재사용 횟수만 증가했습니다.",
    ],
    tools: [
      {
        name: "SkillLoop.verify-and-record(Python 사내 패키지 설치 방법)",
        output: ["VERIFY PASS", "verified reuse 20 → 21", "new candidate 0"],
        tone: "success",
      },
    ],
  },
];
const P1: DemoStep[] = [
  {
    title: "Excel 읽기 실패",
    prompt: "AAAAA01_직전_3달_생산량.xlsx 데이터를 읽고 다음달 추세선 보여줘.",
    answer: ["데이터를 확인해 보겠습니다."],
    tools: [
      {
        name: "Read(AAAAA01_직전_3달_생산량.xlsx)",
        output: ["AccessError: 현재 Python parser로 직접 읽을 수 없습니다."],
        tone: "error",
      },
    ],
  },
  {
    title: "xlwings 발견·적재 제안",
    prompt:
      "이상하네. 나는 Excel 앱을 직접 열어서 볼 수 있거든. 데이터를 조회할 다른 방법을 Agent SkillLoop를 이용해서 찾아봐.",
    answer: [
      "기존에 등록된 해결 방법은 없습니다. 현재 Windows 환경에서는 xlwings를 이용해 Excel 앱을 통해 데이터를 읽는 방법으로 작업이 가능합니다.",
      "데이터를 정상적으로 확인할 수 있습니다. 새로 확인한 이 방법을 다른 팀원도 사용할 수 있도록 Skill로 적재하시겠습니까?",
    ],
    tools: [
      {
        name: "SkillLoop.search(environment: excel)",
        output: ["Team Skills   NO MATCH", "Org Knowledge NO MATCH"],
        tone: "error",
      },
      {
        name: "Explore(Excel capabilities)",
        output: ["xlwings + Desktop Excel AVAILABLE"],
        tone: "success",
      },
    ],
  },
  {
    title: "팀 Skill 적재·내 기여 +1",
    prompt: "응, 적재해줘.",
    answer: [
      "동의한 해결 방법을 팀 Skill로 적재합니다. (시연에서는 검토·검증 과정을 축약합니다.)",
      "사내 Excel 데이터 접근 방법 - CJ가 팀 Skill로 적재되었습니다. 다음 Agent는 같은 환경에서 이 방법을 먼저 확인할 수 있습니다.",
    ],
    tools: [
      {
        name: "SkillLoop.add-team-skill(사내 Excel 데이터 접근 방법 - CJ)",
        output: [
          "ADDED  사내 Excel 데이터 접근 방법 - CJ",
          "내 기여 Skill 0 → 1",
        ],
        tone: "success",
      },
    ],
  },
];

// Advance one user prompt and its complete response per click.
const SCENARIOS = { p0: [P0], p1: P1.map((step) => [step]) } as const;

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
  const history = useRef<HTMLDivElement>(null);
  const steps = SCENARIOS[scenario];
  const finished = completed === steps.length;

  useEffect(() => {
    setScenario(initialScenario);
    setCompleted(0);
  }, [initialScenario]);

  useEffect(() => {
    const panel = history.current;
    const latest = panel?.querySelector<HTMLElement>(".demo-conversation:last-of-type");
    if (panel) panel.scrollTop = latest ? latest.offsetTop - panel.offsetTop : 0;
  }, [completed]);

  const demoState = useMemo(
    () => ({
      published: scenario === "p1" && finished ? 2 : 1,
      contributed: scenario === "p1" && finished ? 1 : 0,
      reused: scenario === "p0" && finished ? 1 : 0,
    }),
    [scenario, finished],
  );

  function reset() {
    setCompleted(0);
  }

  function choose(next: Scenario) {
    location.hash = `demo-${next}`;
    setScenario(next);
    setCompleted(0);
  }

  function runNext() {
    setCompleted((value) => Math.min(value + 1, steps.length));
  }

  function previous() {
    setCompleted((value) => Math.max(value - 1, 0));
  }

  const primaryLabel = finished
    ? scenario === "p0" ? "P1 시연 시작" : "전체 시연 다시 보기"
    : "다음 대화";

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
        아이템 이해를 돕기 위한 시연 시나리오입니다. 실제 구현 후 갤러리에 실제
        실행 캡처 화면을 업로드할 예정입니다.
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
          ? [
              "Proxy 실패",
              "Team Skill 발견·적용",
              completed === steps.length
                ? "재사용 20 → 21"
                : "자동 검증·재사용 기록",
            ]
          : [
              "기존 Skill 없음",
              "xlwings 해결법 발견",
              "Skill 적재 제안",
              "내 기여 0 → 1",
            ]
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
            <pre className="claude-pixel" aria-hidden="true">{"▐▛███▛█\n▝▜██████▀\n  ▝▝ ▝▝"}</pre>
            <div className="claude-identity">
              <strong>Claude Code <small>v2.1.263</small></strong>
              <span>claude-luna · API Usage Billing</span>
              <small>~\SkillLoopP1Forecast\workspaces\cj-p1-cold-c882b7</small>
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
                <small>다음 대화를 누르면 프롬프트와 답변을 함께 확인합니다.</small>
              </div>
            </div>
          )}
          {steps.slice(0, completed).map((group, index) => (
            <div className="demo-conversation" key={index}>
              {group.map((item) => <Turn item={item} key={item.title} />)}
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

        <div className="claude-composer">
          <span>❯</span>
          <textarea
            aria-label="Claude Code 프롬프트"
            readOnly
            value=""
            placeholder={
              finished
                ? "시연이 완료되었습니다."
                : "다음 대화로 프롬프트와 답변 보기"
            }
          />
          <button
            aria-label="다음 대화 보기"
            disabled={finished}
            onClick={runNext}
          >
            <Send size={16} />
          </button>
        </div>
        <div className="claude-statusbar skillloop-terminal-status">
          <div>🧠 SkillLoop · 팀 연결 | 📚 '디디톤 기술혁신팀' 공개 Skill <b>{demoState.published}개</b> | cik61</div>
          <div>✨ 내가 기여한 Skill <b>{demoState.contributed}개</b> · 팀에 도움이 될 스킬을 공유해 보세요</div>
          <div>👑 우리팀 스킬 적재왕 : 박찬준 | 🔥 인기 스킬 - python pip 사내환경 적용 방법 - <b>{20 + demoState.reused}회 적용</b></div>
          <div className="skillloop-evidence">데모 기준 20회 + 시뮬레이션 재사용 {demoState.reused}회 · 실제 검증 0회</div>
          <div>⏸ manual mode on · ← for agents <span className="skillloop-simulation">SIMULATION</span></div>
        </div>
      </div>

      {scenario === "p1" && (
        <p className="demo-publish-note">
          시연에서는 적재 과정을 축약해 표시합니다. 실제 구현에서는 사람 검토와
          독립 Replay를 통과한 Skill만 팀에 게시됩니다.
        </p>
      )}
      <div className="demo-controls claude-controls">
        <button
          className="button"
          disabled={completed === 0}
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
