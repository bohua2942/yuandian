import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowUpRight, CalendarDays } from "lucide-react";
import { channels, itemsFor, latestBatch, datesFor, chineseTime, type Channel } from "@/lib/content";
import { catalog } from "@/lib/data";
import { DateDisplay, EmptyState, Sidebar, StoryRow } from "@/components/content";

export function generateStaticParams() { return channels.map(channel => ({ channel: channel.id })); }
export const dynamicParams = false;
export async function generateMetadata({ params }: { params: Promise<{ channel: string }> }): Promise<Metadata> {
  const { channel } = await params;
  return { title: channels.find(entry => entry.id === channel)?.name || "栏目" };
}

export default async function ChannelPage({ params }: { params: Promise<{ channel: string }> }) {
  const { channel } = await params;
  const definition = channels.find(entry => entry.id === channel);
  if (!definition) notFound();
  const entries = itemsFor(catalog, definition.id);
  const batch = latestBatch(catalog, definition.id);
  const dates = datesFor(catalog, definition.id);
  const status = catalog.status[channel as Channel];
  const editionLabel = channel === "ph" ? (entries.some(story => story.source === "Product Hunt RSS") ? "官方订阅快照 · 按发布时间排序，不含票数" : "前一完整 UTC 日榜单") : channel === "hn" ? "采集时刻热榜快照" : channel === "weekly" ? "人工精选周刊" : "近 72 小时来源精选";
  return <div className="page-container home-layout"><div className="main-column"><Link className="back-link" href="/"><ArrowLeft size={14} />回到今日精选</Link><section className="channel-hero"><span className="hero-eyebrow mono">{definition.english} · DAILY EDITION</span><h1>{definition.name}<span className="title-period">.</span></h1><p>{definition.description}</p>{batch && <><DateDisplay date={batch.date} /><div className="edition-meta"><span>{entries.length} {channel === "ph" ? "款产品" : "条内容"}</span><span>{editionLabel}</span><span>整理于 {chineseTime(batch.generatedAt)}</span></div></>}</section>{status?.state === "error" && <p className="source-notice">本期更新暂未完成，以下保留上次成功整理的内容。</p>}<div className="archive-tabs"><span><CalendarDays size={14} />往期</span>{dates.map(date => <Link className={date === batch?.date ? "selected" : ""} key={date} href={`/${channel}/${date}/`}>{date}</Link>)}{!dates.length && <span className="muted">首期内容整理后开放</span>}</div><div className="story-card channel-story-card">{entries.length ? entries.map((story, index) => <StoryRow key={story.id} story={story} rank={index + 1} detailed />) : <EmptyState channel={definition.id} />}</div><a className="all-archive-link" href="/feed.xml">用 RSS 订阅后续内容<ArrowUpRight size={14} /></a></div><Sidebar /></div>;
}
