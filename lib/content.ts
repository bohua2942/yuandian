export type Channel = "ph" | "hn" | "ai" | "weekly";
export type Story = {
  id: string; sourceId: string; channel: Channel; date: string;
  title: string; titleZh?: string; summary: string; summaryZh?: string;
  description?: string; descriptionZh?: string; websiteUrl?: string; detailSourceUrl?: string;
  detailStatus?: "available" | "cached"; detailFetchedAt?: string;
  url: string; discussionUrl?: string; image?: string; source: string;
  publishedAt: string; collectedAt: string; score?: number; comments?: number;
  tags?: string[]; translationStatus: "translated" | "original" | "editorial";
};
export type Batch = { channel: Channel; date: string; generatedAt: string; count: number };
export type SourceStatus = { state: string; checkedAt: string; lastSuccessAt?: string; message: string; count?: number };
export type Catalog = { version: number; updatedAt: string | null; items: Story[]; batches: Batch[]; status: Partial<Record<Channel, SourceStatus>> };

export const channels: { id: Channel; name: string; short: string; english: string; description: string; mark: string }[] = [
  { id: "ph", name: "PH 新品", short: "新品", english: "PRODUCT HUNT", description: "从 Product Hunt 发现新产品，看看创造者正在解决什么问题。", mark: "P" },
  { id: "ai", name: "AI 早报", short: "早报", english: "AI DAILY", description: "从一手来源出发，读懂 AI 领域值得关注的新进展。", mark: "✳" },
  { id: "hn", name: "HN 热榜", short: "讨论", english: "HACKER NEWS", description: "开发者社区正在讨论什么？保留热度，也保留原文。", mark: "Y" },
  { id: "weekly", name: "独立周刊", short: "周刊", english: "INDIE WEEKLY", description: "慢一点阅读。每周整理值得留下的工具、想法和实践。", mark: "↗" },
];

export function latestBatch(catalog: Catalog, channel?: Channel): Batch | undefined {
  return catalog.batches.filter(batch => !channel || batch.channel === channel).sort((a, b) => b.date.localeCompare(a.date) || b.generatedAt.localeCompare(a.generatedAt))[0];
}

export function itemsFor(catalog: Catalog, channel: Channel, date?: string): Story[] {
  const selected = date || latestBatch(catalog, channel)?.date;
  return catalog.items.filter(story => story.channel === channel && story.date === selected);
}

export function datesFor(catalog: Catalog, channel: Channel): string[] {
  return [...new Set(catalog.batches.filter(batch => batch.channel === channel).map(batch => batch.date))].sort().reverse();
}

export function archiveParams(catalog: Catalog): { channel: Channel; date: string }[] {
  return catalog.batches.map(({ channel, date }) => ({ channel, date }));
}

export function searchItems(catalog: Catalog, query: string): Story[] {
  const normalized = query.trim().toLocaleLowerCase();
  if (!normalized) return [];
  const seen = new Set<string>();
  return [...catalog.items].sort((a, b) => b.date.localeCompare(a.date)).filter(story => {
    if (seen.has(story.sourceId)) return false;
    seen.add(story.sourceId);
    return [story.title, story.titleZh, story.summary, story.summaryZh, story.source, ...(story.tags || [])].join(" ").toLocaleLowerCase().includes(normalized);
  }).slice(0, 40);
}

export function escapeXml(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

export function displayTitle(story: Story): string { return story.titleZh || story.title; }
export function displaySummary(story: Story): string { return story.summaryZh || story.summary; }
export function shortDate(value: string): string { return value.slice(5).replace("-", "."); }
export function domain(value: string): string { try { return new URL(value).hostname.replace(/^www\./, ""); } catch { return "原文"; } }
export function chineseTime(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", { timeZone: "Asia/Shanghai", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(value));
}
