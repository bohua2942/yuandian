import type { Metadata } from "next";
import { Header, Footer } from "@/components/shell";
import { site } from "@/lib/data";
import { SearchDialog } from "@/components/search";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(site.url), title: { default: `${site.name} DAILY · 独立开发者的每日信息`, template: `%s · ${site.name} DAILY` },
  description: site.description, alternates: { types: { "application/rss+xml": "/feed.xml" } }, icons: { icon: "/icon.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN" suppressHydrationWarning>
    <head><script dangerouslySetInnerHTML={{ __html: `try{if(localStorage.getItem('source-theme')==='dark'||(!localStorage.getItem('source-theme')&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.dataset.theme='dark'}catch{}` }} /></head>
    <body><a href="#main" className="skip-link">跳到内容</a><Header /><main id="main">{children}</main><Footer /><SearchDialog /></body>
  </html>;
}
