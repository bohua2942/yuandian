"""Official API and RSS adapters. Failures never create replacement stories."""
import hashlib
import html
import json
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from store import canonical_url


def request_bytes(url, *, headers=None, body=None):
    request_headers = {"User-Agent": "SourceDaily/0.1 (+RSS reader)", **(headers or {})}
    for attempt in range(3):
        try:
            request = Request(url, data=body, headers=request_headers)
            with urlopen(request, timeout=30) as response:
                data = response.read(8_000_001)
                if len(data) > 8_000_000:
                    raise ValueError("来源响应超过 8 MB，已停止读取")
                return data
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f"来源请求失败（HTTP {error.code}）") from None
        except (URLError, TimeoutError, OSError, HTTPException):
            if attempt == 2:
                raise RuntimeError("来源网络连接失败或超时") from None
        time.sleep(2 ** attempt)


def request_json(url, *, headers=None, payload=None):
    if payload is not None:
        headers = {**(headers or {}), "Content-Type": "application/json"}
    raw = request_bytes(url, headers=headers, body=json.dumps(payload).encode() if payload is not None else None)
    return json.loads(raw)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, value):
        self.parts.append(value)


def plain_text(value):
    parser = PlainText()
    parser.feed(html.unescape(value or ""))
    return " ".join(" ".join(parser.parts).split())[:4000]


def iso_date(value):
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        try:
            date = parsedate_to_datetime(value)
        except (ValueError, TypeError, IndexError):
            return None
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    return date.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_feed(raw, name):
    root = ET.fromstring(raw)
    entries = root.findall(".//item")
    atom = "{http://www.w3.org/2005/Atom}"
    if not entries:
        entries = root.findall(f"{atom}entry")
    results, seen = [], set()
    for entry in entries:
        def value(tag):
            return entry.findtext(tag) or entry.findtext(f"{atom}{tag}") or ""
        link = value("link")
        if not link:
            links = entry.findall(f"{atom}link")
            link = next((node.attrib.get("href", "") for node in links if node.attrib.get("rel", "alternate") == "alternate"), "")
        try:
            url = canonical_url(link)
        except ValueError:
            continue
        if url in seen or not value("title").strip():
            continue
        seen.add(url)
        published = iso_date(value("pubDate") or value("published") or value("updated"))
        if not published:
            continue
        results.append({
            "sourceId": f"ai-{hashlib.sha256(url.encode()).hexdigest()[:16]}", "channel": "ai",
            "title": plain_text(value("title")), "summary": plain_text(value("description") or value("summary") or value("content")),
            "url": url, "source": name, "publishedAt": published,
        })
    return results


def collect_ai(config, now=None):
    now = now or datetime.now(timezone.utc)
    earliest = now - timedelta(hours=config["aiMaxAgeHours"])
    entries, failed = [], []
    for feed in config["feeds"]:
        try:
            entries.extend(parse_feed(request_bytes(feed["url"]), feed["name"]))
        except (RuntimeError, ValueError, ET.ParseError):
            failed.append(feed["name"])
    if failed:
        # Never silently claim complete coverage of a broken source configuration.
        raise RuntimeError("RSS 读取失败：" + "、".join(failed))
    unique = {}
    for entry in entries:
        published = datetime.fromisoformat(entry["publishedAt"].replace("Z", "+00:00"))
        if earliest <= published <= now + timedelta(minutes=10):
            unique.setdefault(entry["url"], entry)
    return sorted(unique.values(), key=lambda entry: entry["publishedAt"], reverse=True)[:config["aiLimit"]]


def collect_hn(limit=30, fetch=request_json):
    base = "https://hacker-news.firebaseio.com/v0"
    ids = fetch(f"{base}/topstories.json")[:limit + 10]
    def story(story_id):
        entry = fetch(f"{base}/item/{story_id}.json")
        if not entry or entry.get("deleted") or entry.get("dead") or entry.get("type") != "story":
            return None
        discussion = f"https://news.ycombinator.com/item?id={entry['id']}"
        try:
            url = canonical_url(entry.get("url") or discussion)
        except ValueError:
            return None
        return {
            "sourceId": f"hn-{entry['id']}", "channel": "hn", "title": entry["title"],
            "summary": plain_text(entry.get("text", "")), "url": url, "discussionUrl": discussion,
            "source": "Hacker News", "score": entry.get("score", 0), "comments": entry.get("descendants", 0),
            "publishedAt": datetime.fromtimestamp(entry["time"], timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
    with ThreadPoolExecutor(max_workers=5) as pool:
        entries = list(pool.map(story, ids))
    return [entry for entry in entries if entry][:limit]


PH_QUERY = """query DailyPosts($start: DateTime!, $end: DateTime!, $limit: Int!) {
  posts(first: $limit, order: VOTES, postedAfter: $start, postedBefore: $end) {
    nodes { id name tagline description votesCount createdAt website url thumbnail { url } }
  }
}"""

PH_FEED_URL = "https://www.producthunt.com/feed?category=undefined"


class ProductPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.website = ""
        self.schemas = []
        self.schema_text = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("data-test") == "visit-website-button":
            self.website = attrs.get("href", "")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.schema_text = []

    def handle_data(self, data):
        if self.schema_text is not None:
            self.schema_text.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.schema_text is not None:
            try:
                self.schemas.append(json.loads("".join(self.schema_text)))
            except ValueError:
                pass
            self.schema_text = None


def parse_ph_page(raw, source_url):
    parser = ProductPage()
    parser.feed(raw.decode("utf-8", errors="replace"))
    def objects(value):
        if isinstance(value, list):
            for child in value:
                yield from objects(child)
        elif isinstance(value, dict):
            yield value
            yield from objects(value.get("@graph", []))
    description = ""
    for schema in parser.schemas:
        for obj in objects(schema):
            if obj.get("@type") in ("Product", "SoftwareApplication", "WebApplication") and isinstance(obj.get("description"), str):
                description = obj["description"]
    result = {"description": plain_text(description)} if description else {}
    if parser.website:
        try:
            result["websiteUrl"] = canonical_url(urljoin(source_url, parser.website))
        except ValueError:
            pass
    if result:
        result["detailSourceUrl"] = canonical_url(source_url)
    return result


def enrich_ph_product(entry):
    if urlsplit(entry["url"]).hostname not in ("www.producthunt.com", "producthunt.com"):
        return entry
    try:
        details = parse_ph_page(request_bytes(entry["url"]), entry["url"])
        if details:
            details.update(detailStatus="available", detailFetchedAt=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"))
        return {**entry, **details}
    except (RuntimeError, ValueError, TypeError):
        # A missing public detail page must not erase a valid feed item.
        return entry


def parse_ph_feed(raw):
    atom = "{http://www.w3.org/2005/Atom}"
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        raise ValueError("PH 订阅 XML 不完整或无法解析") from None
    if root.tag != f"{atom}feed":
        raise ValueError("PH 订阅入口没有返回 Atom 内容")
    result, seen = [], set()
    for entry in root.findall(f"{atom}entry"):
        title = plain_text(entry.findtext(f"{atom}title") or "")
        published = iso_date(entry.findtext(f"{atom}published"))
        links = entry.findall(f"{atom}link")
        link = next((node.attrib.get("href", "") for node in links if node.attrib.get("rel", "alternate") == "alternate"), "")
        try:
            url = canonical_url(link)
        except ValueError:
            continue
        if not title or not published:
            continue
        post_id = re.search(r"Post/(\d+)$", entry.findtext(f"{atom}id") or "")
        source_id = "ph-" + (post_id.group(1) if post_id else hashlib.sha256(url.encode()).hexdigest()[:16])
        if source_id in seen:
            continue
        seen.add(source_id)
        content = entry.findtext(f"{atom}content") or entry.findtext(f"{atom}summary") or ""
        # The official feed's first paragraph is the tagline; later paragraphs are navigation.
        tagline = plain_text(re.split(r"</p\s*>", content, maxsplit=1, flags=re.IGNORECASE)[0])
        result.append({
            "sourceId": source_id, "channel": "ph", "title": title, "summary": tagline,
            "url": url, "discussionUrl": url, "source": "Product Hunt RSS", "publishedAt": published,
        })
    return result


def parse_ph(payload):
    if payload.get("errors"):
        raise ValueError("PH API 返回 GraphQL 错误，请检查 token 与访问权限")
    nodes = payload.get("data", {}).get("posts", {}).get("nodes")
    if nodes is None:
        raise ValueError("PH API 返回的数据结构不完整")
    result = []
    for entry in nodes:
        result.append({
            "sourceId": f"ph-{entry['id']}", "channel": "ph", "title": entry["name"] + " — " + entry.get("tagline", ""),
            "summary": entry.get("tagline", ""), "description": entry.get("description", ""),
            "url": canonical_url(entry.get("website") or entry["url"]), "websiteUrl": canonical_url(entry.get("website") or entry["url"]),
            "detailSourceUrl": canonical_url(entry["url"]),
            "discussionUrl": canonical_url(entry["url"]), "source": "Product Hunt",
            "score": entry.get("votesCount", 0), "publishedAt": entry["createdAt"],
            "image": (entry.get("thumbnail") or {}).get("url"),
        })
    return result


def collect_ph(day, token, limit=30):
    if not token:
        entries = parse_ph_feed(request_bytes(PH_FEED_URL))
        selected = sorted(entries, key=lambda entry: entry["publishedAt"], reverse=True)[:limit]
        with ThreadPoolExecutor(max_workers=3) as pool:
            return list(pool.map(enrich_ph_product, selected))
    start = datetime.fromisoformat(day).replace(tzinfo=timezone.utc)
    payload = request_json("https://api.producthunt.com/v2/api/graphql", headers={"Authorization": f"Bearer {token}"}, payload={
        "query": PH_QUERY,
        "variables": {"start": start.isoformat(), "end": (start + timedelta(days=1)).isoformat(), "limit": limit},
    })
    return parse_ph(payload)
