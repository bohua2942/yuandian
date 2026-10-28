"use client";
import { useEffect, useState } from "react";
import { Search, Moon, Sun } from "lucide-react";

export function SearchButton() {
  return <button className="search-trigger" onClick={() => window.dispatchEvent(new Event("source-search"))} aria-label="搜索内容"><Search size={15} /><span className="search-word">搜索</span><kbd>⌘ K</kbd></button>;
}

export function ThemeButton() {
  const [dark, setDark] = useState(false);
  useEffect(() => setDark(document.documentElement.dataset.theme === "dark"), []);
  function toggle() {
    const next = !dark;
    document.documentElement.dataset.theme = next ? "dark" : "light";
    try { localStorage.setItem("source-theme", next ? "dark" : "light"); } catch { /* Theme still works without storage. */ }
    setDark(next);
  }
  return <button className="theme-toggle" aria-label={dark ? "切换到浅色" : "切换到深色"} onClick={toggle}>{dark ? <Sun size={18} /> : <Moon size={18} />}</button>;
}
