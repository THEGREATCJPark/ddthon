import csv from "../../result/p1-evaluation-comparison-20260909/comparison.csv?raw";
import {CheckCircle2, XCircle} from "lucide-react";
const lines = csv.trim().split(/\r?\n/).map(line => line.split(","));
const rows = lines.slice(1).map(values => Object.fromEntries(lines[0].map((key,i)=>[key,values[i]])));
const before = rows.filter(r=>r.task_complete === "False");
const after = rows.filter(r=>r.task_complete === "True");
const SOURCE = "https://github.com/THEGREATCJPark/ddthon/blob/f7e06f9cc698f2c753af165f9bf9e428a1fb4017/result/p1-evaluation-comparison-20260909";
export default function P1Comparison() {
  return <article className="impact-evidence" id="p1-results">
    <div className="impact-evidence-heading"><div><span className="overview-eyebrow">P1 · 사내 환경에서 Excel 읽기·예측·차트 생성</span><h3>SkillLoop 없을 땐 미완료, 쓰니 성공.</h3></div><a href="#captures-p1">실제 영상·로그 ↗</a></div>
    <p>동일 Excel 업무의 적용 전·후 3회 비교. 적용 후에도 기존 P1 Skill은 없었습니다. <strong>SkillLoop와 사용자 환경 단서를 활용해 새 문제를 해결한 결과</strong>입니다.</p>
    <div className="p1-outcome-grid">
      <section><span>SkillLoop 미사용</span><h4>0 / 3 <small>업무 완료</small></h4><div>{before.map(r=><p key={r.round}><XCircle size={22}/><b>{r.round}회차</b><span>미완료</span></p>)}</div><p className="p1-outcome-description">암호·사본·추가 자료 요청으로 종료.<br/>실제 데이터와 차트 결과 없음.</p></section>
      <section className="p1-outcome-success"><span>SkillLoop + 환경 사실 제공</span><h4>3 / 3 <small>업무 완료</small></h4><div>{after.slice(0,3).map(r=><p key={r.round}><CheckCircle2 size={22}/><b>{r.round}회차</b><span>읽기·예측·차트 성공</span></p>)}</div><p className="p1-outcome-description">매회 환경 절차 후보 1건 생성.<br/>기존 Skill 재사용·게시는 이번 측정 범위에서 제외.</p></section>
    </div>
    <p className="impact-caveat">추가 관측 1회도 성공해 적용 후 전체는 4/4 완료입니다. 첫 3회와 추가 관측을 구분해 모두 보존했습니다. PC·승인 방식이 다르고 적용 후에는 ‘파일을 열어 두었다’는 환경 사실을 제공했습니다. 일반적인 성공률 또는 SkillLoop 단독 효과를 뜻하지 않습니다.</p>
    <details className="impact-source"><summary>3회씩 상세 기록 · 추가 관측 · 측정 조건</summary><div className="impact-table-scroll"><table><caption>업무 미완료 응답 시간과 실제 업무 완료 시간은 다른 지표입니다.</caption><thead><tr><th>조건</th><th>회차</th><th>업무 결과</th><th>측정 시점</th><th>시간(초)</th><th>최종 응답(초)</th></tr></thead><tbody>{rows.map(r=><tr key={`${r.condition}-${r.round}`}><th>{r.task_complete === "True" ? "SkillLoop 사용" : "SkillLoop 미사용"}</th><td>{r.round === "4" ? "추가 관측" : `${r.round}회차`}</td><td>{r.task_complete === "True" ? "완료" : "미완료"}</td><td>{r.task_complete === "True" ? "실제 업무 완료" : "미완료 최종 응답"}</td><td>{r.seconds}</td><td>{r.user_final_seconds}</td></tr>)}</tbody></table></div><p>이번 적용 후 4회는 모두 기존 P1 Skill이 없는 Cold 실행입니다. 기존 Skill 재사용 성능이나 비용 절감의 근거가 아닙니다. 승인·독립 Replay·게시를 마친 수동 시연 영상은 별도 실행입니다.</p><a href={SOURCE+"/README.md"} target="_blank" rel="noreferrer">원본 보고서 ↗</a> · <a href={SOURCE+"/comparison.csv"} target="_blank" rel="noreferrer">원 데이터 CSV ↗</a></details>
  </article>;
}
