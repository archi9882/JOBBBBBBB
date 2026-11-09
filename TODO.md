# 前置作業鏈（依序完成；每一步的前置是上一步）

Claude Code：開新工作階段時先讀這份，從第一個未勾選的步驟接著做。某一步的「完成條件」實際驗證通過後，才把 `[ ]` 改成 `[x]` 並 commit（訊息：`todo: 完成 NN`）。

- [x] **01 儲存 grill-me 技能**
  - claude.ai 已儲存（2026-11-08）。Claude Code 版本在 `.claude/skills/grill-me/`，隨 repo 同步。
- [x] **02 WSL2 備齊工具**：git、Miniconda、Docker Desktop（開啟 WSL2 integration）
  - 完成條件：`git --version`、`conda --version`、`docker run hello-world` 都成功。
- [x] **03 clone repo 並設定推送權限**
  - `git clone https://github.com/archi9882/JOBBBBBBB.git`；設定 SSH key 或 Personal Access Token。
  - 完成條件：`git push` 成功。
- [x] **04 建立 conda 環境**
  - `conda env create -f environment.yml && conda activate jobprep`
  - 完成條件：`python -c "import fastapi, shapely, pyproj, prometheus_client"` 不報錯。
- [x] **05 跑全部測試**
  - `pytest`
  - 完成條件：62 passed。失敗時把錯誤記進 `docs/ai-falsification-log.md`（作者：我），這是你的第一筆否證紀錄。
- [x] **06 跑三個檢查工具**
  - `python tools/ship_check.py --run`（預期 4/42 出貨）
  - `python tools/gate.py`（預期專案 C 六層全鎖定，結束碼 0）
  - `python tools/resume_gen.py --refresh`（預期 0/12 解鎖），打開 `resume/generated/resume_table.md` 看缺什麼。
  - 完成條件：三個指令都跑完且結果與預期一致。
- [ ] **07 用 Docker Compose 跑專案 A**
  - `cd projects/A-flood-service && docker compose up --build -d && bash scripts/e2e.sh && python metrics.py`
  - commit 並 push `e2e.json` 與 `metrics.json`。
  - 完成條件：`e2e.json` 中 `"mode": "compose"`、`"ok": true`。這是 Claude 雲端環境無法實測的部分。
- [ ] **08 看一遍專案 A 的拆解地圖**
  - 讀 `projects/A-flood-service/README.md` 的「拆解地圖」，把 `src/floodsvc/solver.py` 從頭到尾看一次（不用看懂）。
  - 完成條件：使用者自己確認。
- [ ] **09 第一場拷問：`grill me A/conservation-form`**
  - 拷問時不看程式碼回答；結束後 commit `grill/scores.json` 與 `grill/log/`。
  - 完成條件：該目標分數 ≥ 2（專案 C 第一層的解鎖條件之一）。之後依序：A/analytic-and-convergence、A/cfl-and-boundaries。
- [ ] **10 選授權條款（LICENSE）**
  - 不擋其他步驟，公開作品集前完成即可。
