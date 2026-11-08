# 07/02　k3d 與 Kubernetes manifest

- Phase：07-self-hosted-platform（自架平台）
- 能力：M2 自架基礎設施
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
把 Compose 改寫成 Deployment、Service、Job。

## 數學／原理（完整推導寫在 math.md）
requests／limits、readiness／liveness 探針、ConfigMap 與 Secret。

## 測試：通過條件
k3d 叢集上跑通，每個 Pod 都有資源限制與探針。

## AI 否證目標
見第 03 課。

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
