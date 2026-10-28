import Link from "next/link";
import { ArrowUpRight, Rss, Aperture } from "lucide-react";
import { channels } from "@/lib/content";
import { site } from "@/lib/data";
import { SearchButton, ThemeButton } from "./controls";

export function Brand({ footer = false }: { footer?: boolean }) {
  return <Link href="/" className={`brand ${footer ? "brand-footer" : ""}`} aria-label="源点首页"><span className="brand-icon"><Aperture size={24} strokeWidth={1.7} /></span><span>源点<span className="brand-daily">DAILY</span></span></Link>;
}

export function Header() {
  return <header className="site-header"><div className="header-inner"><Brand /><nav aria-label="主导航">{channels.map(channel => <Link key={channel.id} href={`/${channel.id}/`}>{channel.name}</Link>)}</nav><div className="header-tools"><a href="/feed.xml" className="rss-header" aria-label="订阅 RSS"><Rss size={15} /><span>RSS</span></a><SearchButton /><ThemeButton /></div></div></header>;
}

export function Footer() {
  return <footer className="site-footer"><div className="footer-top"><div className="footer-about"><Brand footer /><p>{site.description}</p><span className="mono footer-motto">FIND SOMETHING WORTH BUILDING.</span></div><div className="footer-links"><h3>探索内容</h3>{channels.map(channel => <Link key={channel.id} href={`/${channel.id}/`}>{channel.name}<ArrowUpRight size={12} /></Link>)}</div><div className="footer-links"><h3>保持连接</h3><a href="/feed.xml">RSS 订阅<ArrowUpRight size={12} /></a><Link href="/about/">关于源点<ArrowUpRight size={12} /></Link><Link href="/archive/">往期归档<ArrowUpRight size={12} /></Link></div></div><div className="footer-bottom"><span>© {new Date().getFullYear()} 源点 DAILY</span><span>保持好奇，持续创造。<span className="footer-dot">●</span></span><span>内容保留来源，观点留给你。</span></div></footer>;
}
