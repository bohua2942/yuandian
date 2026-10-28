import test from "node:test";
import assert from "node:assert/strict";
import { latestBatch, itemsFor, searchItems, escapeXml, archiveParams, type Catalog, type Story } from "../lib/content.ts";

const story = (id: string, channel: Story["channel"], date: string, title: string): Story => ({
  id, sourceId: id.split("-")[0], channel, date, title, titleZh: "开源开发工具", summary: "A tool for coding", summaryZh: "一个开发工具",
  url: "https://example.com/tool", source: "Test", publishedAt: `${date}T00:00:00Z`, collectedAt: `${date}T01:00:00Z`, translationStatus: "translated", tags: ["编程"],
});
const catalog: Catalog = {
  version: 1, updatedAt: "2026-10-28T01:00:00Z", status: {},
  batches: [
    { channel: "hn", date: "2026-10-27", generatedAt: "2026-10-27T01:00:00Z", count: 1 },
    { channel: "ai", date: "2026-10-28", generatedAt: "2026-10-28T01:00:00Z", count: 1 },
  ],
  items: [story("one-2026-10-27", "hn", "2026-10-27", "Rust developer tool"), story("two-2026-10-28", "ai", "2026-10-28", "AI model release")],
};

test("a source keeps its actual latest date when another source updates", () => {
  assert.equal(latestBatch(catalog, "hn")?.date, "2026-10-27");
  assert.equal(latestBatch(catalog, "ph"), undefined);
  assert.equal(itemsFor(catalog, "hn")[0].id, "one-2026-10-27");
});
test("an explicit archive date cannot fall back to today's stories", () => {
  assert.deepEqual(itemsFor(catalog, "hn", "2026-10-26"), []);
});
test("search finds Chinese tags and English original titles", () => {
  assert.equal(searchItems(catalog, "rust")[0].id, "one-2026-10-27");
  assert.equal(searchItems(catalog, "编程").length, 2);
  assert.equal(searchItems(catalog, "不存在的内容").length, 0);
});
test("search deduplicates older snapshots of the same source story", () => {
  const newer = { ...catalog.items[0], id: "one-2026-10-28", date: "2026-10-28" };
  const result = searchItems({ ...catalog, items: [...catalog.items, newer] }, "rust");
  assert.equal(result.length, 1);
  assert.equal(result[0].date, "2026-10-28");
});
test("RSS text cannot break XML elements", () => {
  assert.equal(escapeXml('A & B <tag> "quote"'), "A &amp; B &lt;tag&gt; &quot;quote&quot;");
});
test("static archive paths come only from existing batches", () => {
  assert.deepEqual(archiveParams(catalog), [
    { channel: "hn", date: "2026-10-27" },
    { channel: "ai", date: "2026-10-28" },
  ]);
});
