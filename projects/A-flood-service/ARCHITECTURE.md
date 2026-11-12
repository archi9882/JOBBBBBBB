# 專案 A 架構註記：每個檔案的作用與資料流

規則來源：根目錄 `CLAUDE.md`「註記文件」。新增、刪除或改變檔案職責時，同一個 commit 要更新本檔。

## 1. 檔案一覽

### 套件 `src/floodsvc/`

| 檔案 | 作用 | 拷問目標 |
|---|---|---|
| `__init__.py` | 標記資料夾為 Python 套件，只有一行說明 | 無 |
| `solver.py` | 數值求解器：1D 淺水方程有限體積法，HLL 通量、前進 Euler、CFL 控制 Δt、透射邊界、乾床處理。入口 `dam_break`，回傳 `Result` | A/conservation-form、A/hll-flux、A/cfl-and-boundaries、A/wet-dry |
| `analytic.py` | 解析解：Ritter（下游乾床）、Stoker（下游濕床，用 brentq 解中間水深）。當作標準答案比對求解器 | A/analytic-and-convergence |
| `jobs.py` | SQLite 手寫工作佇列：狀態 queued → running → done 或 failed；`BEGIN IMMEDIATE` 認領、心跳、逾時重排 | A/job-queue |
| `worker.py` | 背景行程：取工作 → `dam_break` → `stoker` 算誤差 → 寫回結果。`python -m floodsvc.worker` 啟動 | A/job-queue |
| `api.py` | FastAPI：`POST /v1/runs`（202、Idempotency-Key）、`GET /v1/runs/{id}`、`GET /healthz`，錯誤用 RFC 9457 | A/api-contract |

### 測試 `tests/`

| 檔案 | 作用 |
|---|---|
| `conftest.py` | 把 `src/` 加入匯入路徑 |
| `test_a_solver.py` | 測求解器與解析解：Stoker 中間態、解析解守恆、數值質量守恆與水深非負、收斂到 Stoker、乾床前緣落後但收斂、不合法 CFL 被拒 |
| `test_a_service.py` | 測 API 與佇列：202 與 Location、不合法輸入回 problem+json、Idempotency-Key、未知 id 回 404、搭配 worker 的端到端、認領互斥、逾時重排後失敗、求解器例外標為 failed |

### 部署與工具

| 檔案 | 作用 | 拷問目標 |
|---|---|---|
| `Dockerfile` | 同一個映像給 api 與 worker 用，啟動指令由 compose 決定；非 root 使用者 | A/deployment |
| `compose.yaml` | 兩個服務 `api`、`worker`，共用 volume `simdata`（放 SQLite 檔），worker 等 api 健康檢查通過才啟動 | A/deployment |
| `requirements.txt` | 映像內的相依套件 | 無 |
| `scripts/e2e.sh` | 對執行中的服務送一個模擬、輪詢到完成，成功時寫出 `e2e.json` | A/deployment |
| `e2e.json` | `e2e.sh` 的輸出（`ok`、`mode`、`at`、`l1`），給 `metrics.py` 讀 | 無 |
| `metrics.py` | 跑驗證案例與測試，寫出 `metrics.json` | 無 |
| `metrics.json` | `metrics.py` 的輸出，`tools/resume_gen.py` 讀它產生履歷生產表 | 無 |

### 文件

| 檔案 | 作用 |
|---|---|
| `README.md` | 專案說明與「拆解地圖」 |
| `falsification.md` | Claude 被測試或實跑推翻的說法紀錄 |
| `src/solver.md` | 使用者的學習筆記：solver 逐項說明、手算範例、質量守恆條件 |
| `ARCHITECTURE.md` | 本檔 |

## 2. 資料流

### 服務流程（Docker Compose 下是兩個獨立行程）

```
使用者 ──POST /v1/runs──> api.py ──建立 queued 工作──> jobs.py ──> SQLite（simdata volume）
                                                                      │
                                            worker.py 迴圈：認領 + 心跳 ┘
                                              │
                                              ├─> solver.dam_break  ──> Result（h、u、mass0、mass）
                                              ├─> analytic.stoker   ──> 解析解 h、u
                                              └─> 算 L1 誤差、質量相對誤差 ──> 寫回 jobs.py（done）

使用者 ──GET /v1/runs/{id}──> api.py ──讀取──> jobs.py ──> 回傳狀態；done 時附結果
```

api 與 worker 只透過 SQLite 溝通，沒有直接呼叫。這是它們能分開部署的原因。

### 求解器內部（`solver.dam_break` 每一步）

```
_velocity(h, hu) ──> smax ──> dt = cfl·dx/smax
補虛擬格（透射邊界）──> hll_flux ──┬─> _velocity（uL、uR）
                                   └─> _flux（FL、FR）
通量差 ──> 更新 h、hu ──> 乾床修正 ──> 下一步
```

### 驗證與履歷流程

```
tests/ ─┐
        ├─> metrics.py ──> metrics.json ──┐
e2e.sh ──> e2e.json ─────────────────────┤
                                          └─> tools/resume_gen.py ──> resume/generated/
```

## 3. 依賴方向

- `api.py` 依賴 `jobs.py`，不依賴 `solver.py`、`analytic.py`。
- `worker.py` 依賴 `jobs.py`、`solver.py`、`analytic.py`。
- `solver.py`、`analytic.py` 不依賴其他專案內檔案，可單獨測試。
- `metrics.py` 直接匯入 `solver`、`analytic`。
