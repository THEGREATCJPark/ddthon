import {
  ArrowRight,
  Database,
  FolderCheck,
  RefreshCw,
  Search,
  ShieldCheck,
} from "lucide-react";

const SOURCE = "https://github.com/THEGREATCJPark/ddthon/blob/0041d87";
const steps = [
  {
    title: "사내 가상환경을 구축했어요.",
    icon: ShieldCheck,
    body: "일반 경로로 설치되지 않는 패키지, Excel에서는 열리지만 AI가 직접 읽지 못하는 문서. 사내에서 겪는 제약을 합성 데이터와 가상 환경으로 재현했습니다.",
    flow: ["패키지 공급 제약", "문서 접근 제약", "실제 실패 재현"],
    question: "Q6 · 환경 제약 재현",
    answer: "A",
    quote:
      "로컬 공개환경 모의 index에는 패키지를 두지 않고 허용된 사내 모의 index에만 무해한 wheel을 두어 실제 pip 실패→Skill 적용→성공을 통제된 환경에서 재현.",
  },
  {
    title: "조직 Skill Storage를 구축했어요.",
    icon: Database,
    body: "해결 방법을 적용 조건·절차·버전과 함께 저장하고 GitHub로 공유합니다. 개인 대화에 남던 경험을 다른 Agent가 찾아 쓸 수 있게 했습니다.",
    flow: ["해결 절차 저장", "버전·내용 확인", "조직 공유"],
    question: "Q4 · Skill 표현 형태",
    answer: "C",
    quote:
      "version/digest/origin/applicability/절차를 하나의 구조화된 descriptor로 관리하면 동기화·무결성 검사·충돌 판정이 단순하며 실행 스크립트 자체를 공유하지 않아도 됩니다.",
  },
  {
    title: "이미 푼 문제는 조직 Skill로 해결해요.",
    icon: Search,
    body: "“이 프로젝트의 패키지를 설치해줘.” 설치가 막히면 Agent가 기존 Skill을 찾아 적용합니다. 설치·버전·실제 사용 가능 여부를 확인한 뒤 성공한 재사용만 기록합니다.",
    flow: ["설치 실패", "Skill 검색·적용", "검증 성공 · 재사용 +1"],
    question: "Q9 · 사용 실적 기준",
    answer: "A, C",
    quote:
      "검증된 실제 Skill 적용 성공만 actual reuse +1, 실패·검색·Replay·retry·sync 미집계, 초기 DEMO_SEED 이력은 실제 성공 증가분과 구분 표시.",
    scenario: "P0 · 기존 경험 재사용",
  },
  {
    title: "처음 만난 문제는 LOOP를 통해 해결해요.",
    icon: RefreshCw,
    body: "“이 Excel로 다음달 예상 생산량을 보여줘.” 맞는 Skill이 없다면 사용자에게서 환경 사실을 듣고, 접근 방법을 탐색하고 실행 결과를 확인합니다. 이 과정을 거쳐 데이터를 읽고 차트를 완성합니다.",
    flow: ["문제 관찰", "환경 확인·탐색", "실행·검증 ↺"],
    question: "Q7 · 문서 접근 대안",
    answer: "C",
    quote:
      "보호된 합성 XLSX 직접 parser 접근은 실제 실패시키되 정답 라이브러리를 고정하지 않고 Agent가 Windows에서 허용된 read-only 대안 절차를 찾아 완료.",
    scenario: "P1 · 새로운 해결 경험",
  },
  {
    title: "LOOP로 해결한 문제는 조직을 위해 Skill로 적재해요.",
    icon: FolderCheck,
    body: "업무를 해결하며 발견한 환경 접근 절차를 Skill 후보로 남깁니다. 사람이 내용을 검토하고 다른 문서에서 독립적으로 재실행한 뒤 조직 저장소에 게시합니다. 다음 Agent는 이 Skill을 받아 같은 시행착오를 줄일 수 있습니다.",
    flow: [
      "해결 절차 후보화",
      "사람 검토",
      "독립 Replay",
      "조직 게시",
      "다음 Agent 재사용",
    ],
    question: "Q8 · 새 Skill의 완료 기준",
    answer: "B",
    quote:
      "후보 생성이 아니라 사람 검토 + 독립 Replay + 게시까지의 loop 실제 수행 목표.",
    scenario: "해결 경험 → 조직의 자산",
  },
];

export default function Overview() {
  return (
    <section className="overview-page">
      <div className="overview-section-title">
        <div>
          <span className="overview-eyebrow">BUILT DURING THE HACKATHON</span>
          <h2>해커톤 동안 우리가 만든 것</h2>
        </div>
        <a href="#flow">
          개발 진행 순서도 <ArrowRight size={16} />
        </a>
      </div>
      <div className="overview-grid">
        {steps.map((step, index) => (
          <article className="overview-card" key={step.title}>
            <div className="overview-card-top">
              <span>{String(index + 1).padStart(2, "0")}</span>
              <step.icon size={24} />
            </div>
            {step.scenario && (
              <span className="overview-scenario">{step.scenario}</span>
            )}
            <h3>{step.title}</h3>
            <p>{step.body}</p>
            <div className="overview-step-flow">
              {step.flow.map((label, i) => (
                <span key={label}>
                  {i > 0 && <ArrowRight size={14} />}
                  <b>{label}</b>
                </span>
              ))}
            </div>
            <div className="overview-evidence">
              <span>AI-DLC 문답 원문 · {step.question}</span>
              <blockquote><strong>답변 {step.answer} — </strong>{step.quote}</blockquote>
              <a
                href={`${SOURCE}/aidlc-docs/audit.md`}
                target="_blank"
                rel="noreferrer"
              >
                사용자 답변 원문 보기 ↗
              </a>
            </div>
          </article>
        ))}
      </div>
      <div className="overview-records">
        <div>
          <h3>설명에서 끝내지 않고, 실행 기록으로 남겼어요.</h3>
          <p>
            패키지 설치와 Excel 접근을 대상으로 구현한 MVP입니다. 가상
            환경에서의 실제 실행·차트·Git 공유 기록을 확인할 수 있습니다.
          </p>
        </div>
        <div>
          <a
            href={`${SOURCE}/result/p0-reproduction/README.md`}
            target="_blank"
            rel="noreferrer"
          >
            P0 실행 근거 ↗
          </a>
          <a
            href={`${SOURCE}/result/p1-acceptance/README.md`}
            target="_blank"
            rel="noreferrer"
          >
            P1 해결·공유·재사용 근거 ↗
          </a>
          <a href="#challenge">태클 남기기 →</a>
        </div>
      </div>
    </section>
  );
}
