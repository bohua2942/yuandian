import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { Sidebar } from "@/components/content";

export const metadata = { title: "关于源点" };
export default function About() {
  return <div className="page-container home-layout"><article className="main-column about-page"><span className="hero-eyebrow mono">HELLO, CURIOUS BUILDER.</span><h1>每个好想法，<br />都有一个起点<span className="title-period">.</span></h1><p>源点 DAILY 是为独立开发者和产品创造者整理的信息站。我们关注新产品、AI 的实际进展，以及开发者社区里值得一读的讨论。</p><h2>信息从哪里来？</h2><p>新品来自 Product Hunt，讨论来自 Hacker News。AI 栏目目前收录 OpenAI 新闻、Google AI 博客和 Hugging Face 博客。每条内容都保留原始链接，方便继续阅读和核实。</p><h2>怎样阅读这些内容？</h2><p>榜单是整理时刻的快照，热度会变化。中文摘要基于来源资料整理，不能代替原文。每个栏目标注自己的实际内容日期；更新暂时失败时，会保留上一次的内容。</p><h2>按自己的节奏订阅</h2><p>不必反复刷新。你可以用喜欢的 RSS 阅读器订阅，集中处理每天的信息。</p><a className="primary-link" href="/feed.xml">订阅 RSS<ArrowUpRight size={16} /></a><Link className="about-return" href="/">回到今日精选 →</Link></article><Sidebar /></div>;
}
