import { useEffect, useRef, useState, type FormEvent } from "react";
import { Plus, Trash2, ImagePlus, FileText } from "lucide-react";
import { session } from "./communityApi";
import {
  loadMedia,
  loadTranscript,
  removeCapture,
  saveCapture,
  watchCaptures,
  type Capture,
} from "./captureApi";

function CaptureCard({ item, mine }: { item: Capture; mine: boolean }) {
  const [media, setMedia] = useState("");
  const [text, setText] = useState<string | null>(null);
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
      {!!item.chunks && (
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
            {open ? "실행 전문 접기" : "실행 전문 펼치기"}
            <span>{open ? "−" : "+"}</span>
          </button>
          {open && <pre>{busy ? "불러오는 중…" : text}</pre>}
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

export default function Captures() {
  const [scenario, setScenario] = useState<"p0" | "p1">("p0");
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
          <h2>캡처 정리</h2>
          <p>실제 실행 화면과 대화 전문</p>
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
            onClick={() => setScenario(value)}
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
            실행 텍스트 전문
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
            TXT 불러오기
            <input
              type="file"
              accept=".txt,text/plain"
              disabled={saving}
              onChange={async (event) => {
                const txt = event.target.files?.[0];
                if (!txt) return;
                if (txt.size > 240000) {
                  setFormError("TXT는 240KB까지 불러올 수 있습니다.");
                  return;
                }
                try {
                  const value = await txt.text();
                  if (value.length > 60000) throw new Error();
                  setTranscript(value);
                  setFormError("");
                } catch {
                  setFormError("60,000자 이하 UTF-8 TXT 파일을 선택해 주세요.");
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
      {loading ? (
        <p className="capture-empty">기록을 불러오는 중…</p>
      ) : !visible.length && !error ? (
        <div className="capture-empty">
          <ImagePlus size={32} />
          <h3>아직 {scenario.toUpperCase()} 실행 기록이 없습니다</h3>
          <p>이미지/GIF와 실행 전문을 등록해 주세요.</p>
        </div>
      ) : null}
      <div className="capture-list">
        {visible.map((item) => (
          <CaptureCard key={item.id} item={item} mine={uid === item.uid} />
        ))}
      </div>
    </section>
  );
}
