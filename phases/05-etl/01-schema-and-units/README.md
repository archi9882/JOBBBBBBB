# 05/01　Schema 與單位

- Phase：05-etl（ETL 與資料品質）
- 能力：E1 ETL
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
多來源雨量資料統一欄位、型別、單位。

## 數學／原理（完整推導寫在 math.md）
明確的 schema；單位換算寫成純函式。

## 測試：通過條件
違反 schema 的列被拒收並記錄原因。

## AI 否證目標
0.1 mm 與 mm 混用；字串數字未轉型。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
