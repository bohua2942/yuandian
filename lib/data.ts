import raw from "@/content/catalog.json";
import type { Catalog } from "./content";

export const catalog = raw as Catalog;
export const site = { name: "源点", english: "SOURCE DAILY", description: "独立开发者的每日信息源。发现新产品，读懂 AI 动态，找到下一步的灵感。", url: (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "") };
