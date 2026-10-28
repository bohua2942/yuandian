import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sources import parse_feed, parse_ph, collect_hn
from store import empty_catalog, merge_batch, write_json, canonical_url
from translate import validate_translation, translate_items, TranslationError
from daily import update_source


def item(source_id="hn-123", channel="hn"):
    return {
        "sourceId": source_id, "channel": channel,
        "title": "A new open source tool", "summary": "A command-line tool for developers.",
        "url": "https://example.com/tool", "discussionUrl": "https://news.ycombinator.com/item?id=123",
        "source": "Hacker News", "publishedAt": "2026-10-27T12:00:00Z",
        "score": 100, "comments": 10,
    }


def translated(items):
    return [{**entry, "titleZh": "一个新的开源工具", "summaryZh": "面向开发者的命令行工具。", "tags": ["开发工具"], "translationStatus": "translated"} for entry in items]


class StorageTests(unittest.TestCase):
    def test_same_day_rerun_replaces_batch_without_duplicate_items(self):
        catalog = merge_batch(empty_catalog(), "hn", "2026-10-28", translated([item()]), "2026-10-28T01:00:00Z")
        newer = translated([item()])
        newer[0]["score"] = 150
        result = merge_batch(catalog, "hn", "2026-10-28", newer, "2026-10-28T02:00:00Z")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["score"], 150)
        self.assertEqual(len(result["batches"]), 1)

    def test_new_day_preserves_previous_snapshot_and_other_sources(self):
        catalog = merge_batch(empty_catalog(), "hn", "2026-10-27", translated([item()]), "2026-10-27T01:00:00Z")
        catalog = merge_batch(catalog, "ai", "2026-10-27", translated([item("ai-456", "ai")]), "2026-10-27T01:00:00Z")
        result = merge_batch(catalog, "hn", "2026-10-28", translated([item()]), "2026-10-28T01:00:00Z")
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual({entry["date"] for entry in result["items"]}, {"2026-10-27", "2026-10-28"})
        self.assertEqual(len({entry["id"] for entry in result["items"]}), 3)

    def test_empty_collection_does_not_erase_existing_batch(self):
        catalog = merge_batch(empty_catalog(), "hn", "2026-10-28", translated([item()]), "2026-10-28T01:00:00Z")
        with self.assertRaises(ValueError):
            merge_batch(catalog, "hn", "2026-10-28", [], "2026-10-28T02:00:00Z")
        self.assertEqual(len(catalog["items"]), 1)

    def test_atomic_json_write_reads_as_complete_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            write_json(path, {"title": "中文内容"})
            self.assertEqual(json.loads(path.read_text()), {"title": "中文内容"})

    def test_canonical_url_removes_tracking_but_preserves_meaningful_query(self):
        self.assertEqual(canonical_url("https://EXAMPLE.com/tool?utm_source=rss&v=2#top"), "https://example.com/tool?v=2")


class TranslationTests(unittest.TestCase):
    def test_model_cannot_change_original_url_or_id(self):
        originals = [item()]
        reply = {"items": [{"sourceId": "hn-123", "titleZh": "开源工具", "summaryZh": "一个命令行工具。", "tags": ["工具"], "url": "https://attacker.example/"}]}
        result = validate_translation(originals, reply)
        self.assertEqual(result[0]["url"], "https://example.com/tool")
        self.assertEqual(result[0]["sourceId"], "hn-123")
        self.assertEqual(originals[0]["title"], "A new open source tool")

    def test_missing_duplicate_or_unknown_translation_ids_are_rejected(self):
        valid = {"sourceId": "hn-123", "titleZh": "开源工具", "summaryZh": "命令行工具。", "tags": []}
        for entries in [[], [valid, valid], [{**valid, "sourceId": "hn-other"}]]:
            with self.subTest(entries=entries), self.assertRaises(TranslationError):
                validate_translation([item()], {"items": entries})

    def test_english_only_model_result_is_not_successful_translation(self):
        with self.assertRaises(TranslationError):
            validate_translation([item()], {"items": [{"sourceId": "hn-123", "titleZh": "New tool", "summaryZh": "A tool.", "tags": []}]})

    def test_unchanged_content_reuses_verified_translation_without_api_key(self):
        previous = translated([item()])
        result = translate_items([item()], previous, {})
        self.assertEqual(result[0]["titleZh"], "一个新的开源工具")

    def test_changed_content_requires_new_translation(self):
        changed = {**item(), "summary": "Different product capabilities."}
        with self.assertRaises(TranslationError):
            translate_items([changed], translated([item()]), {})


class SourceTests(unittest.TestCase):
    def test_rss_deduplicates_and_filters_unsafe_links(self):
        xml = b'''<rss><channel>
          <item><title>First</title><link>https://example.com/post?utm_source=rss</link><description>&lt;p&gt;Safe &amp;amp; useful&lt;/p&gt;</description><pubDate>Tue, 27 Oct 2026 12:00:00 GMT</pubDate></item>
          <item><title>Duplicate</title><link>https://example.com/post</link><pubDate>Tue, 27 Oct 2026 12:00:00 GMT</pubDate></item>
          <item><title>Bad</title><link>javascript:alert(1)</link></item>
        </channel></rss>'''
        result = parse_feed(xml, "Test Feed")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["summary"], "Safe & useful")
        self.assertEqual(result[0]["publishedAt"], "2026-10-27T12:00:00Z")

    def test_atom_feed_preserves_alternate_link_and_publication_time(self):
        xml = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Article</title><link rel="self" href="https://example.com/feed/1"/><link rel="alternate" href="https://example.com/article"/><summary>Hello</summary><published>2026-10-27T10:00:00Z</published></entry></feed>'''
        result = parse_feed(xml, "Atom")
        self.assertEqual(result[0]["url"], "https://example.com/article")
        self.assertEqual(result[0]["publishedAt"], "2026-10-27T10:00:00Z")

    def test_graphql_errors_do_not_become_empty_success(self):
        with self.assertRaises(ValueError):
            parse_ph({"errors": [{"message": "Unauthorized"}]})

    def test_hn_filters_dead_items_and_keeps_ask_hn_links(self):
        def fetch(url, **kwargs):
            if url.endswith("topstories.json"):
                return [1, 2]
            if url.endswith("/1.json"):
                return {"id": 1, "type": "story", "title": "Ask HN: Tool?", "score": 20, "time": 1793102400, "descendants": 2}
            return {"id": 2, "type": "story", "title": "Removed", "dead": True}
        result = collect_hn(2, fetch)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], "https://news.ycombinator.com/item?id=1")


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = merge_batch(empty_catalog(), "hn", "2026-10-27", translated([item()]), "2026-10-27T01:00:00Z")

    def test_translation_failure_preserves_published_content(self):
        original = copy.deepcopy(self.catalog["items"])
        def fail(items, cache):
            raise TranslationError("Invalid response")
        result, report = update_source(self.catalog, "hn", "2026-10-28", lambda: [item()], fail, "2026-10-28T01:00:00Z")
        self.assertEqual(result["items"], original)
        self.assertEqual(report["state"], "error")
        self.assertEqual(result["status"]["hn"]["lastSuccessAt"], "2026-10-27T01:00:00Z")

    def test_collection_failure_never_creates_mock_items(self):
        def fail():
            raise OSError("network unavailable")
        result, report = update_source(self.catalog, "hn", "2026-10-28", fail, lambda items, cache: translated(items), "2026-10-28T01:00:00Z")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(report["state"], "error")

    def test_successful_source_can_publish_after_another_source_fails(self):
        result, report = update_source(self.catalog, "ai", "2026-10-28", lambda: [item("ai-1", "ai")], lambda entries, cache: translated(entries), "2026-10-28T01:00:00Z")
        self.assertEqual(report["state"], "ok")
        self.assertEqual(len(result["items"]), 2)


if __name__ == "__main__":
    unittest.main()
