# 在 WSL2 用 k3d 部署（未實測）

> 建置環境沒有 k3d，Docker Hub 也被擋，以下指令**沒有實際跑過**。指令格式請以 k3d、kubectl 官方文件確認。

```bash
# 1. 建映像（在 projects/B-rain-etl-spatial/）
docker build -t rain-etl-spatial:0.1.0 .
docker run --rm rain-etl-spatial:0.1.0 python -m pytest -q -p no:cacheprovider tests   # 容器內跑測試

# 2. 建叢集並匯入映像（本機映像不用推 registry）
k3d cluster create rainb
k3d image import rain-etl-spatial:0.1.0 -c rainb

# 3. 部署
kubectl apply -f k8s/
kubectl rollout status deploy/rainb
kubectl port-forward svc/rainb 8080:80
curl "http://localhost:8080/v1/areal-rainfall?start=2026-06-01T09:00:00%2B08:00&end=2026-06-01T12:00:00%2B08:00"
curl http://localhost:8080/metrics
```

注意：URL 裡的 `+08:00` 要寫成 `%2B08:00`，否則 `+` 會被解成空白，字串無法解析成時間，API 回 422（實測）。這種 422 由 FastAPI 在進入處理函式前回傳，**不會計入 `rainb_requests_total`**（實測），監控會漏掉這類錯誤。

## 審查清單（07/03 的演練素材）
| 項目 | 這份 manifest 的做法 | 拿掉會怎樣 |
|---|---|---|
| 映像標籤 | `0.1.0` | `:latest` 出事無法回溯 |
| 資源 | requests 256Mi／limits 512Mi | 一個 Pod 吃光節點記憶體 |
| 探針 | readiness 5 s、liveness 30 s | ETL 還沒跑完就收流量；或啟動中被 liveness 殺掉 |
| 權限 | runAsNonRoot、drop ALL、唯讀根目錄 | 容器被入侵時權限過大 |
| 儲存 | emptyDir（每個 Pod 自己的） | 多副本共用 RWO PVC 會掛載失敗 |
