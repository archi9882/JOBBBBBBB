# 專案 A：淹水模擬服務（速成版，Claude 撰寫）

一維潰壩淹水模擬，包成可非同步呼叫的服務：

```
POST /v1/runs ──► SQLite 佇列 ──► worker ──► HLL 有限體積求解器 ──► 與 Stoker／Ritter 解析解比較 ──► 結果
     ▲                                                                                              │
     └──────────────────────────── GET /v1/runs/{id} ◄───────────────────────────────────────────────┘
```

**這是速成版**：Claude 寫好、能跑、有測試。你的工作不是重寫，而是用 grill-me 逐段拆解，直到每一行都能自己解釋（見下方「拆解地圖」）。拆解通過的元件，才會解鎖對應的履歷敘述。

## 執行（WSL2 Ubuntu）

```bash
cd projects/A-flood-service
pip install -r requirements.txt
PYTHONPATH=src python -m pytest -o addopts= -q tests     # 17 個測試
python metrics.py                                         # 寫出 metrics.json

# 方式一：Docker Compose
docker compose up --build -d
bash scripts/e2e.sh                                       # 寫出 e2e.json（mode=compose）

# 方式二：不用 Docker
export PYTHONPATH=$PWD/src FLOODSVC_DB=/tmp/fs.db
uvicorn floodsvc.api:app --port 8000 &
python -m floodsvc.worker &
MODE=local bash scripts/e2e.sh
```

## 檔案

| 檔案 | 內容 | 行數 |
|---|---|---|
| `src/floodsvc/solver.py` | 守恆形式 SWE、HLL 通量、CFL 時間步、透射邊界、乾床處理 | 71 |
| `src/floodsvc/analytic.py` | Ritter 與 Stoker 解析解（brentq 解中間水深） | 40 |
| `src/floodsvc/jobs.py` | SQLite 佇列：原子性 claim、心跳、逾時重排、冪等鍵 | 94 |
| `src/floodsvc/worker.py` | 取工作、求解、比對解析解、寫回結果 | 53 |
| `src/floodsvc/api.py` | FastAPI：202＋Location、problem+json、輸入上限、Idempotency-Key | 92 |
| `compose.yaml`、`Dockerfile` | api＋worker 兩個服務、共用資料卷、健康檢查、非 root | — |
| `metrics.py` | 產生 metrics.json 給履歷生產表 | — |

## 實測結果（Claude 環境，2026-11-08）

| 項目 | 值 |
|---|---|
| Stoker 濕床潰壩（h_l=10、h_r=1、t=20 s、N=400）L1 誤差 | 33.16 m² |
| 觀測收斂階（N=400→800） | 0.927（N=200→400 為 0.664） |
| 總水量相對誤差 | 0（波未到邊界前，通量守恆） |
| 乾床最小水深 | 0（未出現負水深） |
| 乾床前緣（h > 1 mm）落後 Ritter 解 | N=400：57.5 m；800：45.0 m；1600：34.4 m；3200：25.6 m |
| 測試 | 17 個通過 |
| 端到端 | uvicorn＋worker 兩個行程實跑成功；**Docker Compose 未實測**（工作區連不到 Docker Hub） |

## 拆解地圖（grill-me 的題庫來源）

每個元件對應課程的 lesson。grill-me 會從這裡挑問題；這裡只列問題，不給答案。

| 元件 | 對應課程 | grill-me 要追問的事 |
|---|---|---|
| `solver.py` 守恆形式 | 02/01、01/01 | 為什麼更新 hu 而不是 u？若改成更新 u，激波速度會怎樣？ |
| `hll_flux` | 02/03 | S_L、S_R 為什麼取左右特徵速度的極值？ `SL >= 0` 時為什麼直接用 F_L？ |
| CFL 時間步 | 02/01 | `smax` 為什麼是 \|u\|+√(gh) 的最大值？固定 Δt 在哪個時刻最先出事？ |
| 透射邊界 | 02/02 | 虛擬格複製邊界值代表什麼物理條件？波打到邊界時總水量測試會怎樣？ |
| 乾床處理 | 02/05 | `H_DRY` 設太大、太小各會發生什麼？截掉負水深時質量還守恆嗎？ |
| `analytic.stoker` | 02/04 | 中間狀態的兩個方程各來自哪個守恆律？brentq 的搜尋區間為什麼是 (h_r, h_l)？ |
| 收斂階 0.66→0.93 | 01/02 | 為什麼不是 1？哪一部分的解拖慢收斂？ |
| 前緣落後 | 02/05、03/03 | 前緣落後對淹水範圍預報代表什麼？要怎麼量才公平？ |
| `jobs.claim` | 06/02 | 拿掉 `BEGIN IMMEDIATE` 會發生什麼？怎麼寫測試證明？ |
| 心跳與逾時重排 | 06/02、07/07 | worker 被 kill -9 時工作狀態如何回復？重排會不會讓同一工作跑兩次？ |
| `api.py` 202＋Location | 06/03 | 為什麼不直接在 POST 裡跑完模擬？ |
| Idempotency-Key | 06/04 | 同 key 不同參數為什麼回 409？客戶端重送的情境有哪些？ |
| 輸入上限 `cells ≤ 20000` | 06/03、07/06 | 這個上限怎麼從記憶體與時間估出來？ |
| 每請求開連線 | 06/03 | 為什麼不能共用一條 sqlite3 連線？（見 falsification.md） |
| Compose 共用 SQLite 資料卷 | 07/01、07/06 | 這個設計在 worker 擴到 10 個時哪裡先壞？要換成什麼？ |

## 前提與限制

- 物理：平底、無摩擦、一維、矩形斷面、只有向下游潰壩。Manning 摩擦與地形源項留給專案 C 或課程 02/05。
- 數值：一階 HLL＋前進 Euler；乾濕前緣以簡單截斷處理，前緣明顯落後解析解。
- 服務：SQLite 佇列只適合單機低併發；沒有認證；結果存在資料庫而非物件儲存。
- 未實測：Docker Compose（無法從 Docker Hub 拉映像）、在 WSL2 上執行。`requirements.txt` 版本是 Claude 環境的版本，FastAPI 等套件 API 請以官方文件確認。
