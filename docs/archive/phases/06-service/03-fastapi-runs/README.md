# 06/03　FastAPI 非同步工作 API

- Phase：06-service（模擬服務 API）
- 能力：E2 REST API
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
POST /v1/runs 回 202 與 id；GET /v1/runs/{id} 查狀態。

## 數學／原理（完整推導寫在 math.md）
與第 02 課的佇列相同語意，改用框架。

## 測試：通過條件
合約測試：5 個邊界情境（負 n、超大網格、重複送出等）。

## AI 否證目標
長時間模擬寫成同步端點；沒有輸入上限。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
