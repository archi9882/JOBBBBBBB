# 專案 A：AI 否證紀錄

Claude 撰寫本專案時，被測試或實跑推翻的說法。全部真實發生、可重現。

| 日期 | AI 說了什麼 | 可檢驗的預測 | 驗證方法 | 結論 |
|---|---|---|---|---|
| 2026-11-08 | 乾床測試的註解寫「數值擴散會讓極薄水層略微超前 Ritter 前緣」，容差 40 m | 數值前緣 ≥ 解析前緣，差 < 40 m | 實跑 N=800：數值前緣 844 m、解析 889 m（同以 h > 1 mm 定義），**落後** 45 m；N=400→3200 落後 57.5→25.6 m | 方向說反了，容差也太小。改成測「落後且隨網格加密縮小」 |
| 2026-11-08 | API 用一條全域 sqlite3 連線，端到端測試會通過 | worker 與 API 可共用同一連線物件 | 測試失敗：`ProgrammingError: SQLite objects created in a thread can only be used in that same thread`。FastAPI 的同步端點在執行緒池中執行 | 單元測試若都在同一執行緒就抓不到。改成每個請求開新連線；正式環境 uvicorn 也會遇到同樣問題 |
| 2026-11-08 | `scripts/e2e.sh` 內嵌 Python 的 f-string 用 `\"` 跳脫 | 腳本可執行 | 實跑：SyntaxError（f-string 內的反斜線跳脫） | 改用 % 格式化。shell 內嵌 Python 的引號要實跑才知道 |
| 2026-11-08 | metrics.py 以 `pytest -q` 解析「N passed」 | 能解析到通過數 | 實跑得到 0：專案 pytest.ini 已有 `-q`，兩個 `-q` 讓摘要行消失 | 呼叫時以 `-o addopts=...` 覆寫設定 |
| 2026-11-08 | Dockerfile 可在工作區建置 | `docker compose build` 成功 | 失敗：Docker Hub 回 Forbidden（工作區網路限制） | 未實測，已在 README 標明。改以兩個行程模擬 compose 完成端到端 |
