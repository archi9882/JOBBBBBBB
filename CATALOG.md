# 課程目錄（由 gen 產生，勿手改）

### Phase 00　環境與工作方法（`00-setup-and-tooling`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [00/01](phases/00-setup-and-tooling/01-wsl-conda-git) | WSL2、conda 與 git | M2 | 新 clone 後 `conda env create` ＋ `pytest` 全部通過。 |
| [00/02](phases/00-setup-and-tooling/02-repo-and-pytest) | repo 結構與第一個測試 | M3 | `python tools/ship_check.py` 能列出每堂課的狀態。 |
| [00/03](phases/00-setup-and-tooling/03-docker-first-image) | 第一個 Docker 映像 | M2 | 容器輸出與本機輸出的 sha256 相同。 |
| [00/04](phases/00-setup-and-tooling/04-falsification-log) | AI 否證紀錄的方法 | M3 | docs/ai-falsification-log.md 有第一筆完整紀錄。 |

### Phase 01　守恆與驗證（`01-conservation-and-verification`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [01/01](phases/01-conservation-and-verification/01-control-volume-continuity) | 控制體積與連續方程 | M1 | 週期邊界下總水量相對誤差 < 1e-12；水丘中心位移＝u·t。 |
| [01/02](phases/01-conservation-and-verification/02-convergence-order) | 網格收斂與觀測收斂階 | M1 | 上風格式在平滑解上 p ≈ 1（0.9–1.1）。 |
| [01/03](phases/01-conservation-and-verification/03-manufactured-solutions) | 製造解（MMS） | M1 | MMS 誤差隨網格加密以理論階數下降。 |
| [01/04](phases/01-conservation-and-verification/04-lake-at-rest) | 靜水測試 | M1 | 1000 步後最大流速 < 1e-12 m/s。 |

### Phase 02　淺水方程有限體積法（`02-shallow-water-fv`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [02/01](phases/02-shallow-water-fv/01-saint-venant-and-cfl) | Saint-Venant 方程與 CFL | M1 | Δt 每步依 CFL 重算；Cr=1.2 時程式主動報錯。 |
| [02/02](phases/02-shallow-water-fv/02-lax-friedrichs) | Lax–Friedrichs 通量 | M1 | 濕床潰壩與 Stoker 解 L1 誤差隨 N 加倍而下降。 |
| [02/03](phases/02-shallow-water-fv/03-hll-flux) | HLL 近似 Riemann 解 | M1 | 相同 N 下 HLL 的激波寬度（格數）小於 LF。 |
| [02/04](phases/02-shallow-water-fv/04-dam-break-benchmark) | 潰壩解析解基準 | M1 | 基準函式通過守恆與邊界值檢查。 |
| [02/05](phases/02-shallow-water-fv/05-wet-dry-and-bed-slope) | 乾濕邊界與底床源項 | M1 | 第 01-04 課的靜水測試在新求解器上仍通過；水深永不為負。 |
| [02/06](phases/02-shallow-water-fv/06-sensitivity) | 敏感度分析 | M1 | 排序表＋說明哪個環節需要最嚴格的驗證。 |

### Phase 03　物理、資料或混合（`03-method-selection`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [03/01](phases/03-method-selection/01-decision-table) | 方法選擇決策表 | M1 | 三個案例各寫一頁判斷與理由，並列出會推翻判斷的條件。 |
| [03/02](phases/03-method-selection/02-surrogate-from-scratch) | 手刻代理模型 | M1 | 內插範圍內誤差 < 5%；與 PyTorch 版本梯度一致到 1e-6。 |
| [03/03](phases/03-method-selection/03-when-surrogate-fails) | 代理模型何時失效 | M1 | 畫出內插／外插誤差對照；提出拒絕使用的門檻。 |

### Phase 04　空間資訊（`04-spatial`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [04/01](phases/04-spatial/01-projections-twd97) | 投影與 TWD97 | S1 | 來回轉換誤差 < 1 mm；兩站距離與大圓距離差 < 0.1%。 |
| [04/02](phases/04-spatial/02-polygon-area-validity) | 多邊形面積與有效性 | S1 | 手寫面積與 shapely 一致到 1e-9；自相交多邊形被抓出。 |
| [04/03](phases/04-spatial/03-thiessen-weights) | 徐昇式多邊形權重 | S1 | 權重和＝1；對稱案例的權重與手算相同。 |
| [04/04](phases/04-spatial/04-delaunay-mesh-quality) | Delaunay 網格品質 | S1 | 品質報表：最小角分布、最差 10 個元素的位置。 |

### Phase 05　ETL 與資料品質（`05-etl`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [05/01](phases/05-etl/01-schema-and-units) | Schema 與單位 | E1 | 違反 schema 的列被拒收並記錄原因。 |
| [05/02](phases/05-etl/02-timezone-and-resample) | 時區與重新取樣 | E1 | 兩種來源合併後，同一場雨的時序對齊；resample 的區間與標籤有測試。 |
| [05/03](phases/05-etl/03-sentinels-and-quality) | 缺值哨兵與品質報表 | E1 | 品質報表：各站缺值率、重複數、異常值數。 |
| [05/04](phases/05-etl/04-idempotent-pipeline) | 可重跑的流程 | E1 | 連跑兩次輸出 sha256 相同。 |
| [05/05](phases/05-etl/05-autocorrelation-pitfall) | 時間序列自相關 | S2 | 模擬 AR(1) 序列，顯示 t 檢定的偽陽性率超過 5%。 |

### Phase 06　模擬服務 API（`06-service`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [06/01](phases/06-service/01-http-from-stdlib) | 用標準函式庫寫 HTTP 服務 | E2 | curl 測試四種狀態碼。 |
| [06/02](phases/06-service/02-job-queue-sqlite) | 用 SQLite 手寫工作佇列 | E2 | worker 中途被殺掉後，工作會回到 queued 或標記 failed，不會卡在 running。 |
| [06/03](phases/06-service/03-fastapi-runs) | FastAPI 非同步工作 API | E2 | 合約測試：5 個邊界情境（負 n、超大網格、重複送出等）。 |
| [06/04](phases/06-service/04-error-contract) | 錯誤格式與版本 | E2 | 所有錯誤回應通過同一個 schema 測試。 |

### Phase 07　自架平台（`07-self-hosted-platform`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [07/01](phases/07-self-hosted-platform/01-compose-api-worker) | Docker Compose：API＋worker | M2 | `docker compose up` 後送出一個模擬並取得結果。 |
| [07/02](phases/07-self-hosted-platform/02-k3d-manifests) | k3d 與 Kubernetes manifest | M2 | k3d 叢集上跑通，每個 Pod 都有資源限制與探針。 |
| [07/03](phases/07-self-hosted-platform/03-manifest-review-drill) | AI manifest 審查演練 | M2 | 至少找出 4 個地雷並各寫一句後果。 |
| [07/04](phases/07-self-hosted-platform/04-observability) | 監控：Prometheus＋Grafana | M2 | Grafana 看得到三個指標；故意製造失敗時告警觸發。 |
| [07/05](phases/07-self-hosted-platform/05-object-storage-adr) | 物件儲存選型 ADR | M2 | ADR 比較至少兩個方案，含 MinIO 社群版封存的影響（查證日期寫在文中）。 |
| [07/06](phases/07-self-hosted-platform/06-capacity-10x) | 10 倍容量估算 | M2 | 估算表＋第一個瓶頸＋改善方案。 |
| [07/07](phases/07-self-hosted-platform/07-failure-drills) | 故障演練 | M2 | 每個故障都有紀錄：預期、實際、修正。 |

### Phase 08　整合專案：流域淹水模擬服務（`08-capstone`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [08/01](phases/08-capstone/01-end-to-end) | 端到端執行 | ALL | 一行指令從原始資料跑到結果圖。 |
| [08/02](phases/08-capstone/02-adr-collection) | 架構決策紀錄集 | M2 | 每份 ADR 有可推翻的條件。 |
| [08/03](phases/08-capstone/03-falsification-casebook) | 否證案例集 | M3 | 涵蓋至少 4 種錯誤類型。 |

### Phase 09　作品集（`09-portfolio`）

| 課 | 標題 | 能力 | 通過條件 |
|---|---|---|---|
| [09/01](phases/09-portfolio/01-readme-and-demo) | README 與展示 | ALL | 陌生人照 README 能跑出結果。 |
| [09/02](phases/09-portfolio/02-talk) | 10 分鐘簡報 | ALL | 錄影一次並自評。 |
