import { useEffect, useState } from "react";
import { GitBranch, MessageCircle, Flame, ArrowUpRight } from "lucide-react";
import Flow from "./Flow";
import Community from "./Community";
const tabs = [
  { id: "flow", name: "진행 순서도", icon: GitBranch },
  { id: "team", name: "팀 의견", icon: MessageCircle },
  { id: "challenge", name: "딴지 걸기", icon: Flame },
] as const;
type Tab = (typeof tabs)[number]["id"];
function readTab(): Tab {
  const hash = location.hash.slice(1);
  return hash === "team" || hash === "challenge" ? hash : "flow";
}
export default function App() {
  const [tab, setTab] = useState<Tab>(readTab);
  useEffect(() => {
    const change = () => setTab(readTab());
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  return (
    <div className="site">
      <header className="masthead">
        <div className="identity">
          <div className="team-name">
            <span className="team-symbol">N.</span>노웨어
            <span className="event-tag">제4회 디디톤</span>
          </div>
          <h1>
            Agent <span>Skillloop</span>
          </h1>
          <p>한 번 푼 문제, 팀의 다음 해결법으로.</p>
        </div>
        <img
          className="event-art"
          src={`${import.meta.env.BASE_URL}images/ddthon-banner.png`}
          width="1024"
          height="434"
          alt="제4회 디디톤 행사 배너"
        />
      </header>
      <nav className="tabs" aria-label="주 메뉴">
        {tabs.map((t) => (
          <a
            key={t.id}
            href={`#${t.id}`}
            aria-current={tab === t.id ? "page" : undefined}
            className={tab === t.id ? "active" : ""}
          >
            <t.icon size={21} />
            {t.name}
            {t.id === "challenge" && <span className="guest-badge">OPEN</span>}
          </a>
        ))}
      </nav>
      <main>
        {tab === "flow" ? <Flow /> : <Community key={tab} board={tab} />}
      </main>
      <footer>
        <span>NOWHERE · Agent Skillloop</span>
        <span>
          제4회 디디톤 <ArrowUpRight size={13} />
        </span>
      </footer>
    </div>
  );
}
