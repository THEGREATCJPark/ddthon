import {ArrowRight, CheckCircle2, FileSearch, FolderCheck, RefreshCw} from "lucide-react";
import P0Comparison from "./P0Comparison";
const mechanisms = [
  [FileSearch,"실패에서 찾고","오류와 적용 조건으로 맞는 팀 Skill을 찾습니다.","해결 문서 이름을 몰라도 시작"],
  [RefreshCw,"현재 업무에 적용","맞는 Skill이 없으면 환경을 확인하고 해결 방법을 탐색합니다.","읽을거리에서 끝나지 않고 업무 계속"],
  [CheckCircle2,"결과를 검증","실제 업무 성공을 확인하고, 성공한 재사용만 기록합니다.","Agent의 완료 선언을 넘어 결과 확인"],
  [FolderCheck,"다음 팀원에게 축적","새 환경 절차는 사람 검토·독립 Replay 후 팀에 게시합니다.","이번 시행착오를 다음 업무의 출발점으로"],
] as const;
export default function ProductIntro() {
  return <div className="product-intro">
    <section className="impact-hero"><span className="overview-eyebrow">AGENT SKILLLOOP</span><h2>한 번 찾은 사내환경 해결법,<br/>다음 Agent의 출발점으로.</h2><p>패키지 설치, 보안 문서 접근, 사내 DB 연결에서 막히는 Coding Agent.<br/><strong>팀이 검증한 환경 절차를 찾아 적용하고, 새로 푼 문제는 다음 팀이 쓸 Skill로 남깁니다.</strong></p><div className="impact-actions"><a className="button primary" href="#captures-p0">실제 시연 보기 <ArrowRight size={17}/></a><a href="#skills">우리 조직에서는 어디에 쓸까? ↗</a></div></section>
    <section className="impact-before-after" aria-label="팀 경험 공유 전후"><article><span>경험이 개인 채팅에만 남으면</span><h3>다음 사람도 원인부터 다시 탐색</h3><p>Agent A: 실패 → 탐색·시도 → 해결</p><p>Agent B: 실패 → 같은 원인 탐색·시도 → 해결</p></article><article><span>검증된 해결 절차를 Team Skill로 남기면</span><h3>다음 Agent는 팀의 경험에서 시작</h3><p>Agent A: 해결 → 검증·검토·Replay → Skill 게시</p><p>Agent B: 실패 → 조건에 맞는 Skill → 적용·검증</p></article></section>
    <section className="impact-how"><h2>어떻게 작동해서 좋아지나요?</h2><div>{mechanisms.map(([Icon,title,body,benefit],i)=><article key={title}><span><Icon size={22}/>{String(i+1).padStart(2,"0")}</span><h3>{title}</h3><p>{body}</p><strong>{benefit}</strong></article>)}</div></section>
    <section className="impact-cases"><h2>두 가지 상황, 같은 축적의 흐름</h2><div><article><span className="overview-eyebrow">이미 팀이 해결한 문제 · P0</span><h3>“requirements.txt 패키지 설치해줘.”</h3><p>설치 실패 → 기존 Skill 발견 → 설치·import 검증 → 재사용 +1</p><strong>같은 원인을 다시 찾는 탐색을 줄입니다.</strong></article><article><span className="overview-eyebrow">팀도 처음 보는 문제 · P1</span><h3>“이 Excel로 다음 달 예상 생산량을 보여줘.”</h3><p>직접 읽기 실패 → 맞는 Skill 없음 → 환경 확인·탐색 → 읽기·예측·차트 검증</p><strong>처음 막힌 환경에서도 업무 완료를 시도하고, 새 해결법을 남깁니다.</strong></article></div></section>
    <P0Comparison/>
    <section className="impact-evidence" id="p1-results"><div className="impact-evidence-heading"><div><span className="overview-eyebrow">P1 · 처음 마주한 Excel 접근 문제</span><h3>비교의 기준은 “빨랐나”보다 “업무를 끝냈나”.</h3></div><a href="#captures-p1">실제 영상·응답·차트 ↗</a></div><p>공개된 별도 3회차는 데이터 읽기·예측·차트를 완료하고 환경 절차 후보 1건을 남겼습니다. 게시까지 진행한 수동 영상과는 다른 실행입니다.</p><div className="impact-outcome"><strong>확인된 3회차: 업무 성공</strong><span>후보 1건 · 게시 미실행 · 재사용 증가 0회</span></div><p className="impact-caveat">현재 공개된 근거는 별도 3회차 성공 사례입니다. 적용 전·후 성공률 비교 결과는 아직 없으며, 이 사례 한 건만으로 성공률 향상을 주장하지 않습니다.</p></section>
    <section className="impact-difference"><h2>업무의 답이 아니라, 다음 업무를 풀 방법을 공유합니다.</h2><div><article><h3>실패한 Agent가 찾아 적용</h3><p>문서 링크를 알려주는 데서 끝나지 않고, 현재 상황에 맞는 절차를 적용하고 결과까지 확인합니다.</p></article><article><h3>파일·정답은 새로 해석</h3><p>특정 파일의 경로·시트·열·생산량·예측값 대신 환경 접근 절차를 남깁니다. 다음 업무의 데이터와 답은 새로 확인합니다.</p></article><article><h3>공유와 성공을 구분</h3><p>사람 검토와 다른 입력으로 Replay를 거친 뒤 게시합니다. 다음 Agent가 실제 성공한 재사용만 +1로 기록합니다.</p></article></div></section>
  </div>;
}
