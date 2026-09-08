import { useEffect, useRef, useState, type ReactNode } from "react";
import { ArrowUpRight, ExternalLink, MessageSquare, X } from "lucide-react";
import { fetchComments } from "./api";
import { STAGES, type StageId } from "./stages";
import {
  checklist,
  cleanTitle,
  composeUrl,
  formatDate,
  KIND_NAMES,
  REPO_URL,
  safeGithubUrl,
  STATUS_NAMES,
  statusOf,
  type Comment,
  type Issue,
  type Kind,
} from "./domain";
export function Modal({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const node = ref.current;
    node?.showModal();
    return () => node?.close();
  }, []);
  return (
    <dialog
      ref={ref}
      className="modal"
      onCancel={onClose}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="modal-inner">
        <div className="modal-heading">
          <h2>{title}</h2>
          <button
            autoFocus
            className="icon-button"
            aria-label="닫기"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>
        {children}
      </div>
    </dialog>
  );
}
export function Composer({
  kind,
  initialTitle = "",
  initialBody = "",
  initialStage,
  onClose,
}: {
  kind: Kind;
  initialTitle?: string;
  initialBody?: string;
  initialStage?: StageId;
  onClose: () => void;
}) {
  const [title, setTitle] = useState(initialTitle);
  const [track, setTrack] = useState<string>(
    STAGES.find((s) => s.id === initialStage)?.track ||
      (initialTitle.startsWith("P0")
        ? "P0"
        : initialTitle.startsWith("P1")
          ? "P1"
          : "공통"),
  );
  const [stage, setStage] = useState(initialStage || "");
  const [body, setBody] = useState(initialBody);
  const [criteria, setCriteria] = useState("");
  const [opened, setOpened] = useState(false);
  const composed =
    initialBody && kind === "diagram"
      ? body
      : `### 트랙\n${track}\n\n${stage ? `### 단계\n${stage}\n\n` : ""}### ${kind === "discussion" ? "이야기 나누고 싶은 내용" : "내용"}\n${body}\n\n### ${kind === "discussion" ? "제안 / 결정이 필요한 점" : "완료 기준"}\n${criteria || (kind === "discussion" ? "자유롭게 의견을 남겨 주세요." : "- [ ] 결과와 증거 링크 추가")}\n\n### 증거 / 관련 링크\n\n---\n디디톤 Team Hub에서 작성`;
  const url = composeUrl(kind, title, composed);
  const tooLong = url.length > 7800;
  return (
    <Modal
      title={`${KIND_NAMES[kind]} ${kind === "discussion" ? "나누기" : "등록"}`}
      onClose={onClose}
    >
      <p className="muted">
        GitHub에 등록하면 팀 전체에 공유됩니다. 마지막 등록은 GitHub에서 완료해
        주세요.
      </p>
      <div className="form">
        <label>
          제목
          <input
            autoComplete="off"
            value={title}
            maxLength={100}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={
              kind === "discussion"
                ? "함께 결정할 이야기는 무엇인가요?"
                : "무엇을 함께 진행할까요?"
            }
          />
        </label>
        {kind !== "diagram" && (
          <label>
            트랙
            <select value={track} onChange={(e) => setTrack(e.target.value)}>
              {["공통", "P0", "P1", "공유", "QA"].map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </label>
        )}
        {kind === "task" && (
          <label>
            순서도 단계
            <select
              value={stage}
              onChange={(e) => {
                const next = e.target.value as StageId | "";
                setStage(next);
                const match = STAGES.find((s) => s.id === next);
                if (match) setTrack(match.track);
              }}
            >
              <option value="">연결 안 함</option>
              {STAGES.map((s) => (
                <option value={s.id} key={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
        )}
        <label>
          {kind === "diagram" ? "설명과 Mermaid 코드" : "내용"}
          <textarea
            value={body}
            maxLength={kind === "diagram" ? 5000 : 1500}
            onChange={(e) => setBody(e.target.value)}
            placeholder="배경, 현재 상황, 도움이 필요한 부분을 적어 주세요."
            rows={kind === "diagram" ? 10 : 5}
          />
        </label>
        {kind !== "diagram" && (
          <label>
            {kind === "discussion" ? "제안 / 결정이 필요한 점" : "완료 기준"}
            <textarea
              value={criteria}
              maxLength={700}
              onChange={(e) => setCriteria(e.target.value)}
              rows={3}
              placeholder={
                kind === "discussion"
                  ? "어떤 의견이 필요한가요?"
                  : "- [ ] 무엇으로 완료를 확인하나요?"
              }
            />
          </label>
        )}
        <p className="small muted">
          공개 저장소입니다. 합성 데이터와 공유 가능한 내용만 작성해 주세요.
        </p>
        {tooLong && (
          <p className="error-text" role="alert">
            GitHub 작성 링크가 너무 깁니다. 내용을 줄이거나 GitHub에서 직접
            작성해 주세요.
          </p>
        )}
        <div className="form-actions">
          <button className="button" onClick={onClose}>
            닫기
          </button>
          {title.trim() && body.trim() && !tooLong ? (
            <a
              className="button primary"
              href={url}
              target="_blank"
              rel="noreferrer"
              onClick={() => setOpened(true)}
            >
              GitHub에서 등록 완료
              <ArrowUpRight size={16} />
            </a>
          ) : (
            <button className="button primary" disabled>
              GitHub에서 등록 완료
              <ArrowUpRight size={16} />
            </button>
          )}
        </div>
        {opened && (
          <div className="notice" role="status">
            작성 창을 열었습니다. GitHub에서 Submit new issue를 누른 뒤 돌아와
            ‘새로고침’을 눌러 주세요.
          </div>
        )}
      </div>
    </Modal>
  );
}
export function IssueDetail({
  issue,
  cachedComments,
  onClose,
}: {
  issue: Issue;
  cachedComments: Comment[];
  onClose: () => void;
}) {
  const [comments, setComments] = useState(cachedComments);
  const [state, setState] = useState("댓글을 불러오는 중…");
  useEffect(() => {
    const controller = new AbortController();
    fetchComments(issue.number, controller.signal)
      .then((data) => {
        setComments(data);
        setState("");
      })
      .catch(() => {
        if (!controller.signal.aborted)
          setState(
            "실시간 댓글을 불러오지 못했습니다. 저장된 댓글 또는 GitHub 원문을 확인하세요.",
          );
      });
    return () => controller.abort();
  }, [issue.number]);
  const check = checklist(issue.body);
  return (
    <Modal title={cleanTitle(issue.title)} onClose={onClose}>
      <div className="detail-meta">
        <span className={`status ${statusOf(issue)}`}>
          {STATUS_NAMES[statusOf(issue)]}
        </span>
        <span>
          #{issue.number} · {issue.user.login}
        </span>
        <span>{formatDate(issue.updated_at)}</span>
      </div>
      <div className="detail-body">{issue.body || "내용이 없습니다."}</div>
      {check.total > 0 && (
        <p className="small muted">
          체크리스트 {check.done} / {check.total} 완료
        </p>
      )}
      <div className="notice">
        담당자·상태는 GitHub에서 수정합니다. 진행 중은 <code>status:doing</code>
        , 도움 필요는 <code>status:blocked</code>, 완료는 Close as completed를
        사용하세요.
      </div>
      <a
        className="button"
        href={safeGithubUrl(issue.html_url)}
        target="_blank"
        rel="noreferrer"
      >
        <ExternalLink size={16} />
        GitHub 원문 · 담당자 / 상태 수정
      </a>
      <div className="comments">
        <h3>
          <MessageSquare size={18} />팀 의견 <span>{comments.length}</span>
        </h3>
        {state && (
          <p className="muted small" role="status">
            {state}
          </p>
        )}
        {!comments.length && !state && (
          <p className="empty-copy">
            아직 댓글이 없어요. 첫 의견을 남겨 주세요.
          </p>
        )}
        {comments.map((c) => (
          <article className="comment" key={c.id}>
            <div>
              <strong>{c.user.login}</strong>
              <time>{formatDate(c.created_at)}</time>
            </div>
            <p>{c.body}</p>
          </article>
        ))}
        <a
          className="button primary"
          href={`${safeGithubUrl(issue.html_url)}#new_comment_field`}
          target="_blank"
          rel="noreferrer"
        >
          GitHub에서 댓글 남기기
          <ArrowUpRight size={16} />
        </a>
      </div>
    </Modal>
  );
}
export function Help({ onClose }: { onClose: () => void }) {
  return (
    <Modal title="우리 팀, 이렇게 사용해요" onClose={onClose}>
      <div className="help-list">
        <article>
          <span>01</span>
          <div>
            <h3>할 일을 등록하고 담당자를 정해요</h3>
            <p>
              ‘작업 추가’에서 내용을 작성하고 GitHub에서 등록을 완료하세요.
              Assignees에서 담당자를 지정합니다.
            </p>
          </div>
        </article>
        <article>
          <span>02</span>
          <div>
            <h3>상태를 바꾸고 결과를 남겨요</h3>
            <p>
              GitHub Labels에서 status:doing 또는 status:blocked를 선택합니다.
              검증·결과 링크를 남긴 뒤 Close as completed로 완료하세요. Not
              planned로 닫은 항목은 집계하지 않습니다.
            </p>
          </div>
        </article>
        <article>
          <span>03</span>
          <div>
            <h3>댓글로 이야기하고, 순서도로 설명해요</h3>
            <p>
              의견 탭에서는 주제별 댓글을 확인하고, 아이템 설명 탭에서는
              Mermaid를 편집해 공유할 수 있습니다. GitHub 로그인 후 작성할 수
              있으며 팀원별 권한이 적용됩니다.
            </p>
          </div>
        </article>
        <article>
          <span>04</span>
          <div>
            <h3>돌아와 새로고침하면 함께 보여요</h3>
            <p>
              공유 내용은 GitHub에 저장됩니다. 웹은 5분마다 또는 직접 새로고침할
              때 동기화합니다. 연결 오류 시 배포 시점 저장본과 날짜를
              표시합니다.
            </p>
          </div>
        </article>
      </div>
      <a
        href={`${REPO_URL}/blob/codex/team-hub/team-hub/README.md`}
        target="_blank"
        rel="noreferrer"
        className="text-button"
      >
        자세한 운영 가이드
        <ArrowUpRight size={16} />
      </a>
    </Modal>
  );
}
