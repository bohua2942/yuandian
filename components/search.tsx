"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Search, X, ArrowUpRight } from "lucide-react";
import { displayTitle, searchItems, channels, type Catalog } from "@/lib/content";

export function SearchDialog() {
  const dialog = useRef<HTMLDialogElement>(null);
  const input = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [catalog, setCatalog] = useState<Catalog>({ version: 1, updatedAt: null, items: [], batches: [], status: {} });
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const loadPromise = useRef<Promise<void> | null>(null);
  const results = searchItems(catalog, query);
  useEffect(() => {
    const open = () => {
      setQuery(""); dialog.current?.showModal(); input.current?.focus();
      if (!loadPromise.current) {
        setLoadState("loading");
        loadPromise.current = fetch("/search-index.json").then(response => {
          if (!response.ok) throw new Error("search index unavailable");
          return response.json();
        }).then((data: Catalog) => { setCatalog(data); setLoadState("ready"); }).catch(() => { setLoadState("error"); loadPromise.current = null; });
      }
    };
    const keydown = (event: KeyboardEvent) => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); if (dialog.current?.open) dialog.current.close(); else open(); } };
    window.addEventListener("source-search", open);
    window.addEventListener("keydown", keydown);
    return () => { window.removeEventListener("source-search", open); window.removeEventListener("keydown", keydown); };
  }, []);
  return <dialog ref={dialog} className="search-dialog" aria-label="搜索内容" onClick={event => { if (event.target === dialog.current) dialog.current.close(); }}><div className="search-panel"><div className="search-input-row"><Search size={20} /><input ref={input} aria-label="搜索关键词" placeholder="搜索产品、新闻、工具…" value={query} onChange={event => setQuery(event.target.value)} /><button onClick={() => dialog.current?.close()} aria-label="关闭搜索"><X size={18} /></button></div><div className="search-results">{loadState === "error" ? <div className="search-empty"><p>搜索内容暂时没有加载成功</p><span>请检查网络后重新打开搜索。</span></div> : loadState === "loading" ? <div className="search-empty"><p>正在载入搜索内容…</p></div> : !query.trim() ? <div className="search-empty"><span className="search-empty-icon">⌘</span><p>好灵感，从一个关键词开始。</p><span>支持中文、英文、产品名与标签</span></div> : results.length ? results.map(story => <Link key={story.id} href={`/posts/${story.id}/`} onClick={() => dialog.current?.close()}><span>{channels.find(channel => channel.id === story.channel)?.name} · {story.date}</span><strong>{displayTitle(story)}</strong><ArrowUpRight size={16} /></Link>) : <div className="search-empty"><p>没有找到「{query}」</p><span>换个关键词，再找找看。</span></div>}</div><div className="search-hint"><span>搜索已收录内容</span><span><kbd>esc</kbd> 关闭</span></div></div></dialog>;
}
