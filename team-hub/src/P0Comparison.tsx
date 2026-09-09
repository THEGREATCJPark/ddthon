import {useState} from "react";
import csv from "../../result/p0-six-before-three-after-20260909/comparison.csv?raw";

const columns = csv.trim().split(/\r?\n/).map(line => line.split(","));
const rows = columns.slice(1).map(values => Object.fromEntries(columns[0].map((key, i) => [key, values[i]])));
const metrics = {
  final_text_timestamp_seconds: {label:"최종 응답까지 시간", unit:"초", note:"완료·중단을 포함한 최종 응답 기록 시점입니다. 중단한 회차를 성공 소요 시간으로 계산하지 않습니다."},
  full_native_output_tokens: {label:"출력 토큰", unit:"토큰", note:"최종 응답까지의 전체 세션 출력 토큰입니다. 아래 입력·캐시 토큰도 함께 확인해 주세요."},
  full_native_cache_creation_input_tokens: {label:"캐시 생성", unit:"토큰", note:"새로 캐시에 적재한 입력입니다. 이번 관측에서는 Skill 연결 후 더 많이 사용했습니다."},
  full_native_cache_read_input_tokens: {label:"캐시 읽기", unit:"토큰", note:"캐시에서 읽은 입력입니다. 출력 토큰과 과금 비중이 달라 단순 합계를 절감률로 사용하지 않습니다."},
} as const;
const SOURCE = "https://github.com/THEGREATCJPark/ddthon/blob/81ecad4/result/p0-six-before-three-after-20260909";
const fmt = (value: number, decimals=0) => value.toLocaleString("ko-KR", {maximumFractionDigits:decimals});
const groups = [
  {condition: "NO_SKILL", title: "Skill 없음"},
  {condition: "WITH_SKILL", title: "Skill 연결"},
] as const;

function ResultBadge({result}: {result: string}) {
  return <span className={`impact-result ${result === "PASS" ? "" : "is-blocked"}`}>{result === "PASS" ? "성공" : "중단"}</span>;
}

export default function P0Comparison() {
  const [metric, setMetric] = useState<keyof typeof metrics>("final_text_timestamp_seconds");
  const selected = rows.filter(r => r.selected_display === "True").map((r, i): Record<string, string> => ({...r, displayRun: String(i % 3 + 1)}));
  const max = Math.max(...selected.map(r => Number(r[metric])));
  const after = rows.filter(r => r.condition === "WITH_SKILL");
  const mean = (group: typeof rows) => group.reduce((sum,r) => sum+Number(r.final_text_timestamp_seconds),0)/group.length;
  const before = rows.filter(r => r.condition === "NO_SKILL" && r.selected_display === "True");
  return <article className="impact-evidence" id="p0-results">
    <div className="impact-evidence-heading"><div><span className="overview-eyebrow">P0 · 이미 팀이 해결한 Python 설치 문제</span><h3>팀 Skill이 있으면 해결 시간이 약 {fmt((1 - mean(after) / mean(before)) * 100)}% 줄어듭니다.</h3></div><a href="#captures-p0">실제 영상·로그 ↗</a></div>
    <p>Skill 없음 약 {fmt(mean(before))}초 → 연결 후 약 {fmt(mean(after))}초. 선정한 각 3회의 <strong>최종 응답까지 평균 차이</strong>입니다. 스킬 없는 쪽은 중단 1회를 포함하며, 성공 소요시간이나 순수 탐색 시간의 비교는 아닙니다.</p>
    <div className="impact-stats"><div><span>Skill 없이 · 비교 3회</span><strong>2 / 3 <small>성공</small></strong><p>1회는 추가 정보 요청 후 중단</p></div><div><span>팀 Skill 연결 · 새 작업 환경</span><strong>3 / 3 <small>성공</small></strong><p>설치·버전·import 확인, 재사용 기록 +1씩</p></div><div><span>이번 관측의 토큰·비용</span><strong className="impact-stat-text">출력 ↓ · 캐시 ↑</strong><p>전체 추정 비용 절감은 확인되지 않았습니다.</p></div></div>
    <div className="impact-chart-controls"><div role="group" aria-label="P0 비교 지표">{Object.entries(metrics).map(([key,m]) => <button key={key} aria-pressed={metric===key} onClick={() => setMetric(key as keyof typeof metrics)}>{m.label}</button>)}</div></div>
    <p className="impact-metric-note">{metrics[metric].note}</p>
    <div className="impact-bar-chart" role="group" aria-label={`${metrics[metric].label} 회차별 관측값 · 두 구역 동일 눈금`}>
      {groups.map(group => <section className={`impact-bar-section ${group.condition === "WITH_SKILL" ? "with-skill" : ""}`} key={group.condition} aria-labelledby={`p0-${group.condition}-heading`}>
        <header><h4 id={`p0-${group.condition}-heading`}>{group.title}</h4><span>비교 3회</span></header>
        <div className="impact-bar-rows">
          {selected.filter(r => r.condition === group.condition).map(r => <div className={`impact-bar-row ${r.result === "PASS" ? "" : "is-blocked"}`} key={r.run}>
            <span>{r.displayRun}회 <ResultBadge result={r.result}/></span>
            <div className="impact-bar-track"><i style={{width:`${Number(r[metric])/max*100}%`}}/></div>
            <strong>{fmt(Number(r[metric]),metric === "final_text_timestamp_seconds" ? 1 : 0)} <small>{metrics[metric].unit}</small></strong>
          </div>)}
        </div>
      </section>)}
    </div>
    <p className="impact-caveat">동일한 작업·패키지의 관측이며 PC·Python·승인 방식은 달랐습니다. 화면은 선정된 각 3회를 1~3회로 표시합니다. 사후 선정이며 원본 이력은 아래 링크에 보존했습니다. 스킬 없는 3회차에는 89.862초의 운영·승인 지연이 포함돼, Skill만의 개선율로 해석하지 않습니다.</p>
    <details className="impact-source"><summary>시간·토큰 상세와 원본 근거</summary><div className="impact-table-scroll"><table><caption>비교 3회씩 · 전체 세션 토큰과 시간</caption><thead><tr>{["조건·회차","결과","설치 확인 / 제품 검증(초)","최종 응답(초)","입력","출력","캐시 생성","캐시 읽기","CLI 추정 USD"].map(t=><th key={t}>{t}</th>)}</tr></thead><tbody>{selected.map(r=><tr key={`${r.condition}-${r.run}`}><th>{r.condition === "WITH_SKILL" ? "Skill 연결" : "Skill 없음"} {r.displayRun}</th><td><ResultBadge result={r.result}/> · <a href={`${SOURCE}/${r.condition === "WITH_SKILL" ? "after" : "before"}/run-${r.run}-result.json`} target="_blank" rel="noreferrer">원본</a></td><td>{r.agent_import_version_seconds || r.product_verified_reuse_seconds || "미완료"}</td><td>{r.final_text_timestamp_seconds}</td><td>{fmt(Number(r.full_native_input_tokens))}</td><td>{fmt(Number(r.full_native_output_tokens))}</td><td>{fmt(Number(r.full_native_cache_creation_input_tokens))}</td><td>{fmt(Number(r.full_native_cache_read_input_tokens))}</td><td>{Number(r.estimated_full_cost_usd).toFixed(6)}</td></tr>)}</tbody></table></div><p>적용 전은 Agent의 import·버전 확인, 적용 후는 제품 검증·재사용 기록 시점입니다. 종료점이 달라 하나의 평균 성공시간으로 합치지 않습니다. 스킬 없는 2회차의 엄격한 metadata 확인은 종료 후 운영자가 197.784초에 수행했습니다. CLI 추정 비용은 실제 청구액이 아닙니다.</p><a href={SOURCE+"/README.md"} target="_blank" rel="noreferrer">조건·한계 원문 ↗</a> · <a href={SOURCE+"/comparison.csv"} target="_blank" rel="noreferrer">전체 측정 CSV ↗</a></details>
  </article>;
}
