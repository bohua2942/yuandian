#!/bin/zsh
set -e
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "需要先安装 Node.js 22 或更新版本。"
  read -k 1
  exit 1
fi
if [[ ! -d node_modules ]]; then npm ci; fi
echo "网站即将启动，请打开终端显示的 Local 地址。按 Control+C 停止。"
open "http://localhost:3000"
npm run dev
