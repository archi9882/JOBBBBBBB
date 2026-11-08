# 02/02　Lax–Friedrichs 通量

- Phase：02-shallow-water-fv（淺水方程有限體積法）
- 能力：M1 數值模擬與物理判斷
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
第一個完整的 1D SWE 求解器。

## 數學／原理（完整推導寫在 math.md）
F_{i+½} = ½(F_L + F_R) − ½ α (U_R − U_L)。

## 測試：通過條件
濕床潰壩與 Stoker 解 L1 誤差隨 N 加倍而下降。

## AI 否證目標
α 用全域常數而非局部最大波速，過度擴散卻沒發現。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
