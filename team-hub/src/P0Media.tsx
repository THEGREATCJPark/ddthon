import video from "../../result/p0-demo-20260909/p0-demo.mp4?url";
import subtitles from "./p0-demo.ko.vtt?url";
import srt from "../../result/p0-demo-20260909/p0-demo.ko.srt?url";
import evaluationZip from "../../result/p0-demo-20260909/ai-evaluation/p0-ai-evaluation.zip?url";
import counter from "../../result/p0-demo-20260909/ai-evaluation/Agent_SkillLoop_카운트변화.png";

const frames = import.meta.glob<string>(
  "../../result/p0-demo-20260909/ai-evaluation/evidence/*.png",
  { eager: true, query: "?url", import: "default" },
);
const labels = ["업무 요청", "Skill 적용 명령", "재사용 카운트 0", "재사용 카운트 1", "검증 명령", "최종 응답", "편집 영상 · 카운트 0", "편집 영상 · 카운트 1"];
const repo = "https://github.com/THEGREATCJPark/ddthon/tree/57e4904/result/p0-demo-20260909";

export default function P0Media() {
  return <article className="capture-card p0-media">
    <header><div>
      <span className="capture-kind">P0 · 시연 영상</span>
      <h3>팀 Skill로 Python 패키지 설치하기</h3>
      <p>58초 · 한국어 자막</p>
    </div></header>
    <video controls preload="metadata" playsInline aria-label="P0 실제 시연 영상">
      <source src={video} type="video/mp4" />
      <track kind="subtitles" src={subtitles} srcLang="ko" label="한국어" default />
      영상을 재생할 수 없습니다. 아래 영상 다운로드를 이용해 주세요.
    </video>
    <div className="p0-media-links">
      <a href={video} download="p0-demo.mp4">영상 다운로드</a>
      <a href={srt} download="p0-demo.ko.srt">한국어 자막</a>
      <a href={evaluationZip} download="p0-ai-evaluation.zip">AI 평가 자료 ZIP</a>
      <a href={repo + "/ai-evaluation"} target="_blank" rel="noreferrer">평가 가이드·데이터</a>
    </div>
    <p className="capture-log-note">58초는 편집 영상 길이입니다. 아래 프레임은 제공된 평가 자료이며, 별도 실행의 검증 로그는 영상과 구분해 첨부했습니다.</p>
    <details className="p0-evidence">
      <summary>카운트 변화 · 실행 캡처 보기</summary>
      <a href={counter} target="_blank" rel="noreferrer"><img src={counter} alt="P0 재사용 카운트 변화" loading="lazy" /></a>
      <div className="p0-frame-grid">
        {Object.entries(frames).sort(([a], [b]) => a.localeCompare(b)).map(([path, src], index) => <figure key={path}>
          <a href={src} target="_blank" rel="noreferrer"><img src={src} alt={labels[index]} loading="lazy" /></a>
          <figcaption>{labels[index]}</figcaption>
        </figure>)}
      </div>
    </details>
  </article>;
}
