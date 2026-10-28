import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { ArrowLeft } from "lucide-react";
import { channels, itemsFor, archiveParams } from "@/lib/content";
import { catalog } from "@/lib/data";
import { Sidebar, StoryRow, DateDisplay, EmptyState } from "@/components/content";

export function generateStaticParams() { return archiveParams(catalog); }
export const dynamicParams = false;
export async function generateMetadata({ params }: { params: Promise<{ channel: string; date: string }> }): Promise<Metadata> {
  const { channel, date } = await params;
  return { title: `${channels.find(entry => entry.id === channel)?.name || "归档"} ${date}` };
}
export default async function ArchiveEdition({ params }: { params: Promise<{ channel: string; date: string }> }) {
  const { channel, date } = await params;
  const definition = channels.find(entry => entry.id === channel);
  if (!definition || !/^\d{4}-\d{2}-\d{2}$/.test(date)) notFound();
  const entries = itemsFor(catalog, definition.id, date);
  return <div className="page-container home-layout"><div className="main-column"><Link className="back-link" href={`/${channel}/`}><ArrowLeft size={14} />返回{definition.name}</Link><section className="channel-hero"><span className="hero-eyebrow mono">{definition.english} · ARCHIVE</span><h1>{definition.name}<span className="title-period">.</span></h1><DateDisplay date={date} /><p>这是 {date} 的内容归档，保留当期整理结果。</p></section><div className="story-card">{entries.length ? entries.map((story, index) => <StoryRow key={story.id} story={story} rank={index + 1} detailed />) : <EmptyState channel={definition.id} />}</div></div><Sidebar /></div>;
}
