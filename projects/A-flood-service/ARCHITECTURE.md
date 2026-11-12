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

## 4. 指令流程：三層關卡

以下指令都在 `projects/A-flood-service` 底下執行，環境為 WSL 的 `jobprep`。

### 指令格式

兩種常用指令都是同一個骨架：

```
環境變數=值   python   <怎麼啟動>   <參數>
```

| 部分 | 跑測試 | 跑求解器 |
|---|---|---|
| 環境變數 | `PYTHONPATH=src` | `PYTHONPATH=src` |
| 直譯器 | `python` | `python` |
| 怎麼啟動 | `-m pytest`：把 pytest 當程式執行 | `-c "..."`：直接執行引號內的一段 Python |
| 參數 | `-o addopts= -q tests` | 引號內的程式碼 |

- `PYTHONPATH=src`：只對這條指令生效，讓 Python 去 `src/` 找 `floodsvc` 套件。沒有它，`import floodsvc` 會失敗。（測試另有 `tests/conftest.py` 加入 `src/`，所以對測試可能是多餘的，但沿用 CLAUDE.md 的完整寫法。）
- `-m pytest`：pytest 自己到 `tests/` 找 `test_*.py`，執行每個 `test_` 開頭的函式，回報通過或失敗。
- `-o addopts=`：清空 `pytest.ini` 預設的 `-q`，避免與自己加的 `-q` 疊成兩個，使結尾的「N passed」摘要行消失。
- `-c "..."`：自己寫一小段程式當場執行。

差別：跑測試是讓 pytest 去檢查程式；跑求解器是自己呼叫函式，看它回傳什麼。

### 三層關卡

| 關 | 指令 | 動作 | 代表 | 輸出 |
|---|---|---|---|---|
| 一：單元測試 | `PYTHONPATH=src python -m pytest -o addopts= -q tests` | 不啟動服務，直接呼叫函式比對答案 | 每個零件各自正確 | `17 passed` |
| 二：指標 | `python metrics.py` | 跑驗證案例與測試，寫成 `metrics.json` | 把精度變成可留存的數字 | `metrics.json` |
| 三：端到端 | 見下方 | 啟動 api 與 worker，送請求並等結果 | 零件組合起來能運作 | `e2e.json`（`ok: true`） |

第三關有兩種做法：

```bash
# 方式一：Docker Compose
docker compose up --build -d     # 建映像並在背景啟動 api 與 worker
bash scripts/e2e.sh              # 送一個模擬請求，輪詢直到完成
docker compose down              # 關掉服務

# 方式二：不用 Docker
uvicorn floodsvc.api:app --port 8000 &    # 啟動 API，放背景
python -m floodsvc.worker &               # 啟動 worker，放背景
MODE=local bash scripts/e2e.sh            # 送請求並等結果
```

| 關 | 啟動服務 | 驗證範圍 | 失敗代表 |
|---|---|---|---|
| 一 | 否 | 單個函式 | 某段邏輯寫錯 |
| 二 | 否 | 整體精度 | 數字不夠準 |
| 三 | 是 | 整個系統 | 零件之間接不起來，或部署設定錯 |

### 直接呼叫求解器

```bash
PYTHONPATH=src python -c "from floodsvc.solver import dam_break; r = dam_break(10, 1); print(r.mass0, r.mass, r.steps)"
```

預設參數下實測輸出 `5500.0 5500.0 120`：初始水量 5500、結束水量 5500（20 秒內波未到邊界，故守恆）、共 120 步。
