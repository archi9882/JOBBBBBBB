# 07/01　Docker Compose：API＋worker

- Phase：07-self-hosted-platform（自架平台）
- 能力：M2 自架基礎設施
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
兩個容器、一個共用資料卷，一行指令啟動。

## 數學／原理（完整推導寫在 math.md）
服務、網路、資料卷、健康檢查。

## 測試：通過條件
`docker compose up` 後送出一個模擬並取得結果。

## AI 否證目標
worker 與 API 共用同一個容器；沒有健康檢查。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
