# 00/03　第一個 Docker 映像

- Phase：00-setup-and-tooling（環境與工作方法）
- 能力：M2 自架基礎設施
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
把求解器裝進容器，在容器裡跑出與本機逐位元相同的輸出。

## 數學／原理（完整推導寫在 math.md）
映像＝環境的快照；標籤＝版本。

## 測試：通過條件
容器輸出與本機輸出的 sha256 相同。

## AI 否證目標
AI 的 Dockerfile 用 :latest、以 root 執行、把 .git 與資料打進映像。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
