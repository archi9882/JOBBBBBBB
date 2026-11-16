# 00/04　AI 否證紀錄的方法

- Phase：00-setup-and-tooling（環境與工作方法）
- 能力：M3 GAI 協作與否證
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
建立固定流程：先要 AI 寫出可檢驗的預測，再用獨立方法檢查。

## 數學／原理（完整推導寫在 math.md）
驗證工具箱：量綱、極限情形、守恆、解析解、製造解、收斂階、第二實作。

## 測試：通過條件
docs/ai-falsification-log.md 有第一筆完整紀錄。

## AI 否證目標
叫 AI 檢查自己的輸出，當成獨立驗證。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
