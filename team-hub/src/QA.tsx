import { useState } from "react";
import { BadgeCheck, ShieldCheck, Terminal, ChevronDown } from "lucide-react";
import report from "./qaReport.json";

type Round = {
  n: number;
  at: string;
  sha?: string;
  counted: boolean;
  resolved?: number;
  tracking?: number;
};
type Area = {
  id: string;
  name: string;
  state: string;
  pct?: number;
  summary: string;
  evidence: string[];
};

const rounds = report.rounds as Round[];
const areas = report.areas as Area[];
const counted = rounds.filter((r) => r.counted);

/* 앞뒤로 붙은 미집계 회차는 그릴 점이 없으므로 축에서 뺀다 — 표와 회차 수에는 남는다.
   사이에 낀 미집계 회차는 그대로 눈금을 유지하고 선을 끊는다(보간 금지). */
const first = rounds.findIndex((r) => r.counted);
const lastIdx = rounds.length - 1 - [...rounds].reverse().findIndex((r) => r.counted);
const plot = rounds.slice(first, lastIdx + 1);
const trimmed = rounds.length - plot.length;

const W = 640;
const H = 244;
const PAD = { top: 18, right: 104, bottom: 52, left: 44 };
const top = Math.max(
  ...counted.flatMap((r) => [r.resolved ?? 0, r.tracking ?? 0]),
);
const yMax = Math.ceil((top + 1) / 2) * 2;
const x = (i: number) =>
  PAD.left + (i * (W - PAD.left - PAD.right)) / Math.max(plot.length - 1, 1);
const y = (v: number) =>
  H - PAD.bottom - (v / yMax) * (H - PAD.top - PAD.bottom);

/** 집계 없는 회차에서 선을 끊는다 — 보간하지 않는다. */
function segments(key: "resolved" | "tracking") {
  const out: { i: number; v: number }[][] = [];
  let run: { i: number; v: number }[] = [];
  plot.forEach((r, i) => {
    const v = r[key];
    if (r.counted && typeof v === "number") run.push({ i, v });
    else if (run.length) {
      out.push(run);
      run = [];
    }
  });
  if (run.length) out.push(run);
  return out;
}

const series = [
  { key: "resolved" as const, name: "누적 해소", color: "var(--blue)" },
  { key: "tracking" as const, name: "추적 중", color: "var(--gold)" },
];

function RoundChart() {
  const [hover, setHover] = useState<number | null>(null);
  const active = hover === null ? null : plot[hover];
  const last = counted[counted.length - 1];
  return (
    <div className="qa-chart">
      {/* 좁은 화면에서 축 글자가 읽을 수 없게 줄어드는 대신 가로 스크롤 */}
      <div className="qa-chart-scroll">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label={`QA 라운드별 지적 처리 추이. 집계된 ${counted.length}개 회차, ${plot[0].at}부터 ${plot[plot.length - 1].at}까지. 마지막 회차 누적 해소 ${last.resolved}건, 추적 중 ${last.tracking}건.`}
      >
        <title>QA 라운드별 지적 처리 추이</title>
        <desc>
          {`${counted.length}개 회차. 누적 해소는 ${counted[0].resolved}건에서 ${last.resolved}건으로, 추적 중은 ${counted[0].tracking}건에서 ${last.tracking}건으로 변화. 집계가 없는 회차는 선이 끊어져 있다.`}
        </desc>

        {Array.from({ length: yMax / 2 + 1 }, (_, k) => k * 2).map((v) => (
          <g key={v}>
            <line
              className="qa-grid"
              x1={PAD.left}
              x2={W - PAD.right}
              y1={y(v)}
              y2={y(v)}
            />
            <text className="qa-axis qa-ytick" x={PAD.left - 10} y={y(v) + 4}>
              {v}
            </text>
          </g>
        ))}

        {/* 날짜는 바뀌는 눈금에만 — 같은 날짜를 6번 반복하면 축이 넘친다.
            양 끝 눈금은 start/end로 붙여 카드 밖으로 밀려나지 않게 한다. */}
        {plot.map((r, i) => {
          const [day, time] = r.at.split(" ");
          const newDay = i === 0 || plot[i - 1].at.split(" ")[0] !== day;
          const side = i === 0 ? " start" : i === plot.length - 1 ? " end" : "";
          return (
            <g key={r.n}>
              <text className={`qa-axis qa-xtick${side}`} x={x(i)} y={H - 30}>
                {time}
              </text>
              {newDay && (
                <text
                  className={`qa-axis qa-xtick qa-xday${side}`}
                  x={x(i)}
                  y={H - 15}
                >
                  {day}
                </text>
              )}
            </g>
          );
        })}

        {series.map((s) =>
          segments(s.key).map((seg, k) => (
            <polyline
              key={`${s.key}-${k}`}
              className="qa-line"
              stroke={s.color}
              points={seg.map((p) => `${x(p.i)},${y(p.v)}`).join(" ")}
            />
          )),
        )}

        {series.map((s) =>
          plot.map((r, i) => {
            const v = r[s.key];
            if (!r.counted || typeof v !== "number") return null;
            return (
              <circle
                key={`${s.key}-${r.n}`}
                className="qa-dot"
                cx={x(i)}
                cy={y(v)}
                r={hover === i ? 7 : 5}
                fill={s.color}
                tabIndex={0}
                role="button"
                aria-label={`${r.n}회차 ${r.at} · ${s.name} ${v}건`}
                onMouseEnter={() => setHover(i)}
                onMouseLeave={() => setHover(null)}
                onFocus={() => setHover(i)}
                onBlur={() => setHover(null)}
              />
            );
          }),
        )}

        {series.map((s) => {
          const v = last[s.key];
          if (typeof v !== "number") return null;
          return (
            <text
              key={`end-${s.key}`}
              className="qa-endlabel"
              x={W - PAD.right + 12}
              y={y(v) + 4}
            >
              {s.name} {v}건
            </text>
          );
        })}

      </svg>
      </div>

      {active && (
        <p className="qa-tip" role="status">
          <b>
            {active.n}회차 · {active.at}
          </b>
          {active.counted
            ? ` — 누적 해소 ${active.resolved}건 · 추적 중 ${active.tracking}건`
            : " — 이 회차는 집계 형식 이전이라 건수가 없습니다"}
          {active.sha && <code>{active.sha}</code>}
        </p>
      )}

      <ul className="qa-legend">
        {series.map((s) => (
          <li key={s.key}>
            <i style={{ background: s.color }} />
            {s.name}
          </li>
        ))}
      </ul>
      <p className="qa-axisnote">
        QA 자체 집계 · 지적 처리 건수이며 심사 점수가 아닙니다.
        {trimmed > 0 &&
          ` 초기 ${trimmed}개 회차는 집계 형식 이전이라 그래프에는 없고 아래 표에만 있습니다.`}
        {plot.some((r) => !r.counted) &&
          " 중간의 미집계 회차는 앞뒤 값으로 잇지 않고 선을 끊어 둡니다."}
      </p>

      <details className="qa-table">
        <summary>
          같은 수치를 표로 보기 <ChevronDown size={16} />
        </summary>
        <div className="qa-table-scroll">
          <table>
            <thead>
              <tr>
                <th>회차</th>
                <th>시각</th>
                <th>검토 커밋</th>
                <th>누적 해소</th>
                <th>추적 중</th>
              </tr>
            </thead>
            <tbody>
              {rounds.map((r) => (
                <tr key={r.n}>
                  <td>{r.n}</td>
                  <td>{r.at}</td>
                  <td>
                    <code>{r.sha ?? "—"}</code>
                  </td>
                  <td>{r.counted ? `${r.resolved}건` : "—"}</td>
                  <td>{r.counted ? `${r.tracking}건` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}

export default function QA() {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <section className="qa-page">
      <div className="page-heading">
        <div>
          <h2>QA 검증</h2>
          <p>
            팀 내부 독립 QA 점검 · <code>{report.reviewedSha}</code> 기준 (
            {report.reviewedAt})
          </p>
        </div>
        <span className="qa-headline">
          <BadgeCheck size={18} />
          {report.headline}
        </span>
      </div>

      <p className="notice">{report.disclaimer}</p>

      <div className="qa-card">
        <div className="qa-card-head">
          <h3>검증 라운드</h3>
          <p>
            QA 라운드 {rounds.length}회 · {rounds[0].at} ~{" "}
            {rounds[rounds.length - 1].at}
          </p>
        </div>
        <RoundChart />
      </div>

      <div className="qa-card">
        <div className="qa-card-head">
          <h3>검증 영역</h3>
          <p>막대 = QA 검증 완료도 · 심사 점수가 아닙니다</p>
        </div>
        <ul className="qa-areas">
          {areas.map((a) => (
            <li key={a.id}>
              <button
                aria-expanded={open === a.id}
                onClick={() => setOpen(open === a.id ? null : a.id)}
              >
                <span className="qa-area-name">{a.name}</span>
                <span className={`qa-state s-${a.state === "CLEAN" ? "clean" : a.state === "부분 검증" ? "part" : a.state === "NOT_RUN" ? "notrun" : "ok"}`}>
                  {a.state}
                </span>
                <span className="qa-bar">
                  {typeof a.pct === "number" ? (
                    <i style={{ width: `${a.pct}%` }} />
                  ) : (
                    <em>미실행</em>
                  )}
                </span>
                <ChevronDown size={18} className={open === a.id ? "flip" : ""} />
              </button>
              <p className="qa-area-summary">{a.summary}</p>
              {open === a.id && (
                <ul className="qa-evidence">
                  {a.evidence.map((e) => (
                    <li key={e}>{e}</li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </div>

      <div className="qa-card">
        <div className="qa-card-head">
          <h3>
            <Terminal size={18} /> 직접 실행해 확인한 명령
          </h3>
          <p>아래 명령은 저장소를 받아 그대로 재현할 수 있습니다</p>
        </div>
        <ul className="qa-runs">
          {report.runs.map((r) => (
            <li key={r.cmd}>
              <code>{r.cmd}</code>
              <span>{r.result}</span>
              <b>exit {r.exit}</b>
            </li>
          ))}
        </ul>
      </div>

      <Findings />
    </section>
  );
}

type View = "all" | "resolved" | "tracking";

function Findings() {
  const [view, setView] = useState<View>("resolved");
  const { total, resolved, tracking } = report.findings;
  /* 목록에 실리지 않은 해소분 — 제품이 아니라 QA 진행 자체에 대한 항목이라 뺐다.
     빼놓고 말하지 않으면 숫자가 안 맞고, 안 맞는 숫자는 나머지 전부를 의심하게 만든다. */
  const unlisted = resolved - report.resolvedItems.length;

  const tiles: { id: View; n: number; label: string }[] = [
    { id: "all", n: total, label: "누적 지적" },
    { id: "resolved", n: resolved, label: "해소" },
    { id: "tracking", n: tracking, label: "추적 중" },
  ];

  return (
    <div className="qa-card qa-findings">
      <div className="qa-card-head">
        <h3>
          <ShieldCheck size={18} /> 지적 현황
        </h3>
        <p>숫자를 누르면 해당 항목만 봅니다</p>
      </div>

      <div className="qa-counts" role="group" aria-label="지적 현황 보기 선택">
        {tiles.map((t) => (
          <button
            key={t.id}
            className={view === t.id ? "on" : ""}
            aria-pressed={view === t.id}
            onClick={() => setView(t.id)}
          >
            <b>{t.n}</b>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      <div
        className="qa-findings-panel"
        role="region"
        aria-label={tiles.find((t) => t.id === view)!.label}
      >
        {view === "all" && (
          <div className="qa-breakdown">
            <div
              className="qa-stack"
              role="img"
              aria-label={`누적 ${total}건의 구성: 공개된 해소 ${report.resolvedItems.length}건, 비공개 해소 ${unlisted}건, 추적 중 ${tracking}건`}
            >
              <i
                className="b-listed"
                style={{ flexGrow: report.resolvedItems.length }}
              />
              <i className="b-unlisted" style={{ flexGrow: unlisted }} />
              <i className="b-tracking" style={{ flexGrow: tracking }} />
            </div>
            <ul className="qa-buckets">
              <li>
                <i className="b-listed" />
                <b>{report.resolvedItems.length}건</b>
                <span>해소 · 수정 이력 공개</span>
                <button onClick={() => setView("resolved")}>보기</button>
              </li>
              <li>
                <i className="b-unlisted" />
                <b>{unlisted}건</b>
                <span>해소 · 제품이 아니라 QA 진행 자체에 대한 항목이라 생략</span>
              </li>
              <li>
                <i className="b-tracking" />
                <b>{tracking}건</b>
                <span>아직 닫히지 않아 건수로만 공개</span>
                <button onClick={() => setView("tracking")}>이유</button>
              </li>
            </ul>
            <p className="muted">
              {report.resolvedItems.length} + {unlisted} + {tracking} = {total}건
              · 회차마다 새로 발견된 지적과 닫힌 지적이 위 그래프의 두 선입니다.
            </p>
          </div>
        )}

        {view === "resolved" && (
          <>
            <p className="muted">{report.findings.note}</p>
            <ol className="qa-fixlog">
              {report.resolvedItems.map((f) => (
                <li key={f.id}>
                  <div className="qa-fix-meta">
                    <span className="qa-fix-id">{f.id}</span>
                    <span className="qa-fix-round">
                      {f.round}회차 · {f.at}
                    </span>
                  </div>
                  <p className="qa-fix-found">
                    <span>지적</span>
                    {f.found}
                  </p>
                  <p className="qa-fix-fixed">
                    <span>해소</span>
                    {f.fixed}
                  </p>
                </li>
              ))}
            </ol>
          </>
        )}

        {view === "resolved" && unlisted > 0 && (
          <p className="qa-unlisted">
            <b>{unlisted}건</b>은 해소되었으나 제품이 아니라 QA 진행 자체에 대한
            항목이라 위 목록에서 뺐습니다 — 그래서 여기 {report.resolvedItems.length}
            건이고 타일은 {resolved}건입니다.
          </p>
        )}

        {view === "tracking" && (
          <div className="qa-rest qa-tracking">
            <h4>추적 중 {tracking}건 — 제목을 싣지 않습니다</h4>
            <p>
              닫히지 않은 지적을 요약해 올리면, 읽는 사람은 그것을 이미 처리된
              것으로 받아들이게 됩니다. QA에서 미실행은 서술로 닫지 않고 실행으로
              닫기 때문에, 여기서는 <b>건수만</b> 공개합니다.
            </p>
            <p>
              닫히는 대로 <b>해소</b> 목록에 같은 형식(지적 · 해소 · 닫힌 회차)으로
              올라갑니다. 지금까지 {report.resolvedItems.length}건이 그렇게
              올라왔습니다.
            </p>
            <p className="muted">
              상세 내역은 팀 내부 QA 저장소의 회차별 리포트에서 관리합니다.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
