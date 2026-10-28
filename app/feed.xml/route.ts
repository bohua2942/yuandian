import { catalog, site } from "@/lib/data";
import { displayTitle, displaySummary, escapeXml } from "@/lib/content";

export const dynamic = "force-static";
export function GET() {
  const seen = new Set<string>();
  const entries = [...catalog.items].sort((a, b) => b.date.localeCompare(a.date)).filter(story => { if (seen.has(story.sourceId)) return false; seen.add(story.sourceId); return true; }).slice(0, 60);
  const xml = `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>${escapeXml(site.name)} DAILY</title><link>${escapeXml(site.url)}</link><description>${escapeXml(site.description)}</description><language>zh-CN</language>${entries.map(story => `<item><title>${escapeXml(displayTitle(story))}</title><link>${escapeXml(site.url)}/posts/${story.id}/</link><guid isPermaLink="false">${story.sourceId}</guid><description>${escapeXml(displaySummary(story) + "\n原文：" + story.url)}</description><pubDate>${new Date(story.publishedAt).toUTCString()}</pubDate></item>`).join("")}</channel></rss>`;
  return new Response(xml, { headers: { "Content-Type": "application/rss+xml; charset=utf-8" } });
}
