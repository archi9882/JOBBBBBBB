# 06/04　錯誤格式與版本

- Phase：06-service（模擬服務 API）
- 能力：E2 REST API
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
下游系統依賴你的錯誤格式；改介面不能破壞舊用戶。

## 數學／原理（完整推導寫在 math.md）
RFC 9457 Problem Details；路徑版本 /v1。

## 測試：通過條件
所有錯誤回應通過同一個 schema 測試。

## AI 否證目標
例外的堆疊追蹤直接回傳給使用者。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
