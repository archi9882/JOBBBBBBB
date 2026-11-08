# 01/04　靜水測試

- Phase：01-conservation-and-verification（守恆與驗證）
- 能力：M1 數值模擬與物理判斷
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
水面水平、流速為 0、底床有坡度：正確的格式應永遠靜止。

## 數學／原理（完整推導寫在 math.md）
壓力梯度項與底床坡度源項需在離散層級抵銷（well-balanced）。

## 測試：通過條件
1000 步後最大流速 < 1e-12 m/s。

## AI 否證目標
AI 說假流速是「數值雜訊可忽略」。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
