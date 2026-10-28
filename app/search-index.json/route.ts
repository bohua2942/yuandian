import { catalog } from "@/lib/data";

export const dynamic = "force-static";
export function GET() {
  const seen = new Set<string>();
  const items = [...catalog.items].sort((a, b) => b.date.localeCompare(a.date)).filter(story => {
    if (seen.has(story.sourceId)) return false;
    seen.add(story.sourceId);
    return true;
  }).map(story => ({ ...story, summary: story.summary.slice(0, 400), summaryZh: story.summaryZh?.slice(0, 400) }));
  return Response.json({ ...catalog, items, status: {}, batches: [] });
}
