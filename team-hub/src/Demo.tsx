import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronRight,
  FlaskConical,
  RotateCcw,
  Search,
  Sparkles,
  TerminalSquare,
} from "lucide-react";

type Scenario = "p0" | "p1";
type Tone = "user" | "agent" | "command" | "error" | "success" | "note";
type Line = { tone: Tone; label: string; text: string };
type DemoStep = {
  eyebrow: string;
  title: string;
  why: string;
  lines: Line[];
  visual?:
    "search" | "verify" | "count" | "chart" | "candidate" | "replay" | "future";
};

const P0: DemoStep[] = [
  {
    eyebrow: "01 · 요청",
    title: "Python 프로젝트 준비",
    why: "사용자는 평소처럼 업무만 요청합니다.",
    lines: [
      {
        tone: "user",
        label: "사용자",
        text: "이 프로젝트의 requirements.txt 설치를 진행해줘.",
      },
      {
        tone: "agent",
        label: "Agent",
        text: "필요한 패키지를 일반적인 방법으로 설치하겠습니다.",
      },
      {
        tone: "command",
        label: "$",
        text: "python -m pip install -r requirements.txt",
      },
    ],
  },
  {
    eyebrow: "02 · 실패",
    title: "일반 경로에서 설치 실패",
    why: "사내 환경의 제약은 Agent가 반복해서 부딪히는 지점입니다.",
    lines: [
      {
        tone: "error",
        label: "ERROR",
        text: "Could not find a version that satisfies acme-fab-sdk",
      },
      {
        tone: "agent",
        label: "Agent",
        text: "필요한 패키지를 찾지 못했습니다. 현재 환경에 맞는 팀의 해결 경험을 검색하겠습니다.",
      },
    ],
  },
  {
    eyebrow: "03 · 검색",
    title: "팀이 이미 찾은 해결법 발견",
    why: "한 번 검증한 방법을 다음 Agent가 다시 사용합니다.",
    lines: [
      {
        tone: "command",
        label: "SkillLoop",
        text: "현재 실패 원인과 적용 조건 비교 중…",
      },
      {
        tone: "success",
        label: "FOUND",
        text: "Python 사내 패키지 설치 방법 · Published Team Skill",
      },
      {
        tone: "note",
        label: "적용 조건",
        text: "일반 패키지 공급 경로에 필요한 사내 의존성이 없는 경우",
      },
    ],
    visual: "search",
  },
  {
    eyebrow: "04 · 적용",
    title: "검증된 절차로 설치",
    why: "실제 사내 주소나 인증정보는 시연에 포함하지 않습니다.",
    lines: [
      {
        tone: "command",
        label: "1",
        text: "승인된 사내 모의 package source 적용",
      },
      { tone: "command", label: "2", text: "pip install acme-fab-sdk" },
      {
        tone: "success",
        label: "OK",
        text: "Successfully installed acme-fab-sdk",
      },
      {
        tone: "agent",
        label: "Agent",
        text: "설치는 성공했습니다. 요청이 제대로 끝났는지 별도로 확인하겠습니다.",
      },
    ],
  },
  {
    eyebrow: "05 · 검증",
    title: "업무와 해결 능력을 각각 확인",
    why: "검색이나 재시도가 아니라 실제로 도움이 된 경우만 재사용으로 셉니다.",
    lines: [
      {
        tone: "success",
        label: "PASS",
        text: "요청한 패키지 설치와 import 확인",
      },
      {
        tone: "success",
        label: "PASS",
        text: "현재 환경에서 승인된 합성 source 사용 확인",
      },
    ],
    visual: "verify",
  },
  {
    eyebrow: "06 · 조직 학습",
    title: "다음 Agent는 여기서 시작합니다",
    why: "기존 해결법이 실제 업무를 끝냈을 때 조직의 재사용 경험이 하나 늘어납니다.",
    lines: [
      {
        tone: "agent",
        label: "Agent",
        text: "검증된 Team Skill 재사용으로 기록했습니다.",
      },
      {
        tone: "note",
        label: "원칙",
        text: "검색 · 다운로드 · 실패 · retry는 적용 횟수가 아닙니다.",
      },
    ],
    visual: "count",
  },
];

const P1: DemoStep[] = [
  {
    eyebrow: "01 · 요청",
    title: "Excel 데이터 분석 요청",
    why: "팀에도 아직 해결법이 없는 상황에서 시작합니다.",
    lines: [
      {
        tone: "user",
        label: "사용자",
        text: "합성 생산량.xlsx를 읽고 다음 달 예상치를 포함한 추세를 보여줘.",
      },
      {
        tone: "agent",
        label: "Agent",
        text: "최근 세 달의 값을 읽고 다음 달을 예측하겠습니다.",
      },
    ],
  },
  {
    eyebrow: "02 · 제약 발견",
    title: "직접 파일 읽기 실패",
    why: "실제 보호체계를 재현하거나 우회하는 장면이 아닙니다.",
    lines: [
      { tone: "command", label: "$", text: "openpyxl · 직접 parser 접근" },
      {
        tone: "error",
        label: "AccessError",
        text: "protected workbook cannot be read through direct parser",
      },
      {
        tone: "note",
        label: "환경",
        text: "사내 보호문서와 유사한 합성 제약 환경",
      },
    ],
  },
  {
    eyebrow: "03 · 기존 지식 검색",
    title: "아직 팀에도 답이 없음",
    why: "실제 검색 결과가 없을 때만 새로운 해결 탐색을 시작합니다.",
    lines: [
      { tone: "error", label: "Team Skills", text: "NO MATCH" },
      { tone: "error", label: "Org Knowledge", text: "NO MATCH" },
      {
        tone: "user",
        label: "사용자",
        text: "나는 Excel에서 내용을 볼 수 있어. 다른 안전한 방법을 찾아봐.",
      },
    ],
  },
  {
    eyebrow: "04 · 환경 탐색",
    title: "읽기 가능한 경로 발견",
    why: "특정 라이브러리보다 이 환경에서 유효했던 접근 절차가 학습 대상입니다.",
    lines: [
      {
        tone: "command",
        label: "CHECK",
        text: "Windows 환경 → Desktop Excel 사용 가능",
      },
      {
        tone: "command",
        label: "CHECK",
        text: "application-mediated read-only access 탐색",
      },
      {
        tone: "success",
        label: "FOUND",
        text: "Excel 앱을 통한 read-only values 접근",
      },
      {
        tone: "note",
        label: "예시",
        text: "xlwings / Excel COM은 가능한 구현 중 하나입니다.",
      },
    ],
  },
  {
    eyebrow: "05 · 업무 완료",
    title: "실제값과 예상값을 구분",
    why: "접근 성공만으로 끝내지 않고 사용자가 요청한 결과까지 완성합니다.",
    lines: [
      {
        tone: "success",
        label: "READ",
        text: "7월 100 · 8월 110 · 9월 120 units",
      },
      {
        tone: "agent",
        label: "Agent",
        text: "세 완료 월을 기준으로 10월 예상값 130 units를 계산했습니다.",
      },
      { tone: "note", label: "계산", text: "3점 OLS · x=1,2,3 → x=4" },
    ],
    visual: "chart",
  },
  {
    eyebrow: "06 · Candidate",
    title: "업무 데이터는 빼고 해결 절차만",
    why: "이번 업무의 답이 아니라 다시 쓸 수 있는 환경 해결 경험을 남깁니다.",
    lines: [
      {
        tone: "agent",
        label: "SkillLoop",
        text: "Team Skill 후보를 만들었습니다. 아직 Published 상태는 아닙니다.",
      },
    ],
    visual: "candidate",
  },
  {
    eyebrow: "07 · 검토와 Replay",
    title: "승인한 그대로 다시 검증",
    why: "한 번 우연히 된 방법을 곧바로 조직의 Skill로 만들지 않습니다.",
    lines: [
      {
        tone: "success",
        label: "Human Review",
        text: "시연: Candidate digest exact match · APPROVED",
      },
      {
        tone: "success",
        label: "Replay",
        text: "시연: 다른 합성 workbook에서 TASK / CAPABILITY PASS",
      },
    ],
    visual: "replay",
  },
  {
    eyebrow: "08 · 다음 팀원",
    title: "다음 Agent는 처음부터 찾지 않습니다",
    why: "새 해결 경험이 게시되고, 다음 업무에서는 기존 Skill로 재사용됩니다.",
    lines: [
      {
        tone: "success",
        label: "PUBLISHED · 시연",
        text: "보호문서 환경의 read-only 값 접근 절차",
      },
      {
        tone: "user",
        label: "며칠 뒤",
        text: "이 합성 보호 Excel 데이터를 읽어서 분석해줘.",
      },
      {
        tone: "agent",
        label: "다른 Agent",
        text: "팀에서 검증한 절차가 현재 환경에도 적용 가능합니다. 이 Skill로 진행하겠습니다.",
      },
      {
        tone: "success",
        label: "SUCCESS",
        text: "업무 완료 · 새 Candidate 0개",
      },
    ],
    visual: "future",
  },
];

const SCENARIOS = { p0: P0, p1: P1 } as const;

function StepVisual({ kind }: { kind: DemoStep["visual"] }) {
  if (!kind) return null;
  if (kind === "search")
    return (
      <div className="demo-card skill-card">
        <Search size={20} />
        <div>
          <strong>Python 사내 패키지 설치 방법</strong>
          <span>Published · 적용 조건 일치 · 시연 기준 20회</span>
        </div>
      </div>
    );
  if (kind === "verify")
    return (
      <div className="verify-grid">
        <span>
          <Check />
          TASK VERIFY<strong>PASS</strong>
        </span>
        <span>
          <Check />
          CAPABILITY VERIFY<strong>PASS</strong>
        </span>
      </div>
    );
  if (kind === "count")
    return (
      <div className="count-change">
        <div>
          <span>시연상 검증 재사용</span>
          <strong>0</strong>
        </div>
        <ChevronRight />
        <div className="changed">
          <span>시연상 검증 재사용</span>
          <strong>1</strong>
        </div>
      </div>
    );
  if (kind === "chart")
    return (
      <div className="mini-chart" aria-label="7월부터 10월 예상 생산량 추세">
        <div className="chart-bars">
          {[100, 110, 120, 130].map((v, i) => (
            <div key={v} className={i === 3 ? "forecast" : ""}>
              <span style={{ height: `${v - 55}px` }} />
              <strong>{v}</strong>
              <small>
                {7 + i}월{i === 3 ? " 예상" : ""}
              </small>
            </div>
          ))}
        </div>
      </div>
    );
  if (kind === "candidate")
    return (
      <div className="candidate-card">
        <strong>보호문서 환경의 read-only 값 접근</strong>
        <div>
          <span>포함</span> 적용 조건 · 접근 절차 · 검증 근거
        </div>
        <div className="excluded">
          <span>제외</span> 생산량 · 파일 경로 · 암호 · 예측 로직
        </div>
      </div>
    );
  if (kind === "replay")
    return (
      <div className="lifecycle">
        <span>Candidate</span>
        <i>→</i>
        <span>Human Review</span>
        <i>→</i>
        <span className="active">Replay PASS</span>
      </div>
    );
  if (kind === "future")
    return (
      <div className="future-cards">
        <div>
          <b>P0</b>
          <strong>이미 아는 문제</strong>
          <span>즉시 재사용</span>
        </div>
        <div>
          <b>P1</b>
          <strong>처음 보는 문제</strong>
          <span>검증 후 조직 자산</span>
        </div>
      </div>
    );
  return null;
}

export default function Demo({
  initialScenario,
}: {
  initialScenario: Scenario;
}) {
  const [scenario, setScenario] = useState<Scenario>(initialScenario);
  const [step, setStep] = useState(0);
  useEffect(() => {
    setScenario(initialScenario);
    setStep(0);
  }, [initialScenario]);
  const steps = SCENARIOS[scenario];
  const current = steps[step];
  const demoState = useMemo(
    () => ({
      published: scenario === "p1" && step >= 7 ? 2 : 1,
      contributed: scenario === "p1" && step >= 7 ? 1 : 0,
      verifiedReuse: scenario === "p0" && step >= 5 ? 1 : 0,
    }),
    [scenario, step],
  );
  function choose(next: Scenario) {
    location.hash = `demo-${next}`;
    setScenario(next);
    setStep(0);
  }
  return (
    <section className="demo-page" data-demo-state="memory-only">
      <div className="demo-heading">
        <div>
          <div className="section-kicker">INTERACTIVE DEMO</div>
          <h2>Agent SkillLoop 동작 시연</h2>
          <p>한 Agent가 겪은 시행착오를, 다음 Agent는 반복하지 않습니다.</p>
        </div>
        <div className="simulation-badge">
          <FlaskConical size={16} />
          설명용 시뮬레이션
        </div>
      </div>
      <p className="demo-boundary">
        제품 흐름을 설명하기 위한 인터랙티브 시뮬레이션입니다. 실제 검증 결과는
        별도 실행 증거를 확인하세요.
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
      <div className="demo-shell">
        <div className="demo-toolbar">
          <div className="terminal-title">
            <TerminalSquare size={18} />
            <span>
              {scenario.toUpperCase()} ·{" "}
              {scenario === "p0" ? "이미 해결한 문제" : "처음 만난 문제"}
            </span>
          </div>
          <div className="step-count">
            STEP <strong>{step + 1}</strong> / {steps.length}
          </div>
        </div>
        <div className="demo-content">
          <aside className="demo-timeline">
            {steps.map((s, i) => (
              <button
                key={s.title}
                className={i === step ? "active" : i < step ? "complete" : ""}
                onClick={() => setStep(i)}
              >
                <i>{i < step ? <Check size={13} /> : i + 1}</i>
                <span>{s.title}</span>
              </button>
            ))}
          </aside>
          <div className="terminal">
            <div className="terminal-dots">
              <i />
              <i />
              <i />
              <span>agent-skillloop — simulation</span>
            </div>
            <div className="terminal-stage" key={`${scenario}-${step}`}>
              <div className="terminal-copy">
                <span className="terminal-eyebrow">{current.eyebrow}</span>
                <h3>{current.title}</h3>
                <div className="terminal-lines">
                  {current.lines.map((line, i) => (
                    <div
                      className={`terminal-line ${line.tone}`}
                      key={`${line.label}-${i}`}
                    >
                      <span>{line.label}</span>
                      <p>{line.text}</p>
                    </div>
                  ))}
                </div>
              </div>
              <StepVisual kind={current.visual} />
            </div>
            <div className="why">
              <Sparkles size={16} />
              <span>왜 중요한가</span>
              <p>{current.why}</p>
            </div>
          </div>
        </div>
        <div className="skillloop-bar">
          <div>
            <span>🧠 SkillLoop · 노웨어</span>
            <span>
              📚 시연 Skill{" "}
              <strong className={demoState.published > 1 ? "flash" : ""}>
                {demoState.published}개
              </strong>
            </span>
            <span>
              시연 기여{" "}
              <strong className={demoState.contributed ? "flash" : ""}>
                {demoState.contributed}개
              </strong>
            </span>
          </div>
          <div>
            <span>인기 Skill · Python 사내 패키지 설치 방법</span>
            <span>
              시연 기준 20회 + 검증 재사용{" "}
              <strong className={demoState.verifiedReuse ? "flash" : ""}>
                {demoState.verifiedReuse}회
              </strong>
            </span>
          </div>
        </div>
      </div>
      <div className="demo-controls">
        <button
          className="button"
          disabled={step === 0}
          onClick={() => setStep((v) => v - 1)}
        >
          <ArrowLeft size={17} />
          이전
        </button>
        <button className="reset-demo" onClick={() => setStep(0)}>
          <RotateCcw size={15} />
          처음부터
        </button>
        {step === steps.length - 1 && scenario === "p0" ? (
          <button className="button primary" onClick={() => choose("p1")}>
            P1 · 새로운 Skill 발견 보기
            <ArrowRight size={17} />
          </button>
        ) : step === steps.length - 1 ? (
          <button
            className="button primary"
            onClick={() => {
              choose("p0");
            }}
          >
            전체 시연 다시 보기
            <RotateCcw size={16} />
          </button>
        ) : (
          <button
            className="button primary"
            onClick={() => setStep((v) => v + 1)}
          >
            다음
            <ArrowRight size={17} />
          </button>
        )}
      </div>
    </section>
  );
}
