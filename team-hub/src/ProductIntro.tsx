import {CheckCircle2, FileSearch, FolderCheck, RefreshCw} from "lucide-react";
// Keep the original >10MB video available without making it a build input.
const introVideo = "https://raw.githubusercontent.com/THEGREATCJPark/ddthon/2e034256e1529bec30687a110c9cdea50b357171/result/agent-skillloop-intro-20260909/Agent_SkillLoop_Animated_30s.mp4";
const mechanisms = [
  [FileSearch,"실패에서 찾고","오류와 적용 조건으로 맞는 팀 Skill을 찾습니다."],
  [RefreshCw,"새로운 문제는 Loop를 통해 해결하고","맞는 Skill이 없으면 환경을 확인하고 해결 방법을 탐색합니다."],
  [CheckCircle2,"결과를 검증","실제 업무 성공을 확인하고, 성공한 재사용만 기록합니다."],
  [FolderCheck,"다음 팀원에게 축적","새 환경 절차는 사람 검토·독립 Replay 후 팀에 게시합니다."],
] as const;

function IntroVideo({src}: {src: string}) {
  return <aside className="overview-video" aria-label="Agent Skillloop 30초 소개 영상">
    <video src={src} controls playsInline preload="metadata" aria-label="Agent Skillloop 소개 영상">
      <a href={src}>소개 영상 다운로드</a>
    </video>
  </aside>;
}

export default function ProductIntro() {
  return <div className="product-intro overview-simple">
    <section className="impact-hero overview-hero-with-video">
      <div><h2>내 Agent가 고생한 삽질을<br/>다른 팀원은 하지 않습니다.</h2><p>사내 환경 셋업, 보안 문서 접근, 사내 DB 연결 등 AI Agent가 막히는 여러 문제를 팀 공용 Skill을 찾아 적용하고, 새로 푼 문제는 다음 팀원이 쓸 수 있게 Skill로 남깁니다.</p></div>
      <IntroVideo src={introVideo}/>
    </section>
    <section className="impact-how"><h2>어떻게 작동해서 좋아지나요?</h2><div>{mechanisms.map(([Icon,title,body],i)=><article key={title}><span><Icon size={22}/>{String(i+1).padStart(2,"0")}</span><h3>{title}</h3><p>{body}</p></article>)}</div></section>
    <p className="overview-promise">나의 시행착오를 다른 팀원은 겪지 않습니다.</p>
  </div>;
}
