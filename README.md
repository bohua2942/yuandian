# 源点 DAILY

一个参考 DecoHack 阅读布局的独立开发者信息站。包含首页、AI 早报、Hacker News 热榜、Product Hunt 新品、日期归档、详情、搜索、RSS、深浅色与移动端布局。临时品牌为「源点」，可以再改成你的名称。

**目前是可运行的本地项目，尚未部署到线上，也没有激活云端定时任务。** HN 和三个公开 RSS 已实际抓取；首批中文由本次协作整理，详情页标注为初始整理。2026-10-28 已使用用户本地配置完成 DeepSeek 真实调用及采集、翻译、页面更新；PH 已通过免密钥官方 RSS 接入并翻译 30 款产品，无需申请 token。

## 先看网站

双击目录里的 **启动网站.command**，打开终端显示的本地地址，默认是 http://127.0.0.1:3000 。关闭服务按 Control+C。若 3000 端口被占用，以终端显示的新端口为准。

需要 Node.js 22+。命令行方式：

```bash
cd '/Users/wangbohua/code/内容源网站'
npm ci
npm run dev
```

界面使用自己的名称、图标与真实来源内容，没有复制 DecoHack 的品牌和历史文章。

## 本地填 API 并真实验收

**有 DeepSeek API 就可以做中文翻译和摘要，不需要另买 OpenAI API。** 本地示例已使用 DeepSeek：地址 `https://api.deepseek.com`，模型 `deepseek-flash`。在 `.env.local` 的 `LLM_API_KEY=` 后填入你的 DeepSeek 密钥即可；不要把密钥发到聊天。接口名称 `LLM` 表示大语言模型，不限定服务商。配置依据：[DeepSeek 官方文档](https://api-docs.deepseek.com/)。

PH 已支持免密钥方案：`PRODUCTHUNT_TOKEN` 留空时自动读取 Product Hunt [官方 RSS](https://help.producthunt.com/en/articles/484970-does-product-hunt-have-an-rss-feed)，获取名称、简介、原始发布时间和 PH 链接。它是订阅快照，不含票数，也不是完整日榜；页面按原始发布时间排序。以后填入 PH token 才切换为含票数的 API 榜单。

PH 详情还会补采公开产品页的产品结构化介绍与官网入口，再由 DeepSeek 完整翻译；列表用一句话简介，详情另显示产品介绍。只接受产品 JSON-LD，不把登录页或通用站点元描述当作产品内容。某次补采失败时保留已有已验证介绍，并标记原资料保存时间；从未取得详细资料的产品明确显示缺口，不让模型凭空扩写。官网与 PH 原文入口放在详情标题下。

1. 双击 **配置API.command**。它会创建并打开本地 `.env.local`，不会覆盖你已经填写的文件。
2. 填写下表中的配置并保存。密钥只在本机填写，不发到聊天、截图、Git 或笔记网站。
3. 双击 **验证接入.command**：实际抓取一条 HN 原文、绕过缓存调用一次模型，并测试 PH 官方 RSS（填写 token 时测试 API）。一切就绪时才显示接入通过；该操作不发布内容。
4. 双击 **更新内容.command**：真实采集、翻译、校验并更新内容库。本地开发预览会刷新。

| 变量 | 如何填写 | 是否必须 |
| --- | --- | --- |
| `LLM_API_KEY` | 模型服务商的 API 密钥 | 自动翻译必需 |
| `LLM_BASE_URL` | OpenAI 兼容接口根地址，不包含 `/chat/completions`；DeepSeek 为 `https://api.deepseek.com` | 本地示例已填 DeepSeek；其他服务商按文档填写 |
| `LLM_MODEL` | 账户能调用的模型名称，需支持 Chat Completions 和 JSON 输出 | 本地示例已填 `deepseek-flash` |
| `PRODUCTHUNT_TOKEN` | 可选的 Product Hunt Developer Token | 留空即可使用官方 RSS；需要含票数的 API 榜单时再填 |
| `NEXT_PUBLIC_SITE_URL` | 正式网站的完整 HTTPS 地址 | 正式部署必填，用于 RSS 和站点地图 |

获取 PH token：[官方 API 文档](https://api.producthunt.com/v2/docs)。官方文档目前限制商业用途，经营网站前需确认相应授权。

`data/connection-report.json` 记录最近一次真实接入检查，不含密钥。**本地协议测试通过不等于你的真实账号接入通过，以此检查结果为准。**

## 每日自动更新怎样工作

```text
每天北京时间 09:17（GitHub Actions，触发可能延迟）
    → HN 官方 API / PH 官方 RSS（可选 API）/ 配置的 AI RSS
    → 清洗、去重、保留来源与时间
    → 相同原文复用翻译，新内容调用模型
    → 校验中文、条数与来源 ID
    → 更新内容库，失败栏目保留上次成功内容
    → 测试与生产构建通过
    → Git 提交 content/catalog.json
    → Vercel 部署，新内容上线
```

- PH：无 token 时读取官方 RSS 的当前快照，取订阅源中原始发布时间最新的 30 款，不生成票数；页面日期为采集日，详情保留原始发布时间。配置 token 后采集前一个完整 UTC 日的 API 榜单，页面标注该数据日期。不会把 RSS 当作前一日完整票数榜单。
- HN：采集运行时的热榜快照，按官方排名保留顺序，不冒充全天最终榜单。
- AI 早报：读取近 72 小时的条目，合并去重、按发布时间倒序，最多 12 条；没有内容时保留上期。
- AI 来源是 OpenAI 新闻、Google AI 博客、Hugging Face 博客。HF 包含社区作者，不能把每篇都称为平台官方发布。
- 每个栏目显示自己的最后成功内容日期。不会因为今天跑了任务，就把旧内容标成今天的新内容。
- 某栏目失败时不写入假产品或虚构摘要，其他成功栏目可以继续更新；工作流最后会标记失败以便发现问题。
- 即使全部来源失败，也会在构建通过后发布失败状态提示，文章仍保留上版，不把旧文章替换成失败批次。
- 模型密钥缺失时不会把英文原文当作完成翻译。PH 不依赖密钥即可采集官方 RSS；显式配置的 API token 失效时报告失败，保留旧内容。
- 这里实现的是**自动更新模式**，不需要每天人工点发布。周刊为人工编辑栏目，不自动生成整篇周刊。

## 部署到 GitHub 与 Vercel

本地文件已经具备部署配置，但本次没有替你创建远程仓库或绑定 Vercel 账户。

1. 在自己的 GitHub 账户创建仓库，将本目录源码推送到默认分支 `main`。建议先使用私有仓库。不要上传 `.env.local`、`.venv`、`data` 或 `node_modules`。
2. 在 Vercel 导入这个仓库。项目使用 `vercel.json` 的构建命令 `npm run build` 与输出目录 `out`；选择 Node.js 22 或更新版本。
3. 先获得 Vercel 分配的域名，设置 Vercel 环境变量 `NEXT_PUBLIC_SITE_URL=https://你的域名`，重新部署。正式域名确定后再替换并重新部署，否则 RSS 和站点地图仍指向本机。
4. 在 GitHub 仓库 Settings → Secrets and variables → Actions 添加以下配置：

| 位置 | 名称 | 内容 |
| --- | --- | --- |
| Repository secret | `LLM_API_KEY` | 你的模型密钥 |
| Repository secret | `PRODUCTHUNT_TOKEN` | 可选；留空使用官方 RSS，需要 API 榜单时再配 |
| Repository variable | `LLM_BASE_URL` | DeepSeek 填 `https://api.deepseek.com`；留空时程序回退到 OpenAI，因此使用 DeepSeek 时不要留空 |
| Repository variable | `LLM_MODEL` | DeepSeek 填 `deepseek-flash`；留空时程序回退到 `gpt-4.1-mini`，因此使用 DeepSeek 时不要留空 |
| Repository variable | `SITE_URL` | 正式 HTTPS 网址，与 Vercel 的 `NEXT_PUBLIC_SITE_URL` 一致 |
| Repository secret | `VERCEL_DEPLOY_HOOK` | 建议配置 Vercel Deploy Hook 地址，确保内容更新可明确触发部署 |

5. 在 Vercel 项目 Settings → Git → Deploy Hooks 为 `main` 创建 Hook，填入上述 GitHub Secret。这个 Hook 本身有部署权限，不要公开。模型和 PH 密钥无需放进 Vercel，因为访问网站时不会调用它们。
6. 在 GitHub Actions 手动运行「每日采集、翻译与更新」，检查 `daily-run-report`、生成的内容提交和 Vercel 实际部署结果。三者都验证后，才算自动更新接通。

默认工作流每个 UTC 日 `01:17` 运行（北京时间 `09:17`），并使用 concurrency 避免同分支重叠写入。GitHub 只对默认分支执行 schedule，可能延迟；公开仓库长期无活动时可能停用 schedule。

工作流用内置 `GITHUB_TOKEN`，不需要额外 PAT；仅授予内容写权限。`GITHUB_TOKEN` 推送不会递归触发另一套 push Actions，因此采集后的测试和构建直接放在同一更新工作流里。

Vercel Git 集成可能已自动部署内容提交；显式 Deploy Hook 能保证触发路径明确，但也可能产生重复部署。稳定后可根据实际账户配置选择保留其中一种。

## 常用命令

先安装 Python 依赖（Python 3.12+）：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

```bash
# 仅采集公开原文到本地 data/，不消耗模型额度、不覆盖网站
.venv/bin/python scripts/daily.py --collect-only

# 只更新 HN 或 AI（需要翻译密钥；已有相同原文可以复用缓存）
.venv/bin/python scripts/daily.py --source hn
.venv/bin/python scripts/daily.py --source ai

# 翻译成草稿，保存到 data/draft-catalog.json，不改变网站
.venv/bin/python scripts/daily.py --draft

# 实际模型及 PH 接入检查，绕过翻译缓存
.venv/bin/python scripts/check_connection.py

# 全部更新与检查
.venv/bin/python scripts/daily.py
.venv/bin/python -m unittest discover -s tests -v
npm test
npm run typecheck
npm run build
```

`npm run build` 生成 `out/`，不能直接双击 HTML 验收路由。可以运行 `python3 -m http.server 3001 --directory out` 预览静态产物。

## 修改来源、名称和周刊

- 信息源与数量：编辑 `config/sources.json`。RSS 需有标题、HTTP(S) 原文链接和可解析的发布时间；当前三个源任何一个失败都会使本期 AI 栏目保留旧版，避免静默漏采。
- 网站名称和描述：`lib/data.ts`；顶部品牌：`components/shell.tsx`；图标：`public/icon.svg`。
- 样式：`app/globals.css`。保留原站的底色、日期、双栏和卡片语言，品牌为独立的临时名称。
- 周刊目前为空，不展示模拟文章。人工条目放进 `content/catalog.json` 的 `items`，使用 `channel: "weekly"`、独立 `sourceId`、`id`、`date`、中文标题/摘要和原文链接，并在 `batches` 添加对应周刊日期及数量。日更任务会保留它。需要更方便的周刊编辑界面时再单独添加。

## 数据、权限与故障恢复

| 路径 | 用途 | 是否进入 Git |
| --- | --- | --- |
| `content/catalog.json` | 公开内容、历史快照、来源与状态 | 是，内容会公开给访客 |
| `config/sources.json` | 公开 RSS 与数量配置 | 是 |
| `.env.local` | 本机 API 凭据 | 否 |
| `data/collected.json` | 最近一次采集的原文 | 否 |
| `data/last-run.json` | 去密钥的运行报告 | 否；CI 仅上传这份报告为 artifact |
| `data/connection-report.json` | 真实 API 接入检查结果 | 否 |

公开 JSON 使用字段白名单，模型只能补中文标题、摘要和标签，不能改来源链接或热度。写文件使用同目录临时文件原子替换；不覆盖其他日期和栏目。历史翻译按原文指纹缓存，原文改变则重新翻译。

模型 API 使用 HTTPS（仅本机测试允许 HTTP）。抓取和翻译的上游响应正文不进入错误日志，避免回显凭据；也不会把新闻 HTML 当作页面 HTML 渲染。

失败排查：先看 `data/last-run.json` 或 Actions 的 `daily-run-report`，再运行「验证接入」。连接报告中的 PH `rss_ok` 表示免密钥官方 RSS 接入通过；`error` 表示抓取或翻译未通过；`unchanged` 表示没有新内容并保留旧期。失败来源不会删除已发布内容。

回退线上内容：在 GitHub 对最近的 `content: update daily sources` 提交执行 Revert，并重新部署。暂停定时：在 Actions 中禁用「每日采集、翻译与更新」，无需删内容或密钥。

## 代码结构

```text
app/                   页面、静态 RSS、搜索索引、站点地图
components/            导航、阅读列表、搜索与主题
lib/                   类型与内容选择函数
content/catalog.json   公开内容文件
config/sources.json    来源配置
scripts/sources.py     官方 API / RSS 采集
scripts/translate.py   分批翻译、中文校验与缓存
scripts/store.py       去重、历史合并和原子存储
scripts/daily.py       更新入口
tests/                 内容选择、采集、恢复与模型协议测试
.github/workflows/     每日更新与构建检查
```

接口参考：[HN 官方 API](https://github.com/HackerNews/API)、[PH 官方 API](https://api.producthunt.com/v2/docs)、[Next.js 静态导出](https://nextjs.org/docs/app/guides/static-exports)、[GitHub 定时触发](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。实现没有复制开源采集脚本的实质代码；只参考官方 API 及公开数据结构。
