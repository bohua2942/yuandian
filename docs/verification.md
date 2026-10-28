# 本次验收记录

日期：2026-10-28（北京时间）。

## 已验证

- 真实公开采集：HN 30 条；OpenAI / Google AI / Hugging Face RSS 合并后 12 条。原始采集时间保存在本地 data/collected.json；首期公开条目保留来源 URL 和发布时间。
- 首批中文：本次协作整理，translationStatus 为 editorial。它不代表真实模型 API 翻译验收完成。
- Python 自动测试：20 项通过，包括真实本地 HTTP 协议、分批翻译校验、截断响应重试、去重、跨日保留、来源失败恢复。
- TypeScript 内容选择测试：6 项通过。
- npm run typecheck 通过；npm run build 通过，导出 57 个静态路由/文件。
- 浏览器：390px 手机视口无横向溢出；搜索中英文命中、结果跳转、ESC 关闭、深浅色切换与刷新后记忆通过。
- RSS 返回 200，XML 可解析，含 42 条；栏目、归档、站点地图和 robots 均返回 200。
- 对 out/ 独立启动静态 HTTP 服务验收：按需搜索 Ghostty、点击搜索结果进入正确详情及原文链接通过；静态 RSS 与搜索索引返回 200。
- 独立代码审查发现的两项问题已修复并复核：HTTP 截断影响来源隔离；全部来源失败时也应发布失败状态。
- .env.local、data/、node_modules/、.venv/ 已通过 Git ignore 检查；双击入口均通过 zsh 语法检查。

## 尚未验证 / 尚未激活

- 用户真实模型 API：未配置 LLM_API_KEY。
- 用户 PH API：未配置 PRODUCTHUNT_TOKEN。
- GitHub 远程仓库、Actions 实际定时执行与 Vercel 部署：未创建或激活。
- 正式域名、线上 RSS 地址与公网访问：等待部署后验证。

填写本地配置后，运行 scripts/check_connection.py，才能确认真实模型与 PH 接入；随后按 README 部署并手动触发一次 Actions，确认内容提交及线上更新。
