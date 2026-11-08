# 00/02　repo 結構與第一個測試

- Phase：00-setup-and-tooling（環境與工作方法）
- 能力：M3 GAI 協作與否證
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
測試是否證的最小單位：沒有測試，就沒有「驗證過」。

## 數學／原理（完整推導寫在 math.md）
斷言（assert）＝可被推翻的預測。

## 測試：通過條件
`python tools/ship_check.py` 能列出每堂課的狀態。

## AI 否證目標
AI 寫的測試只檢查「有回傳值」，沒檢查數值是否正確。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
