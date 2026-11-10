# 前置作業鏈（依序完成；每一步的前置是上一步）

Claude Code：開新工作階段時先讀這份，從第一個未勾選的步驟接著做。某一步的「完成條件」實際驗證通過後，才把 `[ ]` 改成 `[x]` 並 commit（訊息：`todo: 完成 NN`）。

執行環境：後續指令都在 WSL 的 `~/JOBBBBBBB` 跑（先 `conda activate jobprep`）；`C:\JOB` 只是同步副本，不要兩邊都改。

## 已完成（2026-11-09 前）
- [x] 01 儲存 grill-me 技能
- [x] 02 WSL2 工具（git 2.43.0、conda 26.9.4、Docker 29.9.3）
- [x] 03 clone 與 SSH 推送（git push 成功）
- [x] 04 conda 環境 jobprep（`~/.condarc` 已改為只用 conda-forge，避開 Anaconda 預設頻道的服務條款）
- [x] 05 pytest：62 passed
- [x] 06 ship_check 4/42、gate 六層全鎖定（結束碼 0）、resume_gen 0/12
- [x] 07 Docker Compose 跑專案 A：e2e `mode=compose`、`ok=true`

## 待辦
- [x] **08 看一遍專案 A 的拆解地圖**
  - 讀 `projects/A-flood-service/README.md` 的「拆解地圖」，把 `src/floodsvc/solver.py` 從頭到尾看一次（不用看懂）。
  - 完成條件：使用者自己確認。
- [ ] **09 第一場拷問：`grill me A/conservation-form`**
  - 拷問時不看程式碼回答；結束後 commit `grill/scores.json` 與 `grill/log/`。
  - 完成條件：該目標分數 ≥ 2（專案 C 第一層的解鎖條件之一）。之後依序：A/analytic-and-convergence、A/cfl-and-boundaries。
- [ ] **10 選授權條款（LICENSE）**
  - 不擋其他步驟，公開作品集前完成即可。
