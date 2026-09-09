import { useEffect, useState } from "react";
import {
  GitBranch,
  MessageCircle,
  Flame,
  ArrowUpRight,
  Play,
  Images,
  House,
  BarChart3,
  BadgeCheck,
  BookOpen,
} from "lucide-react";
import Flow from "./Flow";
import Community from "./Community";
import Demo from "./Demo";
import Captures from "./Captures";
import Overview from "./Overview";
import Effects from "./Effects";
import QA from "./QA";
import ExampleSkills from "./ExampleSkills";
const tabs = [
  { id: "overview", name: "개요", icon: House },
  { id: "captures", name: "시연 영상 및 캡쳐", icon: Images },
  { id: "effects", name: "효과", icon: BarChart3 },
  { id: "flow", name: "진행 순서도", icon: GitBranch },
  { id: "qa", name: "QA 검증", icon: BadgeCheck },
  { id: "skills", name: "예시 스킬", icon: BookOpen },
  { id: "team", name: "팀 의견", icon: MessageCircle },
  { id: "challenge", name: "태클 걸기", icon: Flame },
  { id: "demo", name: "모의 진행", icon: Play },
] as const;
type Tab = (typeof tabs)[number]["id"];
function readTab(): Tab {
  const hash = location.hash.slice(1);
  if (hash === "demo" || hash === "demo-p0" || hash === "demo-p1")
    return "demo";
  if (["captures", "captures-p0", "captures-p1"].includes(hash)) return "captures";
  if (hash === "effects") return "effects";
  if (hash === "qa") return "qa";
  if (hash === "skills") return "skills";
  if (hash === "flow" || hash === "team" || hash === "challenge") return hash;
  return "overview";
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
        <div className="event-banner">
          <div className="event-banner-copy">
            <span>DS S/W DEVELOPER HACKATHON</span>
            <strong>제4회 디디톤</strong>
            <p>Humans set the direction. AI brings the speed.</p>
          </div>
          <img
            className="event-banner-art"
            src={`${import.meta.env.BASE_URL}images/ddthon-banner.png`}
            width="1024"
            height="434"
            alt="제4회 디디톤 행사 배너"
          />
        </div>
        <div className="brand-heading">
          <a
            className="nowhere-logo"
            href="#overview"
            aria-label="노웨어 · 개요"
          >
            <img
              src={`${import.meta.env.BASE_URL}images/nowhere-logo.png`}
              alt="노웨어 NOWHERE 로고"
              width="1726"
              height="911"
            />
          </a>
          <div className="identity">
            <div className="team-name">
              노웨어 <span className="event-tag">제4회 디디톤</span>
            </div>
            <h1>
              Agent <span>Skillloop</span>
            </h1>
            <p>한 번 푼 문제, 팀의 다음 해결법으로.</p>
          </div>
        </div>
      </header>
      <nav className="tabs" aria-label="주 메뉴">
        {tabs.map((t) => (
          <a
            key={t.id}
            href={t.id === "demo" ? "#demo-p0" : `#${t.id}`}
            aria-current={tab === t.id ? "page" : undefined}
            className={tab === t.id ? "active" : ""}
          >
            <t.icon size={21} />
            {t.name}
          </a>
        ))}
      </nav>
      <main>
        {tab === "overview" ? (
          <Overview />
        ) : tab === "effects" ? (
          <Effects />
        ) : tab === "flow" ? (
          <Flow />
        ) : tab === "demo" ? (
          <Demo initialScenario={location.hash === "#demo-p1" ? "p1" : "p0"} />
        ) : tab === "captures" ? (
          <Captures initialScenario={location.hash === "#captures-p1" ? "p1" : "p0"} />
        ) : tab === "qa" ? (
          <QA />
        ) : tab === "skills" ? (
          <ExampleSkills />
        ) : (
          <Community key={tab} board={tab} />
        )}
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
