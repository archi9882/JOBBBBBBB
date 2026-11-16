# 02/01　Saint-Venant 方程與 CFL

- Phase：02-shallow-water-fv（淺水方程有限體積法）
- 能力：M1 數值模擬與物理判斷
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
寫出守恆形式 U、F(U)、S(U)，並由特徵速度推出時間步限制。

## 數學／原理（完整推導寫在 math.md）
特徵值 u ± √(gh)；Δt ≤ Cr·Δx / max(|u| + √(gh))。

## 測試：通過條件
Δt 每步依 CFL 重算；Cr=1.2 時程式主動報錯。

## AI 否證目標
固定 Δt：水深變大後 CFL 超過 1，解發散。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
