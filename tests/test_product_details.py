import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sources import parse_ph_page
from translate import validate_translation, translate_items, TranslationError
from store import empty_catalog, merge_batch


PAGE = b'''<html><head>
<meta name="description" content="An abbreviated metadata description."/>
<script type="application/ld+json">{"@type":"WebApplication","name":"License Tool","description":"An open-source CLI that checks direct and transitive dependency licenses across ten ecosystems. It reads lockfiles without installing dependencies."}</script>
</head><body><a data-test="visit-website-button" href="https://example.com/tool?ref=producthunt">Visit website</a></body></html>'''


def original():
    return {"sourceId": "ph-1", "channel": "ph", "title": "License Tool", "summary": "Check dependency licenses.",
            "description": "Checks direct and transitive dependencies without installing packages.",
            "url": "https://www.producthunt.com/products/tool", "websiteUrl": "https://example.com/tool",
            "detailSourceUrl": "https://www.producthunt.com/products/tool", "source": "Product Hunt RSS", "publishedAt": "2026-10-28T01:00:00Z"}


class ProductDetailTests(unittest.TestCase):
    def test_public_page_provides_full_description_and_official_website(self):
        details = parse_ph_page(PAGE, "https://www.producthunt.com/products/tool")
        self.assertIn("transitive dependency licenses", details["description"])
        self.assertIn("without installing dependencies", details["description"])
        self.assertEqual(details["websiteUrl"], "https://example.com/tool?ref=producthunt")
        self.assertEqual(details["detailSourceUrl"], "https://www.producthunt.com/products/tool")

    def test_missing_details_do_not_fabricate_product_information(self):
        details = parse_ph_page(b"<html><body>Unavailable</body></html>", "https://www.producthunt.com/products/tool")
        self.assertNotIn("description", details)
        self.assertNotIn("websiteUrl", details)

    def test_login_page_metadata_is_not_a_product_description(self):
        details = parse_ph_page(b'<html><head><meta name="description" content="Discover the best new products on Product Hunt"/></head><body>Sign in</body></html>', "https://www.producthunt.com/products/tool")
        self.assertEqual(details, {})

    def test_failed_detail_refresh_keeps_verified_description_and_original_fetch_time(self):
        previous = {**original(), "titleZh": "许可工具", "summaryZh": "检查依赖许可证。", "descriptionZh": "检查直接和传递依赖，无需安装软件包。", "tags": [], "translationStatus": "translated", "detailFetchedAt": "2026-10-27T12:00:00Z"}
        refreshed = {key: value for key, value in original().items() if key not in ("description", "websiteUrl", "detailSourceUrl")}
        result = translate_items([refreshed], [previous], {})[0]
        self.assertEqual(result["descriptionZh"], "检查直接和传递依赖，无需安装软件包。")
        self.assertEqual(result["websiteUrl"], "https://example.com/tool")
        self.assertEqual(result["detailFetchedAt"], "2026-10-27T12:00:00Z")
        self.assertEqual(result["detailStatus"], "cached")

    def test_unsafe_website_url_is_rejected(self):
        details = parse_ph_page(PAGE.replace(b"https://example.com/tool?ref=producthunt", b"javascript:alert(1)"), "https://www.producthunt.com/products/tool")
        self.assertNotIn("websiteUrl", details)

    def test_detail_translation_required_when_original_description_exists(self):
        reply = {"items": [{"sourceId": "ph-1", "titleZh": "许可工具", "summaryZh": "检查依赖许可证。", "tags": []}]}
        with self.assertRaises(TranslationError):
            validate_translation([original()], reply)

    def test_model_cannot_invent_a_full_description_without_source_text(self):
        entry = original()
        del entry["description"]
        reply = {"items": [{"sourceId": "ph-1", "titleZh": "许可工具", "summaryZh": "检查依赖许可证。", "descriptionZh": "模型凭空添加的功能。", "tags": []}]}
        translated = validate_translation([entry], reply)
        self.assertNotIn("descriptionZh", translated[0])

    def test_full_description_survives_public_storage_without_model_changing_links(self):
        reply = {"items": [{"sourceId": "ph-1", "titleZh": "许可工具", "summaryZh": "检查依赖许可证。", "descriptionZh": "检查直接和传递依赖，无需安装软件包。", "websiteUrl": "https://wrong.example/", "tags": []}]}
        translated = validate_translation([original()], reply)
        catalog = merge_batch(empty_catalog(), "ph", "2026-10-28", translated, "2026-10-28T12:00:00Z")
        self.assertEqual(catalog["items"][0]["descriptionZh"], "检查直接和传递依赖，无需安装软件包。")
        self.assertEqual(catalog["items"][0]["websiteUrl"], "https://example.com/tool")

    def test_new_description_invalidates_old_short_translation_cache(self):
        cache = {**original(), "titleZh": "许可工具", "summaryZh": "检查依赖。", "tags": [], "translationStatus": "translated"}
        del cache["description"]
        with self.assertRaises(TranslationError):
            translate_items([original()], [cache], {})


if __name__ == "__main__":
    unittest.main()
