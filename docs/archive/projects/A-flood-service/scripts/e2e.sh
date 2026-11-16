#!/usr/bin/env bash
# 對執行中的 compose 服務做端到端檢查，成功時寫出 e2e.json（metrics.py 會讀）
set -euo pipefail
cd "$(dirname "$0")/.."
BASE=${BASE:-http://localhost:8000}
MODE=${MODE:-compose}; export MODE   # compose 或 local（直接跑 uvicorn＋worker）
id=$(curl -sf -X POST "$BASE/v1/runs" -H 'Content-Type: application/json' \
      -d '{"h_left":10,"h_right":1,"cells":400}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
for i in $(seq 1 60); do
  out=$(curl -sf "$BASE/v1/runs/$id")
  st=$(echo "$out" | python3 -c 'import sys,json;print(json.load(sys.stdin)["status"])')
  [ "$st" = done ] && break
  [ "$st" = failed ] && { echo "$out"; exit 1; }
  sleep 1
done
echo "$out" | python3 -c '
import sys, json, datetime
r = json.load(sys.stdin)["result"]
print("done: steps=%d mass_rel_error=%.1e L1=%.2f m2" % (r["steps"], r["mass_rel_error"], r["l1_error_vs_analytic_m2"]))
json.dump({"ok": True, "mode": __import__("os").environ.get("MODE", "compose"), "at": datetime.datetime.now().astimezone().isoformat(), "l1": r["l1_error_vs_analytic_m2"]}, open("e2e.json", "w"))
'
