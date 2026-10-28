import Link from "next/link";
import { ArrowRight, ArrowUpRight, ChevronUp, MessageCircle, Radio, Rss } from "lucide-react";
import { channels, itemsFor, latestBatch, shortDate, displayTitle, displaySummary, domain, chineseTime, type Channel, type Story } from "@/lib/content";
import { catalog } from "@/lib/data";

export function DateDisplay({ date }: { date: string }) {
  const parsed = new Date(date + "T12:00:00+08:00");
  const week = new Intl.DateTimeFormat("zh-CN", { weekday: "long", timeZone: "Asia/Shanghai" }).format(parsed);
  return <div className="date-display"><span>{shortDate(date)}</span><div><strong>{date.slice(0, 4)}</strong><span>{week}</span><span className="date-line" /></div></div>;
}

export function StoryRow({ story, rank, detailed = false }: { story: Story; rank: number; detailed?: boolean }) {
  return <article className={`story-row ${detailed ? "story-detailed" : ""}`}><span className={`story-rank ${rank <= 3 ? "top-rank" : ""}`}>{String(rank).padStart(2, "0")}</span>{story.channel === "ph" && <span className="product-avatar">{story.title.charAt(0)}</span>}<div className="story-copy"><Link className="story-title" href={`/posts/${story.id}/`}>{displayTitle(story)}<ArrowUpRight size={14} /></Link>{displaySummary(story) && <p>{displaySummary(story)}</p>}<div className="story-meta"><span>{story.source}</span>{story.channel === "hn" && <><span className="meta-separator">·</span><span>{domain(story.url)}</span></>}{story.translationStatus === "original" && <span className="original-badge">英文原文</span>}{detailed && <span className="story-tags">{story.tags?.slice(0, 3).map(tag => <span key={tag}>{tag}</span>)}</span>}</div></div><div className="story-numbers">{story.score !== undefined && <span><ChevronUp size={13} />{story.score.toLocaleString()}</span>}{detailed && story.comments !== undefined && <a href={story.discussionUrl} target="_blank" rel="noopener noreferrer" aria-label={`查看 ${story.comments} 条讨论`}><MessageCircle size={12} />{story.comments}</a>}</div></article>;
}

export function EmptyState({ channel }: { channel: Channel }) {
  return <div className="empty-state"><span className={`channel-mark mark-${channel}`}>{channels.find(entry => entry.id === channel)?.mark}</span><div><h3>{channel === "ph" ? "下一款好产品，正在路上" : channel === "weekly" ? "好内容，值得慢慢整理" : "这一期正在准备中"}</h3><p>{channel === "weekly" ? "这里将收录每周精选的工具、想法与独立开发实践。" : "栏目有新内容后会在这里展示。先看看其他栏目吧。"}</p></div></div>;
}

export function NewsSection({ channel, limit = 6 }: { channel: Channel; limit?: number }) {
  const definition = channels.find(entry => entry.id === channel)!;
  const entries = itemsFor(catalog, channel);
  const batch = latestBatch(catalog, channel);
  return <section className="news-section" aria-label={definition.name}><div className="section-heading"><h2><span className={`channel-mark mark-${channel}`}>{definition.mark}</span>{definition.name}<span className="section-date mono">{batch ? shortDate(batch.date) : "即将更新"}</span></h2><Link href={`/${channel}/`}>{entries.length ? `全部 ${entries.length} ${channel === "ph" ? "款" : "条"}` : "进入栏目"}<ArrowRight size={15} /></Link></div><div className="story-card">{entries.length ? entries.slice(0, limit).map((story, index) => <StoryRow key={story.id} story={story} rank={index + 1} />) : <EmptyState channel={channel} />}</div></section>;
}

export function Sidebar() {
  const last = latestBatch(catalog);
  return <aside className="sidebar"><div className="sidebar-card directory-card"><div className="card-eyebrow"><span className="live-dot" />今日栏目<span className="mono">INDEX</span></div><div className="directory-list">{channels.map(channel => {
    const batch = latestBatch(catalog, channel.id);
    return <Link key={channel.id} href={`/${channel.id}/`}><span className={`directory-symbol mark-${channel.id}`}>{channel.mark}</span><div><strong>{channel.name}</strong><span>{batch ? `${batch.count} ${channel.id === "ph" ? "款新品" : "条内容"}` : channel.id === "weekly" ? "每周精选" : "准备中"}</span></div><span className="directory-date mono">{batch ? shortDate(batch.date) : "—"}</span></Link>;
  })}</div><Link href="/archive/" className="directory-archive">浏览往期归档<ArrowUpRight size={14} /></Link></div><div className="sidebar-card reading-note"><span className="card-eyebrow">给创造者的一句话</span><div className="note-asterisk">✳</div><p>好点子，<br />始于保持好奇。</p><span className="note-caption">少一点信息噪音，<br />多一点动手的灵感。</span><Link href="/weekly/">去读独立周刊<ArrowUpRight size={15} /></Link><span className="note-grid" aria-hidden="true" /></div><a href="/feed.xml" className="rss-card"><span className="rss-icon"><Rss size={21} /></span><div><strong>把信息源，装进口袋。</strong><span>用 RSS 订阅，按自己的节奏阅读。</span></div><ArrowUpRight size={17} /></a><div className="sidebar-footnote"><Radio size={13} /><span>{last ? `最近整理于 ${chineseTime(last.generatedAt)}` : "每日整理，持续更新"}<br />每天一份，保持独立思考。</span></div></aside>;
}
