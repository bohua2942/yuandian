import Link from "next/link";
import { ArrowDown, ArrowUpRight } from "lucide-react";
import { DateDisplay, NewsSection, Sidebar } from "@/components/content";
import { catalog } from "@/lib/data";
import { latestBatch } from "@/lib/content";

export default function Home() {
  const date = latestBatch(catalog)?.date || new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Shanghai", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  return <div className="page-container home-layout"><div className="main-column"><section className="daily-hero"><div className="hero-eyebrow mono"><span className="accent-dot" />INDEPENDENT MINDS. DAILY FINDS.</div><div className="hero-title-row"><h1>今日灵感<span className="title-period">.</span></h1><span className="hero-stamp mono">独立开发者的<br />每日信息源</span></div><DateDisplay date={date} /><p className="hero-description">发现新产品，读懂 AI 动态，听听开发者们的讨论。<br className="desktop-break" />每天留一点时间，为下一个想法找到起点。</p><div className="hero-bottom"><a href="#daily-content"><ArrowDown size={14} />开始今天的探索</a><span>精选一手来源 · 保留原文链接</span></div></section><div id="daily-content"><NewsSection channel="ai" /><NewsSection channel="hn" /><NewsSection channel="ph" limit={5} /></div><section className="weekly-strip"><div><span className="mono">THE WEEKLY EDIT</span><h2>把值得留下的，留到周末。</h2><p>工具、产品与独立创造者的实践，每周慢慢读。</p></div><Link href="/weekly/" aria-label="阅读独立周刊"><ArrowUpRight size={25} /></Link></section></div><Sidebar /></div>;
}
