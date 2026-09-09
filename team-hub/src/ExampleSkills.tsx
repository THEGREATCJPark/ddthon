import {useEffect, useState, type FormEvent} from "react";
import {Plus, Search, ChevronDown} from "lucide-react";
import {session} from "./communityApi";
import {watchExamples, saveExample, removeExample} from "./exampleSkillApi";
import {fields, valueFields, emptyDraft, featured, type SkillDraft, type ExampleSkill} from "./exampleSkillData";

function SkillCard({item, sample = false, mine = false}: {item: SkillDraft & {id?: string}; sample?: boolean; mine?: boolean}) {
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function remove() {
    setBusy(true);
    try { await removeExample(item.id!); }
    catch { setError("삭제하지 못했습니다. 다시 시도해 주세요."); setBusy(false); }
  }
  return <article className="example-row">
    <details>
      <summary className={`example-row-summary ${item.body ? "example-free-summary" : ""}`}>
        <div className="example-row-name"><span className="capture-kind">{sample ? "실제 사례" : "공유 사례"} · Skill 후보</span><h3>{item.title}</h3><small>{item.author}</small></div>
        {item.body ? <p className="example-body-preview">{item.body}</p> : <>
        <div><span className="example-cell-label">조직에 주는 도움</span><p>{item.benefit || "상세 사례에서 확인"}</p></div>
        <div><span className="example-cell-label">기대효과</span><p>{item.effect || "상세 사례에서 확인"}</p></div>
        </>}
        <span className="example-expand-label">상세 <ChevronDown size={18}/></span>
      </summary>
      <div className="example-row-detail">
        {item.body ? <section className="example-free-body"><p>{item.body}</p></section> : fields.slice(2).map(f => <section key={f.key}><h4>{f.label}</h4><p>{item[f.key]}</p></section>)}
        {mine && <div className="example-actions">{confirm ? <><span>이 사례를 삭제할까요?</span><button disabled={busy} onClick={remove}>삭제</button><button disabled={busy} onClick={() => setConfirm(false)}>취소</button></> : <button onClick={() => setConfirm(true)}>내 사례 삭제</button>}</div>}
        {error && <p role="alert" className="notice">{error}</p>}
      </div>
    </details>
  </article>;
}
export default function ExampleSkills() {
  const [search, setSearch] = useState("");
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
  const allItems = [{...featured, id:"featured-s3", uid:""}, ...items];
  const needle = search.trim().toLocaleLowerCase();
  const visible = allItems.filter(item => (item.body || "").toLocaleLowerCase().includes(needle) || [...fields, ...valueFields].some(f => (item[f.key] || "").toLocaleLowerCase().includes(needle)));
  return <section className="examples-page">
    <div className="page-heading"><div><h2>예시 스킬</h2><p>어떤 문제를 풀고, 우리 조직에 어떤 도움이 될까요?</p></div><button className="button primary" disabled={busy} onClick={() => {setOpen(!open); setSuccess("");}}><Plus size={18}/>{open ? "등록 닫기" : "사례 추가"}</button></div>
    <div className="example-intro"><strong>쌓인 Skill이 다음 LOOP를 더 짧게.</strong><p>새로운 환경에서도 축적된 스킬을 해결의 단서로 활용하면 탐색·시행착오를 줄일 수 있습니다. 새로 찾은 해결법을 검토·검증해 다시 쌓으면, 재사용과 지식 축적이 서로를 가속할 수 있습니다.</p><div>환경 문제 <span>→</span> Skill 활용 <span>→</span> 더 짧은 LOOP <span>→</span> 새 Skill 축적</div></div>
    {success && <p role="status" className="notice">{success}</p>}
    {open && <form className="capture-form example-form" onSubmit={submit}>
      <h3>스킬 아이디어를 자유롭게 남겨 주세요</h3>
      <label>제목<input required maxLength={100} disabled={busy} value={draft.title} placeholder="어떤 스킬인지 한 줄로" onChange={e => setDraft({...draft, title:e.target.value})}/></label>
      <label>내용<textarea required rows={10} maxLength={60000} disabled={busy} value={draft.body} placeholder="겪은 문제, 해결 경험, 조직에 도움이 될 아이디어 등을 자유롭게 적거나 붙여넣어 주세요." onChange={e => setDraft({...draft, body:e.target.value})}/></label>
      <label>이름 · 선택<input maxLength={30} disabled={busy} value={draft.author} placeholder="이름 또는 팀명" onChange={e => setDraft({...draft, author:e.target.value})}/></label>
      <div className="form-bottom"><span>등록한 브라우저에서 삭제할 수 있습니다.</span><button className="button primary" disabled={busy}>{busy ? "공유 중…" : "사례 공유"}</button></div>
      {formError && <p className="notice" role="alert">{formError}</p>}
    </form>}
    <div className="example-list-toolbar"><h3>스킬 목록 <span>{visible.length}</span></h3><label><Search size={18}/><input type="search" aria-label="스킬 검색" placeholder="스킬·문제·기대효과 검색" value={search} onChange={e => setSearch(e.target.value)}/></label></div>
    <div className="example-list-head" aria-hidden="true"><span>어떤 스킬인가요?</span><span>조직에 주는 도움</span><span>기대효과</span><span/></div>
    <div className="example-list">{visible.map(item => <SkillCard key={item.id} item={item} sample={item.id === "featured-s3"} mine={!!uid && item.uid === uid}/>)}</div>
    {!visible.length && <p className="example-empty">검색 결과가 없습니다. 다른 단어로 찾아보세요.</p>}
    {loading && <p role="status">공유 사례를 불러오는 중…</p>}
    {error && <p role="alert" className="notice">{error}</p>}
  </section>;
}
