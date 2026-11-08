# 02/03　HLL 近似 Riemann 解

- Phase：02-shallow-water-fv（淺水方程有限體積法）
- 能力：M1 數值模擬與物理判斷
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
提高激波解析度，比較 LF 與 HLL。

## 數學／原理（完整推導寫在 math.md）
以左右波速 S_L、S_R 組合通量。

## 測試：通過條件
相同 N 下 HLL 的激波寬度（格數）小於 LF。

## AI 否證目標
S_L、S_R 估計式寫錯符號，乾床時出現負水深。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
