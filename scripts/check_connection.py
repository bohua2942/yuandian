#!/usr/bin/env python3
"""Run after adding keys: use one real model call, bypassing translation cache."""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from sources import collect_hn, collect_ph
from translate import translate_items
from store import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT / ".env.local", override=False)
    now = datetime.now(timezone.utc)
    report = {"checkedAt": now.isoformat(), "llm": "not_configured", "ph": "not_configured"}
    if not os.environ.get("LLM_API_KEY"):
        print("模型：待填写 LLM_API_KEY（密钥值不会输出）")
    else:
        try:
            original = collect_hn(1)
            result = translate_items(original, [], os.environ)
            if not result:
                raise ValueError("empty result")
            report["llm"] = "ok"
            print("模型：真实请求及中文结果校验通过")
            print("本次结果：" + result[0]["titleZh"])
        except (RuntimeError, ValueError, OSError, KeyError):
            report["llm"] = "error"
            print("模型：接入未通过。检查 base URL、模型名、密钥权限及 JSON 输出支持。")
    if not os.environ.get("PRODUCTHUNT_TOKEN"):
        print("PH：待填写 PRODUCTHUNT_TOKEN（HN 和 RSS 无需此密钥）")
    else:
        try:
            day = (now.date() - timedelta(days=1)).isoformat()
            items = collect_ph(day, os.environ["PRODUCTHUNT_TOKEN"], 1)
            if not items:
                raise ValueError("empty PH response")
            report["ph"] = "ok"
            print(f"PH：真实 {day} API 请求通过")
            print("本次产品：" + items[0]["title"])
        except (RuntimeError, ValueError, OSError, KeyError):
            report["ph"] = "error"
            print("PH：接入未通过。检查 Developer Token、权限及网络连接。")
    write_json(ROOT / "data/connection-report.json", report)
    print("报告：data/connection-report.json；未更新公开内容。")
    return 0 if report["llm"] == report["ph"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
