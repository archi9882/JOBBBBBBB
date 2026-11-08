# 02/05　乾濕邊界與底床源項

- Phase：02-shallow-water-fv（淺水方程有限體積法）
- 能力：M1 數值模擬與物理判斷
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
處理乾床與地形，同時保持靜水平衡。

## 數學／原理（完整推導寫在 math.md）
水深重構（hydrostatic reconstruction）。

## 測試：通過條件
第 01-04 課的靜水測試在新求解器上仍通過；水深永不為負。

## AI 否證目標
用 h < ε 直接設 0，質量不守恆。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
