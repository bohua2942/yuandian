#!/usr/bin/env python3
"""Collect -> validate translation -> atomically publish; credentials stay local."""
import argparse
import copy
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sources import collect_ai, collect_hn, collect_ph
from store import read_catalog, write_json, merge_batch
from translate import translate_items

ROOT = Path(__file__).resolve().parents[1]


def update_source(catalog, channel, date, collect, translate, now):
    result = copy.deepcopy(catalog)
    try:
        items = collect()
        if not items:
            report = {"state": "unchanged", "checkedAt": now, "message": "暂无新内容，保留上一期", "count": 0}
            result["status"][channel] = {**result["status"].get(channel, {}), **report}
            return result, report
        translated = translate(items, catalog["items"])
        result = merge_batch(catalog, channel, date, translated, now)
        return result, {**result["status"][channel], "count": len(translated)}
    except (RuntimeError, ValueError, OSError, KeyError, TypeError):
        # Error strings can contain upstream response bodies; never persist them.
        report = {"state": "error", "checkedAt": now, "message": "采集或翻译失败，保留上次成功内容；请检查配置和来源连接", "count": 0}
        result["status"][channel] = {**result["status"].get(channel, {}), **report}
        return result, report


def main():
    parser = argparse.ArgumentParser(description="源点 DAILY 每日内容更新")
    parser.add_argument("--collect-only", action="store_true", help="仅收集真实原文到 data/，不调用模型或覆盖公开内容")
    parser.add_argument("--draft", action="store_true", help="翻译后写入 data/draft-catalog.json，不更新网站")
    parser.add_argument("--source", choices=("hn", "ph", "ai"), action="append", help="只更新指定来源，可重复传入")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env.local", override=False)
    config = json.loads((ROOT / "config/sources.json").read_text())
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    today = now.astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    ph_day = (now.date() - timedelta(days=1)).isoformat()
    collectors = {
        "hn": lambda: collect_hn(config["hnLimit"]),
        "ph": lambda: collect_ph(ph_day, os.environ.get("PRODUCTHUNT_TOKEN", ""), config["phLimit"]),
        "ai": lambda: collect_ai(config, now),
    }
    catalog = read_catalog(ROOT / "content/catalog.json")
    reports, collected = {}, {}
    selected = list(dict.fromkeys(args.source or ["hn", "ai", "ph"]))
    for channel in selected:
        day = ph_day if channel == "ph" and os.environ.get("PRODUCTHUNT_TOKEN") else today
        def collect_and_save(channel=channel):
            entries = collectors[channel]()
            collected[channel] = {"date": day, "collectedAt": timestamp, "items": entries}
            write_json(ROOT / "data/collected.json", collected)
            return entries
        if args.collect_only:
            try:
                entries = collect_and_save()
                reports[channel] = {"state": "collected", "count": len(entries), "checkedAt": timestamp, "message": "仅收集原文，尚未翻译或发布"}
            except (RuntimeError, ValueError, OSError, KeyError, TypeError):
                reports[channel] = {"state": "error", "count": 0, "checkedAt": timestamp, "message": "原文采集失败"}
        else:
            catalog, reports[channel] = update_source(catalog, channel, day, collect_and_save, lambda entries, cache: translate_items(entries, cache, os.environ), timestamp)
        print(f"{channel}: {reports[channel]['state']} / {reports[channel]['count']} 条")
    report = {"startedAt": timestamp, "mode": "collect-only" if args.collect_only else "draft" if args.draft else "publish", "sources": reports}
    write_json(ROOT / "data/last-run.json", report)
    if not args.collect_only:
        write_json(ROOT / ("data/draft-catalog.json" if args.draft else "content/catalog.json"), catalog)
    states = [entry["state"] for entry in reports.values()]
    if "error" in states:
        print("存在失败来源：原文与去密钥报告保存在 data/，已发布内容未被失败来源覆盖。")
        return 1
    if not any(state in ("ok", "collected", "unchanged") for state in states):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
