# 07/03　AI manifest 審查演練

- Phase：07-self-hosted-platform（自架平台）
- 能力：M2 自架基礎設施
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
讓 AI 產生 manifest，10 分鐘內找出地雷並說明後果。

## 數學／原理（完整推導寫在 math.md）
檢查清單：映像標籤、資源、探針、Secret、權限、儲存存取模式。

## 測試：通過條件
至少找出 4 個地雷並各寫一句後果。

## AI 否證目標
:latest、無資源限制、root、hostPath、多副本共用 RWO PVC、Secret 進 git。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
