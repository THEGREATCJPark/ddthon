import {useEffect, useState, type FormEvent} from "react";
import {Plus, BookOpen} from "lucide-react";
import {session} from "./communityApi";
import {watchExamples, saveExample, removeExample} from "./exampleSkillApi";
import {fields, emptyDraft, featured, type SkillDraft, type ExampleSkill} from "./exampleSkillData";

function SkillCard({item, sample = false, mine = false}: {item: SkillDraft & {id?: string}; sample?: boolean; mine?: boolean}) {
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function remove() {
    setBusy(true);
    try { await removeExample(item.id!); }
    catch { setError("삭제하지 못했습니다. 다시 시도해 주세요."); setBusy(false); }
  }
  return <article className="example-card">
    <header><span className="capture-kind">{sample ? "공유된 실제 사례" : "팀원이 공유한 사례"} · Skill 후보</span><h3>{item.title}</h3><p>{item.author}</p></header>
    <div className="example-summary">
      <section><h4>겪었던 문제</h4><p>{item.problem}</p></section>
      <section><h4>찾아낸 원인</h4><p>{item.cause}</p></section>
    </div>
    {sample && <div className="example-payoff"><BookOpen size={22}/><div><strong>다음 팀원은 ‘403’에서 시계 오차까지 다시 헤매지 않도록.</strong><p>증상·적용 조건·해결 절차·확인 방법을 함께 남기면, 같은 환경의 다음 요청에 활용할 지식이 됩니다.</p></div></div>}
    <details className="example-detail" open={sample}>
      <summary>Skill로 남길 내용</summary>
      {fields.slice(4).map(f => <section key={f.key}><h4>{f.label}</h4><p>{item[f.key]}</p></section>)}
    </details>
    {mine && <div className="example-actions">{confirm ? <><span>이 사례를 삭제할까요?</span><button disabled={busy} onClick={remove}>삭제</button><button disabled={busy} onClick={() => setConfirm(false)}>취소</button></> : <button onClick={() => setConfirm(true)}>내 사례 삭제</button>}</div>}
    {error && <p role="alert" className="notice">{error}</p>}
  </article>;
}
export default function ExampleSkills() {
  const [items, setItems] = useState<ExampleSkill[]>([]);
  const [uid, setUid] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState({...emptyDraft});
  const [busy, setBusy] = useState(false);
  const [formError, setFormError] = useState("");
  const [success, setSuccess] = useState("");
  useEffect(() => {
    session().then(u => setUid(u.uid)).catch(() => {});
    return watchExamples(data => {setItems(data); setLoading(false); setError("");}, () => {setLoading(false); setError("공유 사례를 불러오지 못했습니다. 새로고침해 주세요.");});
  }, []);
  async function submit(e: FormEvent) {
    e.preventDefault(); if (busy) return;
    setBusy(true); setFormError(""); setSuccess("");
    try {await saveExample(draft); setDraft({...emptyDraft}); setOpen(false); setSuccess("사례를 공유했습니다. 다른 방문자도 볼 수 있습니다.");}
    catch {setFormError("등록하지 못했습니다. 입력 내용은 유지됩니다. 연결을 확인하고 다시 시도해 주세요.");}
    finally {setBusy(false);}
  }
  return <section className="examples-page">
    <div className="page-heading"><div><h2>예시 스킬</h2><p>한 사람이 찾아낸 환경 지식, 다음 팀원의 해결 출발점.</p></div><button className="button primary" disabled={busy} onClick={() => {setOpen(!open); setSuccess("");}}><Plus size={18}/>{open ? "등록 닫기" : "사례 추가"}</button></div>
    {success && <p role="status" className="notice">{success}</p>}
    {open && <form className="capture-form example-form" onSubmit={submit}>
      <h3>우리 팀이 겪은 문제 공유하기</h3>
      <p>방문자에게 공개되는 사례입니다. 비밀번호·키·내부 주소·업무 데이터는 제외해 주세요. 조직 Skill 게시 전 검토·Replay는 별도입니다.</p>
      {fields.map(f => <label key={f.key}>{f.label}{f.key === "title" || f.key === "author" ? <input required maxLength={f.max} disabled={busy} value={draft[f.key]} placeholder={f.placeholder} onChange={e => setDraft({...draft, [f.key]:e.target.value})}/> : <textarea required rows={f.key === "procedure" ? 6 : 3} maxLength={f.max} disabled={busy} value={draft[f.key]} placeholder={f.placeholder} onChange={e => setDraft({...draft, [f.key]:e.target.value})}/>}</label>)}
      <div className="form-bottom"><span>등록한 브라우저에서 삭제할 수 있습니다.</span><button className="button primary" disabled={busy}>{busy ? "공유 중…" : "사례 공유"}</button></div>
      {formError && <p className="notice" role="alert">{formError}</p>}
    </form>}
    <SkillCard item={featured} sample/>
    <h3 className="example-community-title">팀원이 더한 사례 <span>{items.length}</span></h3>
    {loading && <p role="status">공유 사례를 불러오는 중…</p>}
    {error && <p role="alert" className="notice">{error}</p>}
    {!loading && !error && !items.length && <p className="example-empty">설치, 인증, 네트워크, 보안 환경에서 찾아낸 해결법을 남겨 주세요.</p>}
    {items.map(item => <SkillCard key={item.id} item={item} mine={item.uid === uid}/>)}
  </section>;
}
