# Daily Content Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. The user authorized the proposed end-to-end implementation; continue within that scope.

**Goal:** 在当前空目录交付可运行的 DecoHack 风格中文信息站及每日采集翻译流水线。

**Architecture:** 静态 Next.js 页面读取 JSON 内容库，Python 负责官方来源采集和模型翻译。GitHub Actions 在完成验证后生成内容提交，Vercel 部署该提交；来源失败不会抹掉已发布的内容。

**Tech Stack:** Next.js 16, React 19, TypeScript, Python 3.12, unittest, GitHub Actions.

**Spec:** docs/superpowers/specs/2026-10-28-content-site-design.md

## Global Constraints

- 密钥仅 .env.local 或 GitHub Secrets，不进入公开 JSON、浏览器、日志、Git。
- 模拟数据不可替代真实采集，未验证模型/PH 接入必须明确报告。
- 原文链接、来源时间、翻译状态必须可追溯；失败保留上版；历史不能被当天刷新删除。
- 使用原站布局语言，站名与文案使用自己的内容。

### Task 1: 可恢复的数据流水线

**Files:** scripts/sources.py, scripts/translate.py, scripts/store.py, scripts/daily.py, tests/test_pipeline.py, config/sources.json

**Interfaces:** sources.collect(channel,date,limit) 返回条目列表；translate.translate_items(items, env) 返回经校验的中文；store.merge_catalog(catalog,channel,date,items,status) 保留历史及其他来源；daily CLI 写入内容及本地报告。

- [x] 编写测试：重复运行不重复、次日保留旧日、翻译错误不能覆盖原文与旧条目、RSS 跨源去重和危险链接过滤。
- [x] 运行 `.venv/bin/python -m unittest discover -s tests -v`，确认实现缺失导致失败。
- [x] 按固定接口实现采集、翻译、合并；外部 HTTP 只在边界替换以测试，不模拟内部存储。
- [x] 测试变绿，执行 `python scripts/daily.py --collect-only` 检查真实原文。

### Task 2: 真实内容驱动的阅读界面

**Files:** app/, components/, lib/content.ts, content/catalog.json

**Interfaces:** 页面只读取公开 Catalog；ID 路由经过静态参数生成；RSS/站点地图从同一内容库生成。

- [x] 写内容选择测试：各来源使用自己的最新有效批次；搜索可命中中英文；不显示虚构的当日更新。
- [x] 实现首页、栏目、日期归档、详情、搜索、RSS、主题与移动布局；空周刊提供编辑入口说明。
- [x] 执行 `npm run typecheck` 与 `npm run build`。
- [x] 启动本地预览，验证搜索、键盘关闭、主题切换、详情、归档与窄屏无溢出。

### Task 3: 每日任务与可用交付

**Files:** .github/workflows/daily.yml, .github/workflows/check.yml, .env.example, README.md, 启动网站.command, 更新内容.command

- [x] 配置 UTC 01:17 定时与手动运行；concurrency 防并发写；权限最小化；失败上传去密钥报告。
- [x] 自动更新仅提交内容文件；失败状态变化也须构建后提交，文章保留上版。用户已确认自动发布，本地草稿仅由 --draft 输出。
- [x] 写中文接入与部署步骤、失败排查及真实验证清单，双击入口在本目录启动。
- [x] 运行全部测试和生产构建，检查待提交文件无密钥；报告已完成和待凭据验证的部分。
