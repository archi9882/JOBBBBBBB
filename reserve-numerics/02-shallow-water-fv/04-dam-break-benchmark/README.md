# 02/04　潰壩解析解基準

- Phase：02-shallow-water-fv（淺水方程有限體積法）
- 能力：M1 數值模擬與物理判斷
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
Ritter（乾床）與 Stoker（濕床）解寫成可重複使用的基準模組。

## 數學／原理（完整推導寫在 math.md）
稀疏波 h = (2√(gh_0) − x/t)² / (9g)（Ritter）。

## 測試：通過條件
基準函式通過守恆與邊界值檢查。

## AI 否證目標
AI 背出的 Ritter 公式係數錯誤（4/9、1/9g 對調）。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
