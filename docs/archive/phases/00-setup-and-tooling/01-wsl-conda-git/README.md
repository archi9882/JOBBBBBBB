# 00/01　WSL2、conda 與 git

- Phase：00-setup-and-tooling（環境與工作方法）
- 能力：M2 自架基礎設施
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
建立可重現的開發環境，換一台機器也能得到相同結果。

## 數學／原理（完整推導寫在 math.md）
environment.yml 釘住版本；git 記錄每一次變更。

## 測試：通過條件
新 clone 後 `conda env create` ＋ `pytest` 全部通過。

## AI 否證目標
AI 給的安裝指令混用 pip 與 conda、或不釘版本。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
