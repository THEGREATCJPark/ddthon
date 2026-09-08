import { useEffect, useState, type FormEvent } from "react";
import {
  CornerDownRight,
  Flame,
  MessageCircle,
  Send,
  Trash2,
} from "lucide-react";
import {
  removeMessage,
  sendMessage,
  session,
  watchMessages,
  watchOwned,
} from "./communityApi";
import { SAMPLE, type Board, type Message } from "./workspace";

function CommentForm({
  board,
  parentId = "",
  onSent,
  onCancel,
}: {
  board: Board;
  parentId?: string;
  onSent: () => void;
  onCancel?: () => void;
}) {
  const [body, setBody] = useState("");
  const [name, setName] = useState(() => {
    try {
      return localStorage.getItem("nowhere.name") || "";
    } catch {
      return "";
    }
  });
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (sending) return;
    setSending(true);
    setError("");
    try {
      await sendMessage(board, body, name, parentId);
      try {
        if (board === "team") localStorage.setItem("nowhere.name", name.trim());
      } catch {}
      setBody("");
      onSent();
    } catch (e) {
      setError(
        e instanceof Error && e.message.startsWith("의견은")
          ? e.message
          : "등록하지 못했습니다. 연결을 확인하고 잠시 후 다시 눌러주세요.",
      );
    } finally {
      setSending(false);
    }
  }
  return (
    <form
      className={`comment-form ${parentId ? "reply-form" : ""}`}
      onSubmit={submit}
    >
      {board === "team" && (
        <input
          className="name-input"
          aria-label="이름"
          placeholder="이름"
          maxLength={20}
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      )}
      <textarea
        aria-label={parentId ? "답글 내용" : "의견 내용"}
        placeholder={
          parentId
            ? "답글을 남겨주세요"
            : board === "challenge"
              ? "이건 좀 별론데… 왜 그렇게 생각하는지 들려주세요."
              : "아이디어, 질문, 지금 막힌 것. 편하게 남겨주세요."
        }
        value={body}
        onChange={(e) => setBody(e.target.value)}
        maxLength={1000}
        rows={parentId ? 2 : 3}
        required
      />
      <div className="form-bottom">
        <span>
          {board === "challenge"
            ? "이름 없이 익명으로 남겨집니다"
            : "팀 의견은 방문자도 볼 수 있습니다"}
        </span>
        <div>
          {onCancel && (
            <button type="button" onClick={onCancel}>
              취소
            </button>
          )}
          <button
            className={`button ${board === "challenge" ? "gold" : "primary"}`}
            disabled={
              sending || !body.trim() || (board === "team" && !name.trim())
            }
          >
            <Send size={16} />
            {sending
              ? "보내는 중…"
              : parentId
                ? "답글 남기기"
                : board === "challenge"
                  ? "태클 걸기"
                  : "의견 남기기"}
          </button>
        </div>
      </div>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
    </form>
  );
}
export default function Community({ board }: { board: Board }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [owned, setOwned] = useState(new Set<string>());
  const [reply, setReply] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    setLoading(true);
    return watchMessages(
      board,
      (data) => {
        setMessages(data);
        setError("");
        setLoading(false);
      },
      () => {
        setError("의견을 불러오지 못했습니다.");
        setLoading(false);
      },
    );
  }, [board, retry]);
  useEffect(() => {
    let active = true;
    let unsubscribe = () => {};
    session()
      .then((u) => {
        if (active) unsubscribe = watchOwned(u.uid, setOwned);
      })
      .catch(() => {});
    return () => {
      active = false;
      unsubscribe();
    };
  }, []);
  useEffect(() => {
    if (!sent) return;
    const timer = setTimeout(() => setSent(false), 3500);
    return () => clearTimeout(timer);
  }, [sent]);
  const all = board === "challenge" ? [...messages, SAMPLE] : messages;
  const roots = all.filter((m) => !m.parentId);
  for (const m of messages) {
    if (
      m.parentId &&
      !all.some((parent) => parent.id === m.parentId) &&
      !roots.some((r) => r.id === m.parentId)
    )
      roots.push({
        id: m.parentId,
        board,
        name: "이전 댓글",
        body: "원문이 삭제되었거나 최근 목록에 포함되지 않은 댓글입니다.",
        parentId: "",
        createdAt: 0,
      });
  }
  async function remove(id: string) {
    setDeleting(id);
    try {
      await removeMessage(id);
      setError("");
    } catch {
      setError("삭제하지 못했습니다. 본인이 작성한 글인지 확인해 주세요.");
    } finally {
      setDeleting(null);
    }
  }
  function messageCard(m: Message, nested = false) {
    return (
      <div className={`comment ${nested ? "reply" : ""}`} key={m.id}>
        <div className={`avatar ${board === "challenge" ? "anonymous" : ""}`}>
          {board === "challenge" ? "?" : m.name.slice(0, 1)}
        </div>
        <div className="comment-content">
          <div className="comment-meta">
            <strong>{m.name}</strong>
            {m.sample ? (
              <span className="sample-tag">샘플</span>
            ) : (
              m.createdAt > 0 && (
                <time>
                  {new Date(m.createdAt).toLocaleString("ko-KR", {
                    month: "numeric",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </time>
              )
            )}
            {owned.has(m.id) && (
              <button
                className="icon-button delete-comment"
                disabled={deleting === m.id}
                aria-label="내 댓글 삭제"
                onClick={() => remove(m.id)}
              >
                <Trash2 size={15} />
              </button>
            )}
          </div>
          <p className="comment-body">{m.body}</p>
          {!nested && (
            <button
              className="reply-button"
              onClick={() => setReply(reply === m.id ? null : m.id)}
            >
              <CornerDownRight size={15} />
              답글
              {all.filter((r) => r.parentId === m.id).length > 0 && (
                <span>{all.filter((r) => r.parentId === m.id).length}</span>
              )}
            </button>
          )}
        </div>
      </div>
    );
  }
  return (
    <section className={`community-page ${board}`}>
      <div className="page-heading">
        <div>
          <div className="section-kicker">
            {board === "team" ? "TEAM TALK" : "CHALLENGE US"}
          </div>
          <h2>{board === "team" ? "우리 팀의 한마디." : "태클 환영."}</h2>
          <p>
            {board === "team"
              ? "길게 정리하지 않아도 괜찮아요. 댓글로 이야기해요."
              : "맵게 한마디 남겨주세요."}
          </p>
        </div>
        {board === "challenge" ? (
          <Flame className="section-symbol" size={54} />
        ) : (
          <MessageCircle className="section-symbol" size={54} />
        )}
      </div>
      <CommentForm board={board} onSent={() => setSent(true)} />
      <div className="thread-heading">
        <h3>
          {board === "team" ? "의견" : "받은 태클"}{" "}
          <span>{messages.filter((m) => !m.parentId).length}</span>
        </h3>
        <span className="muted">
          {loading ? "불러오는 중…" : "댓글과 답글"}
        </span>
      </div>
      {error && (
        <div className="notice" role="alert">
          {error}
          <button onClick={() => setRetry((v) => v + 1)}>다시 연결</button>
        </div>
      )}
      {!loading && !roots.length && !error && (
        <div className="empty">
          <MessageCircle size={32} />
          <p>첫 의견을 남겨주세요.</p>
        </div>
      )}
      <div className="threads">
        {roots.map((root) => (
          <article className="thread" key={root.id}>
            {messageCard(root)}
            <div className="replies">
              {all
                .filter((m) => m.parentId === root.id)
                .sort((a, b) => a.createdAt - b.createdAt)
                .map((m) => messageCard(m, true))}
            </div>
            {reply === root.id && (
              <CommentForm
                board={board}
                parentId={root.id}
                onCancel={() => setReply(null)}
                onSent={() => {
                  setReply(null);
                  setSent(true);
                }}
              />
            )}
          </article>
        ))}
      </div>
      {messages.length >= 200 && (
        <p className="muted recent-note">
          최근 댓글과 답글 200개를 표시합니다.
        </p>
      )}
      {sent && (
        <div className="toast" role="status">
          의견이 공유되었습니다.
        </div>
      )}
    </section>
  );
}
