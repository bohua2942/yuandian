"""Public content storage. No credentials or raw model responses belong here."""
import copy
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CHANNELS = ("ph", "hn", "ai", "weekly")


def empty_catalog():
    return {"version": 1, "updatedAt": None, "items": [], "batches": [], "status": {}}


def canonical_url(value):
    parts = urlsplit(value.strip())
    if parts.scheme not in ("https", "http") or not parts.hostname or parts.username or parts.password:
        raise ValueError("来源链接必须是公开 HTTP(S) 地址")
    query = [(key, val) for key, val in parse_qsl(parts.query, keep_blank_values=True)
             if not key.lower().startswith("utm_") and key.lower() not in ("fbclid", "gclid")]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", urlencode(query), ""))


def merge_batch(catalog, channel, date, items, now):
    if channel not in CHANNELS or not items:
        raise ValueError("空批次不可覆盖已发布内容")
    seen = set()
    prepared = []
    for entry in items:
        source_id = entry["sourceId"]
        if not re.fullmatch(r"[a-zA-Z0-9-]+", source_id) or source_id in seen or entry["channel"] != channel:
            raise ValueError("来源 ID 重复或栏目不匹配")
        seen.add(source_id)
        public = {key: value for key, value in entry.items() if key in (
            "sourceId", "channel", "title", "titleZh", "summary", "summaryZh", "url", "discussionUrl",
            "source", "publishedAt", "score", "comments", "image", "tags", "translationStatus",
            "description", "descriptionZh", "websiteUrl", "detailSourceUrl", "detailStatus", "detailFetchedAt")}
        public["url"] = canonical_url(entry["url"])
        if public.get("discussionUrl"):
            public["discussionUrl"] = canonical_url(public["discussionUrl"])
        for key in ("websiteUrl", "detailSourceUrl"):
            if public.get(key):
                public[key] = canonical_url(public[key])
        public.update(id=f"{source_id}-{date}", date=date, collectedAt=now)
        prepared.append(public)
    result = copy.deepcopy(catalog)
    result["items"] = [entry for entry in result["items"] if not (entry["channel"] == channel and entry["date"] == date)] + prepared
    result["batches"] = [batch for batch in result["batches"] if not (batch["channel"] == channel and batch["date"] == date)]
    result["batches"].append({"channel": channel, "date": date, "generatedAt": now, "count": len(prepared)})
    result["updatedAt"] = now
    result["status"][channel] = {"state": "ok", "checkedAt": now, "lastSuccessAt": now, "message": f"已更新 {len(prepared)} 条"}
    return result


def read_catalog(path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else empty_catalog()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
