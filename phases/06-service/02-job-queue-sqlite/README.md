# 06/02　用 SQLite 手寫工作佇列

- Phase：06-service（模擬服務 API）
- 能力：E2 REST API
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
長時間模擬不能同步執行；先手寫最小佇列。

## 數學／原理（完整推導寫在 math.md）
狀態機：queued → running → done／failed。

## 測試：通過條件
worker 中途被殺掉後，工作會回到 queued 或標記 failed，不會卡在 running。

## AI 否證目標
沒有處理 worker 崩潰，工作永遠 running。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
