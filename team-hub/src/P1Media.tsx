import video from "../../result/p1-web-delivery-20260909/video/Agent_SkillLoop_P1_90s.mp4?url";
import srt from "../../result/p1-web-delivery-20260909/video/Agent_SkillLoop_P1_ko.srt?url";
import videoZip from "../../result/p1-web-delivery-20260909/Agent-SkillLoop-P1-Video.zip?url";
import logZip from "../../result/p1-web-delivery-20260909/P1-Web-Log-Round3.zip?url";
import responses from "../../result/p1-web-delivery-20260909/log-round3/responses.public.md?raw";
import transcript from "../../result/p1-web-delivery-20260909/log-round3/transcript.public.md?raw";
import transcriptUrl from "../../result/p1-web-delivery-20260909/log-round3/transcript.public.md?url";
import chart from "../../result/p1-web-delivery-20260909/log-round3/actual-trend.png";

export default function P1Media() {
  return <>
    <article className="capture-card p0-media">
      <header><div><span className="capture-kind">P1 · 수동 Cold 시연 영상</span><h3>새 해결법 발견부터 승인·Replay·게시까지</h3><p>90초 편집 영상 · 게시 커밋 e302bf2</p></div></header>
      <video controls preload="metadata" playsInline aria-label="P1 수동 시연 영상"><source src={video} type="video/mp4"/>아래 링크에서 영상을 다운로드할 수 있습니다.</video>
      <div className="p0-media-links"><a href={video} download="Agent_SkillLoop_P1_90s.mp4">영상 다운로드</a><a href={srt} download="Agent_SkillLoop_P1_ko.srt">한국어 자막 다운로드</a><a href={videoZip} download="Agent-SkillLoop-P1-Video.zip">영상 원본 ZIP</a></div>
      <p className="capture-log-note">사람 승인 → 독립 Replay → 게시까지 진행한 수동 시연입니다. 공개 Skill 1→2는 신규 게시이며 재사용 +1이 아닙니다. 90초는 편집 길이이며, 아래 3회차 로그와는 서로 다른 실행입니다.</p>
    </article>
    <article className="capture-card p1-run">
      <header><div><span className="capture-kind">P1 · 별도 자동 실행 3회차</span><h3>업무 완료 · 후보 생성, 게시 미실행</h3><p>업무 완료 110.539초 · 최종 응답 완료 127.155초</p></div></header>
      <p className="capture-log-note">아래 응답·로그·차트는 별도 3회차 실행 자료입니다. 후보 1건 생성 · 재사용 증가 0회. 사람 검토·독립 Replay·게시는 진행하지 않았습니다. 대표 사례이며 전체 성능 통계가 아닙니다.</p>
      <section className="p1-responses capture-transcript"><h4>대표 실행 응답 · 원문</h4><pre>{responses}</pre></section>
      <section className="p1-chart"><h4>3회차 실제 결과 차트</h4><a href={chart} target="_blank" rel="noreferrer"><img src={chart} alt="별도 3회차 실행의 생산량 실적과 다음 달 예측 차트" loading="lazy"/></a><p>5~7월은 실적, 8월 1,650은 추세 예측입니다. 영상에서 촬영한 차트가 아닙니다.</p></section>
      <details className="capture-transcript p1-log"><summary className="capture-expand">3회차 전체 공개 로그 펼쳐보기</summary><pre>{transcript}</pre></details>
      <div className="p0-media-links"><a href={transcriptUrl} download="transcript.public.md">전체 로그 다운로드</a><a href={logZip} download="P1-Web-Log-Round3.zip">3회차 로그 원본 ZIP</a></div>
    </article>
  </>;
}
