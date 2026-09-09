export type Scenario = "p0" | "p1";
type ToolRun = { name: string; output: string[]; tone?: "error" | "success" };
export type DemoStep = {
  title: string;
  prompt: string;
  answer: string[];
  tools?: ToolRun[];
  chart?: string;
  event?: "candidate" | "review" | "replay" | "publish" | "reuse";
};

const P0: DemoStep[] = [
  { title: "현재 프로젝트에서 설치 시도", prompt: "이 프로젝트 requirements.txt의 패키지를 설치해줘.",
    answer: ["현재 프로젝트의 Python 환경과 requirements.txt를 확인했습니다. 기존 공급 경로로 설치해 보겠습니다."],
    tools: [{ name: "pip install (작업 Python)", output: ["No matching distribution found for skillloop-demo-pkg==1.0.0", "exit code 1"], tone: "error" }] },
  { title: "Agent가 실패를 관찰하고 팀 경험 검색", prompt: "",
    answer: ["현재 패키지 공급 경로에서 대상을 찾지 못했습니다. 같은 시도를 반복하지 않고 현재 저장된 팀 Skill을 확인합니다."],
    tools: [{ name: "SkillLoop · 관찰 기반 검색", output: ["MATCH fix-skillloop-demo-pkg-install@1.0.0", "운영자가 승인한 로컬 Skill · 적용 조건 확인"], tone: "success" }] },
  { title: "선택된 절차를 같은 작업 환경에 적용", prompt: "",
    answer: ["Skill에 기록된 허용 공급 경로로 설치합니다. 작업 Python을 새 데모 환경으로 교체하지 않습니다."],
    tools: [{ name: "SkillLoop · 적용·검증", output: ["pip exit=0", "설치 확인 · 요구 버전 확인 · import PASS"], tone: "success" }] },
  { title: "성공한 재사용만 기록", prompt: "", event: "reuse",
    answer: ["설치와 독립 import 확인이 끝났습니다. 검증된 재사용만 1건 기록하며 기존 Skill을 중복 후보로 만들지 않습니다."],
    tools: [{ name: "SkillLoop · 실적 기록 흐름", output: ["설명용 재사용 0 → 1", "새 후보 0 · 같은 실행 재처리 시 추가 집계 없음"], tone: "success" }] },
];

const P1: DemoStep[] = [
  { title: "업무 요청 → 직접 읽기 실패 → 관련 Skill 없음", prompt: "AAAAA01_직전_3달_생산량.xlsx를 읽고 다음달 예상 생산량을 포함한 추세선을 보여줘.",
    answer: ["일반적인 XLSX 읽기를 시도한 뒤 현재 팀 Skill을 검색합니다. ‘사내환경 · NASCA(가상)’은 작업 공간에 제공된 환경 설명입니다.", "일반적인 XLSX 읽기로는 파일을 열 수 없었고, 팀 Skill에서도 맞는 절차를 찾지 못했습니다. 사용자 환경에서는 이 파일을 Excel로 열어 볼 수 있나요?"],
    tools: [{ name: "openpyxl · 실제 직접 읽기 경로", output: ["BadZipFile: File is not a zip file"], tone: "error" },
      { name: "SkillLoop · 현재 팀 Skill 검색", output: ["NO_MATCH · 관련 해결 절차 없음"], tone: "error" }] },
  { title: "사용자가 환경 사실을 알려줌", prompt: "이상하네, 난 엑셀을 열어서 데이터를 볼 수 있는데? 한번 다른 방법으로 진행해봐.",
    answer: ["Excel에서는 볼 수 있다는 점을 확인했습니다. 현재 실행 중인 애플리케이션과 대상 문서를 확인하고, 원본을 저장하지 않는 다른 읽기 방법을 찾아보겠습니다."] },
  { title: "환경을 조사하고 허용된 접근 방법 발견", prompt: "",
    answer: ["실행 중인 Excel에서 대상 문서를 확인했습니다. 이미 사용자가 볼 수 있는 애플리케이션을 통해 원본을 저장하지 않고 값을 읽는 방법을 찾았습니다. 잠금 파일만으로 열린 상태를 판단하지 않습니다."],
    tools: [{ name: "환경 조사 → Excel 앱 접근", output: ["현재 어댑터: Excel COM attach", "workbook read PASS · 원본 hash 유지 · Save 미호출"], tone: "success" }] },
  { title: "업무 차트 완성 → 환경 절차만 후보로", prompt: "", event: "candidate", chart: "p1-cold.png",
    answer: ["현재 문서의 시트·열을 해석해 실제 생산량 1200, 1350, 1500과 다음달 예상 1650을 구했습니다.", "환경 접근 절차만 후보로 남깁니다. 생산량·시트·열·계산식·차트·암호는 공유 후보에 포함하지 않습니다. 후보는 아직 게시된 Skill이 아닙니다."],
    tools: [{ name: "SkillLoop · 업무 검증·후보 생성", output: ["WORK_COMPLETE · 실제 3개월 + 예상 1개월", "후보 +1 · 기존 Skill 재사용 0"], tone: "success" }] },
  { title: "사람이 정확한 후보 내용을 검토", prompt: "이 후보의 접근 절차를 확인했어. 이 정확한 내용을 승인할게.", event: "review",
    answer: ["사람이 검토한 id·version·digest에 승인을 연결합니다. 내용이 바뀌면 이 승인은 이어지지 않습니다. 아직 팀 게시 전입니다."],
    tools: [{ name: "사람 review", output: ["exact candidate APPROVED", "게시 수 변화 없음"], tone: "success" }] },
  { title: "다른 문서에서 독립 Replay", prompt: "", event: "replay",
    answer: ["다른 시트 배치·값의 문서에서 같은 절차를 새로 실행합니다. 처음 읽었던 결과를 재사용하지 않습니다."],
    tools: [{ name: "독립 Replay", output: ["승인 후보 digest 동일 · fresh read PASS", "원본 무변경 · FAIL/NOT_RUN이면 게시 금지"], tone: "success" }] },
  { title: "GitHub 공용 저장소에 실제 게시하는 단계", prompt: "", event: "publish",
    answer: ["검토와 Replay가 충족된 절차만 내보내고 team-skill-store에 push합니다. 원격 성공을 확인해야 PUBLISHED로 표시합니다."],
    tools: [{ name: "Git 공유", output: ["descriptor export → push → remote commit 확인", "설명용 팀 게시 Skill 0 → 1"], tone: "success" }] },
  { title: "새 Agent가 가져온 Skill을 발견", prompt: "BBBBB02_직전_3달_생산량.xlsx도 다음달 예상 생산량을 포함해 보여줘.",
    answer: ["새 작업 환경이 GitHub에서 Skill을 받아 무결성을 확인했습니다. 이번 문서의 직접 읽기 실패에도 해당 Skill이 매칭됩니다. 원격 Skill이므로 정확한 내용의 실행 확인을 받습니다."],
    tools: [{ name: "새 환경 pull → 검색", output: ["MATCH · 같은 id/version/digest", "수신 환경의 사람 review·Replay 기록은 만들어 넣지 않음", "CONFIRMATION_REQUIRED"], tone: "success" }] },
  { title: "확인 후 Warm 재사용 → 새 후보 0", prompt: "확인한 이 Skill의 실행을 승인할게.", event: "reuse", chart: "p1-warm.png",
    answer: ["다른 문서의 시트·열을 해석해 실제 생산량 2100, 2250, 2400과 예상 2550을 구했습니다.", "같은 환경 Skill을 재사용했으므로 새 후보는 0입니다. 검증된 재사용 이벤트를 공유하고 반복 수신해도 한 번만 집계합니다.", "한 Agent가 해결한 사내환경의 시행착오를, 다음 Agent는 처음부터 다시 찾지 않습니다."],
    tools: [{ name: "SkillLoop · Warm 검증·실적", output: ["WORK_COMPLETE · reuse +1 · candidate 0", "공유 이벤트 첫 import 1 · 반복 import 0"], tone: "success" }] },
];

export const SCENARIOS = { p0: P0, p1: P1 } as const;

export function demoCounts(scenario: Scenario, completed: number) {
  const events = SCENARIOS[scenario].slice(0, Math.max(0, completed)).map(step => step.event);
  const published = events.includes("publish") ? 1 : 0;
  const reused = events.includes("reuse") ? 1 : 0;
  // P0 uses an existing operator-approved local Skill; this run never publishes it.
  return { published, available: 1 + published, reused,
    candidates: events.includes("candidate") && !published ? 1 : 0,
    warm: scenario === "p1" && reused === 1 };
}
