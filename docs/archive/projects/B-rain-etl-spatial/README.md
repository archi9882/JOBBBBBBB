# 專案 B：雨量 ETL＋空間（速成版）

**目標**：把兩個格式、時區、單位、品質都不同的雨量來源，清理成可信的時雨量，再用徐昇式多邊形（Thiessen polygon）算出流域面積雨量，包成 API，附監控指標與 Kubernetes manifest。

**速成版的意思**：這份程式由 Claude 寫出、可直接跑。你的工作是用 grill-me 逐段拆解，直到每一段都能自己重寫並回答追問。履歷敘述要等拆解通過才會解鎖。

## 如何執行（WSL2 Ubuntu）

```bash
# 在 repo 根目錄
conda activate floodsim
pip install -r projects/B-rain-etl-spatial/requirements.txt
python -m pytest -o addopts= -q --import-mode=importlib projects/B-rain-etl-spatial/tests   # 26 個測試
python projects/B-rain-etl-spatial/metrics.py        # 產出 metrics.json，履歷生產表會讀它

# 啟動 API
cd projects/B-rain-etl-spatial
PYTHONPATH=src RAINB_WORK_DIR=/tmp/rainb uvicorn rainb.api:default_app --factory --port 8000
curl "http://localhost:8000/v1/areal-rainfall?start=2026-06-01T09:00:00%2B08:00&end=2026-06-01T12:00:00%2B08:00"
curl http://localhost:8000/metrics
```

部署到 k3d 見 `k8s/README.md`（未實測）。

## 架構

```
synth.py ── 真值 10 分鐘雨量（整數 0.1 mm）
   ├─► 來源 A：source_a_10min.csv  （UTC、結束標記、0.1 mm、-999、重複、負值、非數字、無時區）
   └─► 來源 B：source_b_hourly.json（台灣時間、結束標記、mm、null）
            │
etl.py ─────┤ load_a / load_b：schema、時區、單位、哨兵、物理範圍、去重 → 拒收清單
            │ hourly_from_a：resample(closed="right", label="right")，並數有效筆數
            │ merge：A 完整 6 筆 > B > 缺值
            └─► hourly.csv（確定性輸出、sha256）、quality.csv、rejected.csv
                         │
spatial.py ── WGS84 → TWD97（EPSG:3826）→ Voronoi＋虛擬遠點 → 裁切到流域 → 權重
                         │
                         └─► areal_rainfall：缺站重新正規化；coverage < 0.5 → 缺值
                                   │
api.py ──── FastAPI：/v1/areal-rainfall、/healthz、/metrics（prometheus_client）
Dockerfile、k8s/ ── 非 root、固定標籤、資源限制、探針
metrics.py ── 跑全流程＋測試 → metrics.json
```

## 合成資料與已知答案

站點座標為虛構（台灣中部附近的合理數值），不是任何真實測站。6 站 × 24 小時 = 144 個站-小時，清理後應得 141 筆，缺的 3 筆是：

| 站-小時 | 原因 | 能否由另一來源補 |
|---|---|---|
| S02 10:00 | A 在 09:30 為 -999 | 否（B 不含 S02） |
| S03 16:00 | A 在 15:10 為 `abc` | 否 |
| S06 07:00 | B 為 null | 否（A 不含 S06） |

S04 13:00（A 有 -999）與 S05 14:00（A 有負值）由 B 補上，數值與真值一致。

## 拆解地圖（grill-me 用）

只列問題，不給答案。回答不出來的題目對應到課程 lesson，先去完成那一課。

| 元件 | 程式位置 | 對應課程 | grill-me 追問 |
|---|---|---|---|
| 時區與時雨量標籤 | `etl.hourly_from_a`、`parse_time` | 05/02 | ① 為什麼拒收沒有時區的時間，而不是假設它是台灣時間？② 把 `closed="right"` 拿掉，哪一個測試會失敗、為什麼？③ 如果來源 B 其實是「開始標記」，你要從資料的哪個特徵發現？ |
| Schema、單位、哨兵 | `etl.load_a`、`load_b` | 05/01、05/03 | ① -999 為什麼要在換算單位之前檢查？② 10 分鐘 50 mm 的上限從哪裡來，換成時雨量資料要改成多少？③ 拒收清單和品質報表，各是給誰看的？ |
| 去重與合併規則 | `load_a`、`etl.merge` | 05/01 | ① 為什麼 A 要 6 筆都有效才採用，5 筆加總不行嗎？② 兩來源同一小時數值不同時，現在的規則會怎樣？應該怎樣？③ 「完全相同才算重複」漏掉了哪種重複？ |
| 可重跑 | `etl.to_csv_bytes`、`etl.run` | 05/04 | ① 哪些東西會讓兩次輸出的 sha256 不同？② 為什麼用覆寫而不是 append？③ 輸入改了一筆，怎麼只重算受影響的部分？ |
| 投影 | `spatial.project`、`roundtrip_error_m` | 04/01 | ① 拿掉 `always_xy=True` 會發生什麼事，哪個測試會抓到？② 為什麼面積要在 TWD97 算，不能在經緯度算？③ 來回轉換誤差 1e-6 mm 代表投影「正確」嗎？ |
| 徐昇式多邊形 | `spatial.thiessen`、`weights` | 04/03 | ① 為什麼要加 4 個虛擬遠點？`far` 太小時程式怎麼發現？② S06 在流域外，它的權重一定是 0 嗎？③ 權重和＝1 這個測試能抓到哪些錯、抓不到哪些錯？ |
| 面積雨量缺值規則 | `spatial.areal_rainfall` | 04/03、05/03 | ① 重新正規化權重隱含什麼假設？什麼雨型下會偏差很大？② `MIN_COVERAGE = 0.5` 怎麼定才有依據？③ 改用反距離加權補值，結果會怎樣變？ |
| API | `api.create_app` | 06/03、06/04 | ① 為什麼缺參數是 422、沒有時區是 400？② 查詢區間為什麼是 (start, end] 而不是 [start, end)？③ URL 裡的 `+` 為什麼要編碼？ |
| 監控 | `/metrics` | 07/04 | ① 為什麼每個 app 用自己的 `CollectorRegistry`？② 422 沒被計數，要怎麼補？③ 你會對哪個指標設告警、門檻多少？ |
| 容器與 manifest | `Dockerfile`、`k8s/` | 00/03、07/02、07/03 | ① liveness 的延遲為什麼比 readiness 長？② `readOnlyRootFilesystem` 會讓哪些套件出問題？③ replicas 改成 3 時，現在的設計哪裡會出錯？ |

## 前提與限制

- **資料是合成的**。真實來源（氣象署、水利署開放資料）的格式、時間標記、單位與授權，需逐一查官方說明；工作區連不到外部網站，未實作下載。
- **Docker 映像未建置成功**：建置環境的 Docker Hub 被擋（`Forbidden`），`python:3.13.18-slim-bookworm` 標籤是否存在未驗證。
- **k3d 與 manifest 未實測**（環境沒有 k3d）。`readOnlyRootFilesystem: true` 對 pyproj 的資料快取目錄是否有影響未驗證。
- API 已用 uvicorn 在本機實際啟動並以 curl 測試。
- 已知缺口：FastAPI 的 422 驗證錯誤不會計入自訂指標（測試 `test_validation_errors_not_counted_in_metrics` 記錄此行為）。
- 每次啟動都重跑 ETL、資料放在 emptyDir；多副本、持久化、排程更新都還沒做。
