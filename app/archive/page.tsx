import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { catalog } from "@/lib/data";
import { channels } from "@/lib/content";
import { Sidebar } from "@/components/content";

export const metadata = { title: "往期归档" };
export default function ArchivePage() {
  const dates = [...new Set(catalog.batches.map(batch => batch.date))].sort().reverse();
  return <div className="page-container home-layout"><div className="main-column"><section className="channel-hero"><span className="hero-eyebrow mono">THE DAILY ARCHIVE</span><h1>灵感有迹可循<span className="title-period">.</span></h1><p>翻一翻过去的发现，找到今天的新想法。</p></section><div className="archive-list">{dates.map(date => <section key={date}><h2>{date}</h2>{catalog.batches.filter(batch => batch.date === date).map(batch => <Link key={batch.channel} href={`/${batch.channel}/${date}/`}><span>{channels.find(channel => channel.id === batch.channel)?.name}</span><span>{batch.count} 条内容<ArrowUpRight size={15} /></span></Link>)}</section>)}{!dates.length && <p>首期内容整理后将在这里归档。</p>}</div></div><Sidebar /></div>;
}
