#!/bin/zsh
set -e
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
if .venv/bin/python scripts/check_connection.py; then
  echo "接入已通过。现在可以双击「更新内容.command」。"
else
  echo "仍有未接通的项目，请根据上方提示检查配置。"
fi
read -k 1
