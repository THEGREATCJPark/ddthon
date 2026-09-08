import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronDown,
  FlaskConical,
  RotateCcw,
  Send,
} from "lucide-react";

type Scenario = "p0" | "p1";
type Phase = "idle" | "typing" | "running";
type ToolRun = { name: string; output: string[]; tone?: "error" | "success" };
type DemoStep = {
  title: string;
  prompt: string;
  answer: string[];
  tool?: ToolRun;
};

const P0: DemoStep[] = [
  {
    title: "일반 설치 시도",
    prompt: "이 프로젝트의 requirements.txt 설치를 진행해줘.",
    answer: [
      "필요한 패키지를 일반적인 방법으로 설치해 보겠습니다.",
      "일반 공급 경로에는 필요한 사내 의존성이 없습니다. 같은 명령을 반복하지 않고 팀의 해결 경험을 확인하겠습니다.",
    ],
    tool: {
      name: "Bash(python -m pip install -r requirements.txt)",
      output: [
        "ERROR: Could not find a version that satisfies acme-fab-sdk",
        "exit code 1",
      ],
      tone: "error",
    },
  },
  {
    title: "Team Skill 검색",
    prompt: "팀에서 이미 해결한 설치 방법이 있는지 SkillLoop에서 찾아봐.",
    answer: [
      "현재 오류와 적용 조건이 일치하는 Team Skill을 찾았습니다.",
      "검색된 항목은 설명용 합성 데이터이며 실제 사내 주소나 인증정보를 포함하지 않습니다.",
    ],
    tool: {
      name: "SkillLoop.search(environment: python, error: dependency-not-found)",
      output: [
        "FOUND  Python 사내 패키지 설치 방법",
        "STATUS Published · 적용 조건 일치 · 시연 기준 20회",
      ],
      tone: "success",
    },
  },
  {
    title: "적용 조건 확인",
    prompt: "찾은 Skill이 지금 환경에 적용 가능한지 먼저 확인해줘.",
    answer: [
      "운영체제, 프로젝트 유형, 실패 원인을 비교했습니다.",
      "현재 합성 환경은 Skill의 적용 조건과 일치합니다. 승인된 모의 package source만 사용하겠습니다.",
    ],
    tool: {
      name: "SkillLoop.check-applicability(team/python-package-install)",
      output: ["OS windows · source unavailable · MATCH", "secrets exposed 0"],
      tone: "success",
    },
  },
  {
    title: "검증된 절차 적용",
    prompt: "검증된 절차를 적용해서 설치를 완료해줘.",
    answer: ["Team Skill의 절차를 적용했습니다. 패키지 설치가 완료되었습니다."],
    tool: {
      name: "Bash(pip install acme-fab-sdk --index-url [approved-demo-source])",
      output: ["Successfully installed acme-fab-sdk", "exit code 0"],
      tone: "success",
    },
  },
  {
    title: "업무와 능력 검증",
    prompt: "설치 결과와 Skill이 실제로 도움 됐는지 각각 검증해줘.",
    answer: [
      "요청한 업무와 재사용한 해결 능력을 분리해 확인했습니다.",
      "검색, 다운로드, 실패, retry는 재사용 실적으로 세지 않습니다.",
    ],
    tool: {
      name: "SkillLoop.verify(task, capability)",
      output: [
        "TASK VERIFY       PASS · package import",
        "CAPABILITY VERIFY PASS · approved demo source",
      ],
      tone: "success",
    },
  },
  {
    title: "검증 재사용 기록",
    prompt: "검증된 재사용만 기록하고 다음 팀원이 바로 쓸 수 있게 정리해줘.",
    answer: [
      "검증된 Team Skill 재사용을 시연 상태에 기록했습니다.",
      "다음 Agent는 같은 실패를 처음부터 조사하지 않고 이 적용 조건부터 확인합니다.",
    ],
    tool: {
      name: "SkillLoop.record-verified-reuse(team/python-package-install)",
      output: ["verified reuse  0 → 1", "new candidate   0"],
      tone: "success",
    },
  },
];

const P1: DemoStep[] = [
  {
    title: "합성 Excel 분석 요청",
    prompt: "합성 생산량.xlsx를 읽고 다음 달 예상치를 포함한 추세를 보여줘.",
    answer: ["최근 세 달의 값을 읽어 다음 달 예상치를 계산해 보겠습니다."],
    tool: {
      name: "Read(합성 생산량.xlsx)",
      output: [
        "AccessError: direct parser cannot read protected workbook",
        "사내 보호문서와 유사한 합성 제약 환경",
      ],
      tone: "error",
    },
  },
  {
    title: "기존 지식 검색",
    prompt: "팀이나 조직에 이미 검증된 해결 방법이 있는지 찾아봐.",
    answer: [
      "현재 실패 조건과 일치하는 기존 지식이 없습니다. 새로운 해결 경로를 탐색하겠습니다.",
    ],
    tool: {
      name: "SkillLoop.search(environment: protected-workbook)",
      output: ["Team Skills   NO MATCH", "Org Knowledge NO MATCH"],
      tone: "error",
    },
  },
  {
    title: "안전한 경로 탐색",
    prompt:
      "나는 Excel 앱에서 볼 수 있어. 우회하지 말고 읽기 가능한 안전한 경로를 찾아봐.",
    answer: [
      "Desktop Excel을 통한 application-mediated read-only 접근이 가능합니다.",
      "특정 보호체계를 우회하지 않고 사용자가 이미 열람 가능한 합성 값만 읽습니다.",
    ],
    tool: {
      name: "Explore(environment-capabilities)",
      output: [
        "Windows Desktop Excel  AVAILABLE",
        "read-only values access  AVAILABLE",
      ],
      tone: "success",
    },
  },
  {
    title: "업무 결과 완성",
    prompt: "그 경로로 값을 읽고 실제값과 예상값을 구분해서 보여줘.",
    answer: [
      "완료 월은 7월 100, 8월 110, 9월 120 units입니다.",
      "3점 OLS 기준 10월 예상값은 130 units이며 예상값으로 따로 표시했습니다.",
    ],
    tool: {
      name: "Excel(read-only) → Analyze(3-point OLS)",
      output: ["JUL 100  AUG 110  SEP 120", "OCT 130  [FORECAST]"],
      tone: "success",
    },
  },
  {
    title: "TASK / CAPABILITY 검증",
    prompt: "분석 결과와 새 접근 방법을 서로 분리해서 검증해줘.",
    answer: ["사용자 업무 결과와 환경 접근 능력을 각각 확인했습니다."],
    tool: {
      name: "SkillLoop.verify(task, capability)",
      output: [
        "TASK VERIFY       PASS · trend and forecast",
        "CAPABILITY VERIFY PASS · application-mediated read-only",
      ],
      tone: "success",
    },
  },
  {
    title: "Candidate 생성",
    prompt:
      "업무 데이터는 빼고 다시 쓸 수 있는 환경 해결 절차만 후보로 만들어줘.",
    answer: [
      "Team Skill Candidate를 만들었습니다. 생산량, 파일 경로, 암호, 예측 로직은 제외했습니다.",
      "아직 Published 상태가 아니며 사람의 검토가 필요합니다.",
    ],
    tool: {
      name: "SkillLoop.create-candidate(read-only-workbook-access)",
      output: [
        "included  적용 조건 · 접근 절차 · 검증 근거",
        "excluded  business data · paths · secrets",
      ],
      tone: "success",
    },
  },
  {
    title: "검토와 독립 Replay",
    prompt: "평가 담당자가 승인한 그대로 다른 합성 workbook에서 Replay 해줘.",
    answer: [
      "시연용 Human Review와 독립 Replay가 완료되었습니다.",
      "승인된 Candidate digest와 Replay 대상이 정확히 일치합니다.",
    ],
    tool: {
      name: "SkillLoop.replay(candidate-digest: exact-match)",
      output: [
        "HUMAN REVIEW  APPROVED [SIMULATION]",
        "REPLAY TASK / CAPABILITY  PASS [SIMULATION]",
      ],
      tone: "success",
    },
  },
  {
    title: "게시와 다음 재사용",
    prompt: "검증된 절차를 게시하고 다음 Agent가 어떻게 쓰는지 보여줘.",
    answer: [
      "시연용 Team Skill이 게시되었습니다.",
      "다음 Agent는 같은 제약에서 처음부터 탐색하지 않고 적용 조건을 확인한 뒤 재사용합니다.",
    ],
    tool: {
      name: "SkillLoop.publish → teammate reuse",
      output: [
        "PUBLISHED [SIMULATION]  보호문서 환경의 read-only 값 접근",
        "next task  SUCCESS · new candidate 0",
      ],
      tone: "success",
    },
  },
];

const SCENARIOS = { p0: P0, p1: P1 } as const;
const pause = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function Turn({ item }: { item: DemoStep }) {
  return (
    <article className="claude-turn">
      <div className="claude-user">
        <span>❯</span>
        <p>{item.prompt}</p>
      </div>
      <div className="claude-response">
        {item.answer.slice(0, 1).map((line) => (
          <p key={line}>{line}</p>
        ))}
        {item.tool && (
          <div className={`claude-tool ${item.tool.tone || ""}`}>
            <strong>● {item.tool.name}</strong>
            {item.tool.output.map((line) => (
              <code key={line}>⎿ {line}</code>
            ))}
          </div>
        )}
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
  const [phase, setPhase] = useState<Phase>("idle");
  const [draft, setDraft] = useState("");
  const runId = useRef(0);
  useEffect(
    () => () => {
      runId.current += 1;
    },
    [],
  );
  const history = useRef<HTMLDivElement>(null);
  const steps = SCENARIOS[scenario];
  const current = steps[Math.min(completed, steps.length - 1)];
  const finished = completed === steps.length;

  useEffect(() => {
    runId.current += 1;
    setScenario(initialScenario);
    setCompleted(0);
    setPhase("idle");
    setDraft("");
  }, [initialScenario]);

  useEffect(() => {
    history.current?.scrollTo({
      top: history.current.scrollHeight,
      behavior: "smooth",
    });
  }, [completed, phase]);

  const demoState = useMemo(
    () => ({
      published: scenario === "p1" && finished ? 2 : 1,
      contributed: scenario === "p1" && finished ? 1 : 0,
      reused: scenario === "p0" && finished ? 1 : 0,
    }),
    [scenario, finished],
  );

  function reset() {
    runId.current += 1;
    setCompleted(0);
    setPhase("idle");
    setDraft("");
  }

  function choose(next: Scenario) {
    runId.current += 1;
    location.hash = `demo-${next}`;
    setScenario(next);
    setCompleted(0);
    setPhase("idle");
    setDraft("");
  }

  async function runNext() {
    if (phase !== "idle" || finished) return;
    const token = ++runId.current;
    setPhase("typing");
    setDraft("");
    for (let i = 1; i <= current.prompt.length; i += 1) {
      await pause(13);
      if (token !== runId.current) return;
      setDraft(current.prompt.slice(0, i));
    }
    await pause(260);
    if (token !== runId.current) return;
    setDraft("");
    setPhase("running");
    await pause(820);
    if (token !== runId.current) return;
    setCompleted((value) => value + 1);
    setPhase("idle");
  }

  function previous() {
    if (phase !== "idle" || completed === 0) return;
    setCompleted((value) => value - 1);
  }

  const primaryLabel = finished
    ? scenario === "p0"
      ? "P1 시연 시작"
      : "전체 시연 다시 보기"
    : phase === "typing"
      ? "프롬프트 입력 중…"
      : phase === "running"
        ? "Claude 작업 중…"
        : completed === 0
          ? "첫 프롬프트 입력"
          : "다음 프롬프트 입력";

  return (
    <section className="demo-page claude-demo" data-demo-state="memory-only">
      <div className="demo-heading">
        <div>
          <div className="section-kicker">LIVE SIMULATION</div>
          <h2>Claude Code에서 보는 Agent SkillLoop</h2>
        </div>
        <div className="simulation-badge">
          <FlaskConical size={16} />
          설명용 시뮬레이션
        </div>
      </div>
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
            <span className="claude-mark">✻</span>
            <strong>Agent SkillLoop</strong>
            <small>~/nowhere/agent-skillloop</small>
          </div>
          <div className="claude-progress">
            <span>{scenario.toUpperCase()}</span>
            <b>{completed}</b> / {steps.length}
          </div>
        </div>

        <div className="claude-history" ref={history} aria-live="polite">
          {completed === 0 && phase === "idle" && (
            <div className="claude-welcome">
              <div className="claude-logo">✻</div>
              <div>
                <strong>Claude Code</strong>
                <span>Agent SkillLoop demo</span>
                <small>다음을 누르면 프롬프트가 입력되고 실행됩니다.</small>
              </div>
            </div>
          )}
          {steps.slice(0, completed).map((item) => (
            <Turn item={item} key={item.title} />
          ))}
          {phase === "running" && (
            <article className="claude-turn pending">
              <div className="claude-user">
                <span>❯</span>
                <p>{current.prompt}</p>
              </div>
              <div className="claude-thinking">
                <i />
                Working… <small>{current.title}</small>
              </div>
            </article>
          )}
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
                : "다음을 눌러 프롬프트를 입력하세요"
            }
          />
          <button
            aria-label="프롬프트 실행"
            disabled={phase !== "idle" || finished}
            onClick={runNext}
          >
            <Send size={16} />
          </button>
        </div>
        <div className="claude-statusbar">
          <div>
            <span>🧠 SkillLoop · 팀 연결</span>
            <span>
              📚 시연 Skill <b>{demoState.published}개</b>
            </span>
            <span>
              내 기여 <b>{demoState.contributed}개</b>
            </span>
          </div>
          <div>
            <span>
              검증 재사용 <b>{demoState.reused}회</b>
            </span>
            <span>
              Claude Sonnet 4 <ChevronDown size={12} />
            </span>
          </div>
        </div>
      </div>

      <div className="demo-controls claude-controls">
        <button
          className="button"
          disabled={phase !== "idle" || completed === 0}
          onClick={previous}
        >
          <ArrowLeft size={17} />
          이전
        </button>
        <button
          className="reset-demo"
          disabled={phase !== "idle"}
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
          disabled={phase !== "idle"}
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
