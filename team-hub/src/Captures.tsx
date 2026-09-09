import { useEffect, useRef, useState, type FormEvent } from "react";
import { Plus, Trash2, ImagePlus, FileText } from "lucide-react";
import p0Capture from "../../result/p0-demo-20260909/p0-claude-code.png";
import P0Media from "./P0Media";
import P1Media from "./P1Media";
import p0Log from "./p0-execution-log.txt?raw";
import { session } from "./communityApi";
import {
  loadMedia,
  loadTranscript,
  removeCapture,
  saveCapture,
  watchCaptures,
  type Capture,
} from "./captureApi";

const repositoryP0: Capture = {
  id: "repository-p0-20260909", scenario: "p0",
  title: "Python 패키지 설치 · 기존 팀 Skill 재사용",
  uid: "", mime: "image/png", chunks: 0, hasText: true,
  createdAt: Date.parse("2026-09-09T12:02:00+09:00"),
};

function CaptureCard({ item, mine, bundled = false }: { item: Capture; mine: boolean; bundled?: boolean }) {
  const [media, setMedia] = useState(bundled ? p0Capture : "");
  const [text, setText] = useState<string | null>(bundled ? p0Log : null);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const card = useRef<HTMLElement>(null);
  useEffect(() => {
    if (!item.chunks) return;
    let active = true,
      url = "";
    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      observer.disconnect();
      loadMedia(item)
        .then((value) => {
          if (active) {
            url = value;
            setMedia(value);
          } else URL.revokeObjectURL(value);
        })
        .catch(() => {
          if (active) setError("이미지 로딩 실패 · 새로고침해 주세요.");
        });
    });
    if (card.current) observer.observe(card.current);
    return () => {
      active = false;
      observer.disconnect();
      if (url) URL.revokeObjectURL(url);
    };
  }, [item.id, item.chunks]);
  async function toggleText() {
    if (open) {
      setOpen(false);
      return;
    }
    setOpen(true);
    if (text !== null) return;
    setBusy(true);
    setError("");
    try {
      setText(await loadTranscript(item.id));
    } catch {
      setError("전문을 불러오지 못했습니다. 닫았다가 다시 펼쳐 주세요.");
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    setBusy(true);
    setError("");
    try {
      await removeCapture(item);
    } catch {
      setError("삭제하지 못했습니다. 다시 시도해 주세요.");
      setBusy(false);
    }
  }
  return (
    <article className="capture-card" ref={card}>
      <header>
        <div>
          <span className="capture-kind">
            {item.scenario.toUpperCase()} · 실제 실행 기록
          </span>
          <h3>{item.title}</h3>
          <time>{new Date(item.createdAt).toLocaleString("ko-KR")}</time>
        </div>
        {mine && (
          <button
            className="capture-delete"
            aria-label={`${item.title} 삭제`}
            onClick={() => setDeleting(!deleting)}
          >
            <Trash2 size={17} />
          </button>
        )}
      </header>
      {deleting && (
        <div className="capture-delete-confirm">
          이 기록을 삭제할까요?{" "}
          <button disabled={busy} onClick={remove}>
            삭제
          </button>
          <button onClick={() => setDeleting(false)}>취소</button>
        </div>
      )}
      {(!!item.chunks || bundled) && (
        <div className="capture-media">
          {media ? (
            <a
              href={media}
              target="_blank"
              rel="noreferrer"
              title="원본 이미지 열기"
            >
              <img src={media} alt={item.title} />
            </a>
          ) : (
            <p>이미지/GIF 불러오는 중…</p>
          )}
        </div>
      )}
      {item.hasText && (
        <div className="capture-transcript">
          <button
            className="capture-expand"
            aria-expanded={open}
            onClick={toggleText}
          >
            <FileText size={18} />
            {open ? "실행 로그 접기" : "실행 로그 펼치기"}
            <span>{open ? "−" : "+"}</span>
          </button>
          {open && <>
            <pre>{busy ? "불러오는 중…" : text}</pre>
            {bundled && <p className="capture-log-note">
              이 로그는 기존 팀 Skill을 재사용한 P0 실행 기록입니다. 패키지 설치 후 버전·import를 확인하고 재사용 성공 1회를 기록했습니다.
              저장소의 별도 P0 검증 결과에도 버전 1.0.0, import 성공, 재사용 0→1이 기록돼 있습니다.
              {" "}<a href="https://github.com/THEGREATCJPark/ddthon/blob/139e080a4c43aed793696c3bd8f568c7f0a02e23/result/p0-scoped-auto-20260909/github-cold-result.json" target="_blank" rel="noreferrer">검증 근거</a>
            </p>}
          </>}
        </div>
      )}
      {error && (
        <p className="notice" role="alert">
          {error}
        </p>
      )}
    </article>
  );
}

export default function Captures({initialScenario = "p0"}: {initialScenario?: "p0" | "p1"}) {
  const [scenario, setScenario] = useState<"p0" | "p1">(initialScenario);
  useEffect(() => {
    const syncScenario = () => {
      if (location.hash === "#captures-p1") setScenario("p1");
      else if (location.hash === "#captures-p0" || location.hash === "#captures") setScenario("p0");
    };
    window.addEventListener("hashchange", syncScenario);
    return () => window.removeEventListener("hashchange", syncScenario);
  }, []);
  const [items, setItems] = useState<Capture[]>([]);
  const [uid, setUid] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [transcript, setTranscript] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const form = useRef<HTMLFormElement>(null);
  useEffect(() => {
    session()
      .then((user) => setUid(user.uid))
      .catch(() => {});
    return watchCaptures(
      (data) => {
        setItems(data);
        setLoading(false);
        setError("");
      },
      () => {
        setError("기록을 불러오지 못했습니다. 새로고침해 주세요.");
        setLoading(false);
      },
    );
  }, []);
  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (saving) return;
    setSaving(true);
    setFormError("");
    try {
      await saveCapture(scenario, title, transcript, file);
      setTitle("");
      setTranscript("");
      setFile(null);
      form.current?.reset();
      setFormOpen(false);
    } catch (error) {
      setFormError(
        error instanceof Error && !error.message.startsWith("Firebase")
          ? error.message
          : "등록하지 못했습니다. 연결을 확인하고 다시 시도해 주세요.",
      );
    } finally {
      setSaving(false);
    }
  }
  const visible = items.filter((item) => item.scenario === scenario);
  return (
    <section className="captures-page">
      <div className="page-heading">
        <div>
          <h2>실제 실행 화면과 실행 로그</h2>
        </div>
        <button
          className="button primary"
          onClick={() => setFormOpen(!formOpen)}
          disabled={saving}
        >
          <Plus size={18} />
          {formOpen ? "등록 닫기" : "기록 추가"}
        </button>
      </div>
      <div className="demo-tabs" role="tablist" aria-label="실행 기록 시나리오">
        {(["p0", "p1"] as const).map((value) => (
          <button
            key={value}
            role="tab"
            aria-selected={scenario === value}
            disabled={saving}
            onClick={() => {setScenario(value); location.hash = `captures-${value}`;}}
          >
            <b>{value.toUpperCase()}</b>
            <span>
              {value === "p0"
                ? "Python 설치 · 기존 Skill 재사용"
                : "Excel 분석 · 새로운 Skill 발견"}
            </span>
          </button>
        ))}
      </div>
      <div className="capture-scenario-intro" key={scenario}>
        {scenario === "p0" ? <>
          <h3>Python 패키지 설치 시나리오입니다.</h3>
          <p>비개발자 엔지니어들이 자주 부딪히는 문제를 시나리오로 진행해 봤습니다.<br/>DSDN에 이미 해결법이 많아 따라 하면 풀리는 간단한 문제지만, 직접 시도하는 엔지니어는 적습니다.</p>
          <p>오류를 감지한 Agent Skillloop가 조직 Skill Storage에 이미 적재된 Skill을 찾아 적용해, 빠르게 해결하는 것이 목적입니다.</p>
          <p className="capture-scenario-effect"><strong>효과</strong> · Skill 있으면 약 46초, 없으면 약 169초. 출력 토큰은 없으면 약 3,400개, 있으면 약 1,900개.<br/>각 3회 평균 · 시간은 최종 응답 기준 · 미사용은 중단 1회 포함. <a href="#effects">측정 근거 보기 ↗</a></p>
        </> : <>
          <h3>NASCA로 보안 처리된 Excel 파일을 읽는 시나리오입니다.</h3>
          <p>직접 여는 것은 가능하지만 Python으로는 접근하지 못했던 실제 경험에서 착안했습니다.<br/>Skill에 없는 문제를 Loop를 통해 해결하는 것이 목적입니다.</p>
          <p>오류를 감지한 Agent Skillloop가 조직 Skill Storage를 검색하지만 적합한 Skill을 찾지 못합니다.<br/>환경을 확인하고 여러 해결 방법을 시도하는 Loop를 통해 업무를 진행합니다.</p>
          <p>해결되면 그 시행착오에서 얻은 절차를 검토·Replay 후 조직 Skill Storage에 적재해, 다른 팀원이 같은 고생을 반복하지 않도록 돕습니다.</p>
          <p className="capture-scenario-effect"><strong>효과</strong> · 비교 실행에서 SkillLoop 미사용 시 업무 완료 0/3회 → 사용 시 3/3회. 새 해결 절차를 팀에 공유해 다음 팀원의 시행착오를 줄입니다.<br/>Skill 적재까지 진행한 아래 시연 영상과 비교 로그는 별도 실행입니다. <a href="#effects">측정 근거 보기 ↗</a></p>
        </>}
      </div>
      {formOpen && (
        <form className="capture-form" ref={form} onSubmit={submit}>
          <h3>{scenario.toUpperCase()} 실행 기록 등록</h3>
          <label>
            제목
            <input
              required
              maxLength={80}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="예: 사내 Python 설치 · Skill 재사용 성공"
              disabled={saving}
            />
          </label>
          <label className="capture-file">
            <ImagePlus size={20} /> 이미지 / GIF
            <input
              type="file"
              accept="image/png,image/jpeg,image/gif,image/webp"
              disabled={saving}
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <small>
              PNG · JPG · GIF · WebP / 파일당 4MB · 여러 화면은 기록을 나누어
              등록
            </small>
          </label>
          {preview && (
            <img
              className="capture-preview"
              src={preview}
              alt="등록할 이미지 미리보기"
            />
          )}
          <label>
            실행 로그 · 대화 전문
            <textarea
              rows={9}
              maxLength={60000}
              value={transcript}
              onChange={(event) => setTranscript(event.target.value)}
              placeholder="실제 질문·답변과 실행 로그를 붙여넣으세요."
              disabled={saving}
            />
          </label>
          <label className="capture-txt">
            로그 파일 불러오기 (.txt / .log)
            <input
              type="file"
              accept=".txt,.log,text/plain"
              disabled={saving}
              onChange={async (event) => {
                const txt = event.target.files?.[0];
                if (!txt) return;
                if (txt.size > 240000) {
                  setFormError("로그 파일은 240KB까지 불러올 수 있습니다.");
                  return;
                }
                try {
                  const value = await txt.text();
                  if (value.length > 60000) throw new Error();
                  setTranscript(value);
                  setFormError("");
                } catch {
                  setFormError("60,000자 이하 UTF-8 TXT 또는 LOG 파일을 선택해 주세요.");
                }
              }}
            />
          </label>
          <div className="form-bottom">
            <span>방문자에게 공개됩니다 · 등록한 브라우저에서 삭제 가능</span>
            <button
              className="button primary"
              disabled={saving || (!file && !transcript.trim())}
            >
              {saving ? "업로드 중…" : "기록 등록"}
            </button>
          </div>
          {formError && (
            <p className="notice" role="alert">
              {formError}
            </p>
          )}
        </form>
      )}
      {error && (
        <p className="notice" role="alert">
          {error}
        </p>
      )}
      {loading && <p role="status">추가 기록을 불러오는 중…</p>}
      <div className="capture-list">
        {scenario === "p0" && <>
          <P0Media />
          <CaptureCard item={repositoryP0} mine={false} bundled />
        </>}
        {scenario === "p1" && <P1Media />}
        {visible.map((item) => (
          <CaptureCard key={item.id} item={item} mine={uid === item.uid} />
        ))}
      </div>
    </section>
  );
}
