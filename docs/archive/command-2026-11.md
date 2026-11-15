# command.md：專案指令速查

來源：`CLAUDE.md`、`TODO.md`、`pytest.ini`、`environment.yml`、`.github/workflows/ci.yml`、各專案 README 與 `scripts/`、`k8s/README.md`。
執行環境：WSL2 的 `~/JOBBBBBBB`，先啟用 conda 環境。標記「未實測」的指令沒有實際跑過，格式以官方文件為準。

## 1. 環境

```bash
conda env create -f environment.yml      # 建立 jobprep（python 3.12、numpy、pandas、scipy、shapely、pyproj、pytest）
conda activate jobprep                   # 之後所有指令的前提
```

CI 用的最小安裝（不走 conda 時）：

```bash
pip install numpy pandas scipy shapely pyproj pytest fastapi uvicorn httpx prometheus-client
```

## 2. 測試

```bash
pytest                                   # 全部測試（pytest.ini 已含 -q --import-mode=importlib，目前 62 個）

# 專案 A 單獨跑（17 個），需把 src/ 放進 PYTHONPATH
cd projects/A-flood-service
PYTHONPATH=src python -m pytest -o addopts= -q tests

# 專案 B 單獨跑（26 個），在 repo 根目錄
python -m pytest -o addopts= -q --import-mode=importlib projects/B-rain-etl-spatial/tests
```

注意：在子程序解析「N passed」時要用 `-o addopts=--import-mode=importlib -q`，否則兩個 `-q` 會讓摘要行消失。

## 3. 進度與關卡工具（repo 根目錄）

```bash
python tools/ship_check.py               # 42 堂課出貨狀態（math.md、code、tests、falsification.md 四項）
python tools/ship_check.py --run         # 另外對已齊全的課跑 pytest
python tools/gate.py                     # 專案 C 關卡：哪些層已解鎖、還缺什麼；未解鎖層放 .py 會失敗
python tools/resume_gen.py --refresh     # 先重跑 A、B 的 metrics.py，再產生 resume/generated/（勿手改輸出）
python tools/resume_gen.py               # 不重跑 metrics，直接依現有證據產生
python tools/gen.py                      # 改 tools/curriculum.py 後重產課程骨架
```

## 4. 專案 A：flood-service（FastAPI + worker）

```bash
cd projects/A-flood-service
python metrics.py                        # 寫出 metrics.json（履歷生產表會讀）
```

方式一：Docker Compose（已實測，e2e `mode=compose`、`ok=true`）

```bash
docker compose up --build -d             # 啟動 api + worker，共用資料卷 simdata
bash scripts/e2e.sh                      # 送出模擬並等結果，成功時寫出 e2e.json
docker compose down                      # 停止服務（加 -v 會一併刪除資料卷）
```

方式二：不用 Docker

```bash
cd projects/A-flood-service
PYTHONPATH=src uvicorn floodsvc.api:app --port 8000 &
PYTHONPATH=src python -m floodsvc.worker &
MODE=local bash scripts/e2e.sh           # BASE 預設 http://localhost:8000
```

手動呼叫 API：

```bash
curl http://localhost:8000/healthz
curl -X POST http://localhost:8000/v1/runs -H 'Content-Type: application/json' \
     -d '{"h_left":10,"h_right":1,"cells":400}'
curl http://localhost:8000/v1/runs/<id>
```

## 5. 專案 B：rain-etl-spatial

```bash
python projects/B-rain-etl-spatial/metrics.py     # 跑完整流程並寫出 metrics.json
```

本機啟動 API：

```bash
cd projects/B-rain-etl-spatial
PYTHONPATH=src RAINB_WORK_DIR=/tmp/rainb uvicorn rainb.api:default_app --factory --port 8000
curl "http://localhost:8000/v1/areal-rainfall?start=2026-06-01T09:00:00%2B08:00&end=2026-06-01T12:00:00%2B08:00"
curl http://localhost:8000/metrics
```

URL 中的 `+08:00` 必須寫成 `%2B08:00`，否則 API 回 422。

容器與 k3d 部署（未實測）：

```bash
cd projects/B-rain-etl-spatial
docker build -t rain-etl-spatial:0.1.0 .
docker run --rm rain-etl-spatial:0.1.0 python -m pytest -q -p no:cacheprovider tests

k3d cluster create rainb
k3d image import rain-etl-spatial:0.1.0 -c rainb
kubectl apply -f k8s/
kubectl rollout status deploy/rainb
kubectl port-forward svc/rainb 8080:80
curl http://localhost:8080/metrics
```

## 6. 專案 C 與拷問

- 專案 C（`projects/C-groundwater-bottomup/`）由使用者從零寫，Claude 只拷問與審查。
- 拷問指令（在 Claude Code 對話中輸入，目標清單見 `grill/targets.toml`）：

```text
grill me A/conservation-form
grill me A/analytic-and-convergence
grill me A/cfl-and-boundaries
```

## 7. Git

```bash
git status
git add <檔案>
git commit -m "todo: 完成 NN"            # TODO.md 步驟驗證通過後才勾選並 commit
git push                                 # 推送後到 GitHub Actions 頁確認 ci.yml 首次執行結果
```

## 8. CI（`.github/workflows/ci.yml`，每次 push 與 PR 觸發）

依序執行：`pytest` → `python tools/ship_check.py --run` → `python tools/gate.py` → `python tools/resume_gen.py --refresh` → 上傳 `resume/generated/`。本機跑同一組即可預先檢查。

## 9. 不要手動做的事

- 不改 `grill/scores.json`（只由 grill-me 拷問結束時寫入）。
- 不改 `resume/generated/`（`tools/resume_gen.py` 的輸出）。
- 不在專案 C 未解鎖的層放 `.py`。
