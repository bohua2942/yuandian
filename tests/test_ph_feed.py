import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sources import parse_ph_feed, collect_ph
from daily import update_source
from store import empty_catalog, merge_batch


FEED = b'''<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>tag:www.producthunt.com,2005:Post/200</id>
    <title>Older Product</title>
    <published>2026-10-26T09:00:00-07:00</published>
    <updated>2026-10-28T12:00:00Z</updated>
    <link rel="alternate" href="https://www.producthunt.com/products/older"/>
    <content type="html">&lt;p&gt;A local coding tool&lt;/p&gt;&lt;p&gt;&lt;a href="https://example.com"&gt;Discussion&lt;/a&gt; | Link&lt;/p&gt;</content>
  </entry>
  <entry>
    <id>tag:www.producthunt.com,2005:Post/300</id>
    <title>New Product</title>
    <published>2026-10-28T01:00:00Z</published>
    <link rel="alternate" href="https://www.producthunt.com/products/new?utm_source=feed"/>
    <content type="html">&lt;p&gt;An open source app&lt;/p&gt;</content>
  </entry>
  <entry>
    <id>tag:www.producthunt.com,2005:Post/300</id>
    <title>Duplicate</title>
    <published>2026-10-28T01:00:00Z</published>
    <link rel="alternate" href="https://www.producthunt.com/products/new"/>
  </entry>
  <entry>
    <id>tag:www.producthunt.com,2005:Post/400</id>
    <title>Unsafe link</title>
    <published>2026-10-28T02:00:00Z</published>
    <link rel="alternate" href="javascript:alert(1)"/>
  </entry>
</feed>'''


class ProductHuntFeedTests(unittest.TestCase):
    def test_feed_keeps_real_post_id_description_and_original_publication_time(self):
        entries = parse_ph_feed(FEED)
        older = next(entry for entry in entries if entry["sourceId"] == "ph-200")
        self.assertEqual(older["channel"], "ph")
        self.assertEqual(older["summary"], "A local coding tool")
        self.assertEqual(older["publishedAt"], "2026-10-26T16:00:00Z")
        self.assertEqual(older["source"], "Product Hunt RSS")
        self.assertNotIn("score", older)
        self.assertNotIn("comments", older)

    def test_feed_deduplicates_source_ids_and_rejects_unsafe_links(self):
        entries = parse_ph_feed(FEED)
        self.assertEqual(len(entries), 2)
        self.assertEqual({entry["sourceId"] for entry in entries}, {"ph-200", "ph-300"})
        self.assertEqual(next(entry for entry in entries if entry["sourceId"] == "ph-300")["url"], "https://www.producthunt.com/products/new")

    def test_missing_token_collects_official_feed_sorted_by_publication(self):
        with patch("sources.request_bytes", return_value=FEED):
            entries = collect_ph("2026-10-27", "", limit=1)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["sourceId"], "ph-300")
        self.assertNotIn("score", entries[0])

    def test_html_response_is_not_a_successful_empty_feed(self):
        with self.assertRaises(ValueError):
            parse_ph_feed(b"<html><body>Sign in</body></html>")

    def test_invalid_api_token_does_not_silently_fall_back_to_rss(self):
        with patch("sources.request_json", side_effect=RuntimeError("API rejected request")):
            with self.assertRaises(RuntimeError):
                collect_ph("2026-10-27", "local-test-token", 1)

    def test_truncated_atom_response_is_reported_as_a_source_failure(self):
        previous = merge_batch(empty_catalog(), "ph", "2026-10-27", parse_ph_feed(FEED), "2026-10-27T16:00:00Z")
        with patch("sources.request_bytes", return_value=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry>'):
            result, report = update_source(previous, "ph", "2026-10-28", lambda: collect_ph("2026-10-27", ""), lambda entries, cache: entries, "2026-10-28T13:00:00Z")
        self.assertEqual(report["state"], "error")
        self.assertEqual(result["items"], previous["items"])
        self.assertEqual(len(result["batches"]), 1)


if __name__ == "__main__":
    unittest.main()
