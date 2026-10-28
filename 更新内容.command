#!/bin/zsh
set -e
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
if [[ ! -f .env.local ]]; then
  cp .env.example .env.local
  open -t .env.local
  echo "已打开本地配置文件。请填入 API 密钥后，再次双击更新内容。密钥不要发到聊天里。"
  read -k 1
  exit 0
fi
if .venv/bin/python scripts/daily.py; then
  echo "内容已更新。正在运行的本地预览会自动刷新；线上网站需提交更新后部署。"
else
  echo "部分内容没有完成更新，旧内容已保留。请查看 data/last-run.json。"
fi
read -k 1
