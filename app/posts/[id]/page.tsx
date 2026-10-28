import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowUpRight, ChevronUp, MessageCircle, Link2 } from "lucide-react";
import { channels, displayTitle, displaySummary, domain, chineseTime } from "@/lib/content";
import { catalog } from "@/lib/data";
import { Sidebar } from "@/components/content";

export function generateStaticParams() { return catalog.items.map(story => ({ id: story.id })); }
export const dynamicParams = false;
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const story = catalog.items.find(entry => entry.id === id);
  return { title: story ? displayTitle(story) : "内容", description: story ? displaySummary(story) : undefined };
}
export default async function StoryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const story = catalog.items.find(entry => entry.id === id);
  if (!story) notFound();
  const definition = channels.find(channel => channel.id === story.channel)!;
  return <div className="page-container home-layout"><article className="main-column article-column"><Link href={`/${story.channel}/`} className="back-link"><ArrowLeft size={14} />返回{definition.name}</Link><div className="article-header"><div className="article-eyebrow"><span className={`channel-mark mark-${story.channel}`}>{definition.mark}</span><span className="mono">{definition.english}</span><span>{story.date}</span></div><h1>{displayTitle(story)}</h1>{story.titleZh && <p className="article-original-title">{story.title}</p>}<div className="article-stats"><span>{story.source}</span>{story.score !== undefined && <span><ChevronUp size={14} />{story.score} 票</span>}{story.comments !== undefined && <span><MessageCircle size={14} />{story.comments} 条讨论</span>}</div></div><div className="article-body"><div className="article-summary"><span className="card-eyebrow">内容摘要</span><p>{displaySummary(story) || "来源未提供摘要，可以打开原文继续阅读。"}</p></div>{story.tags?.length ? <div className="article-tags">{story.tags.map(tag => <span key={tag}># {tag}</span>)}</div> : null}<div className="article-source"><Link2 size={17} /><div><strong>从一手来源，继续探索。</strong><span>{domain(story.url)} · 发布于 {chineseTime(story.publishedAt)}</span></div><a href={story.url} target="_blank" rel="noopener noreferrer">阅读原文<ArrowUpRight size={15} /></a></div>{story.discussionUrl && story.discussionUrl !== story.url && <a className="discussion-link" href={story.discussionUrl} target="_blank" rel="noopener noreferrer">查看 {story.source} 上的讨论<ArrowUpRight size={14} /></a>}<div className="translation-note">{story.translationStatus === "translated" ? "中文内容由 AI 基于来源标题及摘要整理，重要信息请以原文为准。" : story.translationStatus === "editorial" ? "首批中文内容在项目初始化时整理，保留原始标题与链接；后续内容由每日翻译任务生成。" : "当前为采集到的英文原文，尚未完成中文翻译。"}<br />整理时间：{chineseTime(story.collectedAt)}（北京时间）</div></div></article><Sidebar /></div>;
}
