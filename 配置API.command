#!/bin/zsh
set -e
cd "$(dirname "$0")"
if [[ ! -f .env.local ]]; then cp .env.example .env.local; fi
open -t .env.local
echo "请在打开的 .env.local 中填写密钥并保存。不要把密钥发到聊天、截图或 Git。"
echo "填写后双击「验证接入.command」，确认真实模型和 PH API 能用。"
read -k 1
