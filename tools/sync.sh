#!/usr/bin/env bash
# 三處同步：GitHub(origin) <-> ~/JOB（唯一可編輯）-> /mnt/c/JOB/JOB（唯讀鏡像）
# 用法：
#   bash tools/sync.sh              只檢查三處是否一致，不改任何東西
#   bash tools/sync.sh "commit 說明"  拉取、提交、推送，再更新鏡像
set -euo pipefail

MAIN="$HOME/JOB"            # 主工作區：所有編輯只在這裡做
MIRROR="/mnt/c/JOB/JOB"     # Windows 端鏡像：只接收 fast-forward，不要在這裡編輯
MSG="${1:-}"                # 有給說明才會真的同步

# 顯示三處目前的 commit，方便比對
report() {
  echo "main   (~/JOB)     : $(git -C "$MAIN" rev-parse --short HEAD)"
  if [ -d "$MIRROR/.git" ]; then
    echo "mirror (/mnt/c)    : $(git -C "$MIRROR" rev-parse --short HEAD)"
  fi
  echo "origin (GitHub)    : $(git -C "$MAIN" rev-parse --short origin/main)"
}

git -C "$MAIN" fetch origin --quiet
[ -d "$MIRROR/.git" ] && git -C "$MIRROR" fetch origin --quiet || true

# 檢查模式：只報告，不動檔案
if [ -z "$MSG" ]; then
  report
  [ -n "$(git -C "$MAIN" status --porcelain)" ] && echo "注意：~/JOB 有未提交的改動"
  if [ -d "$MIRROR/.git" ] && [ -n "$(git -C "$MIRROR" status --porcelain)" ]; then
    echo "注意：鏡像有未提交的改動，請先搬回 ~/JOB 再處理"
  fi
  exit 0
fi

# 1. 主工作區：先拉再提交，避免推送被拒
git -C "$MAIN" pull --rebase --autostash
if [ -n "$(git -C "$MAIN" status --porcelain)" ]; then
  git -C "$MAIN" add -A
  git -C "$MAIN" commit -m "$MSG"
fi
git -C "$MAIN" push

# 2. 鏡像：有本地改動就拒絕覆蓋，只做 fast-forward
if [ -d "$MIRROR/.git" ]; then
  if [ -n "$(git -C "$MIRROR" status --porcelain)" ]; then
    echo "略過鏡像：有未提交的改動，不會覆蓋。請先把改動搬到 ~/JOB。"
  else
    git -C "$MIRROR" pull --ff-only
  fi
fi

report
