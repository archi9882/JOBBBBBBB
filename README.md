# JOBBBBBBB：海嘯實驗室

用真正的海嘯模式 COMCOT 跑台灣海嘯情境，一晚 30 分鐘、一張卡，練出目標職缺要的三種能力：**數值模擬與物理判斷**、**自架基礎設施**、**否證 AI 的產出**。完成的卡會自動轉成履歷敘述。

```
第一次設定（一次，約 30 分鐘）
        │
        ▼
每晚一張卡（30 分鐘）：先猜 → 再跑 → 看圖 → 一句收穫 → 推上 GitHub
        │                         ▲
        └──── 33 張卡依序做 ───────┘
        │
        ▼
里程碑解鎖 → 履歷敘述自動產生
```

---

## 步驟 1　第一次設定（只做一次）

在 WSL 的 Ubuntu 終端機執行。專案放在 `~/JOB`，不要放在 `/mnt/c`（跨檔案系統會變慢）。

```bash
# 1. 下載專案
git clone https://github.com/archi9882/JOBBBBBBB.git ~/JOB
cd ~/JOB

# 2. 建立 Python 環境
conda env create -f environment.yml
conda activate jobprep

# 3. 安裝 Fortran 編譯器並編譯 COMCOT
sudo apt install gfortran
bash lab/tools/setup_comcot.sh          # 最後要看到「OK：…/comcot」

# 4. 確認一切正常
pytest                                   # 全部通過
python lab/tools/card.py                 # 顯示「0/33 張」與卡 01
```

**完成條件**：上面四步都沒有錯誤。卡住就把錯誤訊息貼給 Claude。

開啟 VS Code、啟動 Claude Code 的細節見 [startup.md](startup.md)。推送到 GitHub 的方法見 [WSL2GITHUB.md](WSL2GITHUB.md)。

---

## 步驟 2　每晚一張卡（30 分鐘）

**開工（2 分鐘）**

```bash
cd ~/JOB && conda activate jobprep && git pull
claude                                   # 啟動 Claude Code
```

在 Claude Code 說：**「下一張卡」**。

**做卡（25 分鐘）**

| 時間 | 你做什麼 |
|---|---|
| 0–5 分 | 讀 3 行背景，**先寫下預測**。還沒預測不准跑。 |
| 5–25 分 | 跑程式、看圖，和預測對照。實作卡則在 `lab/mine/` 寫自己的程式，用 `python lab/tools/card.py check` 驗收。 |
| 25–30 分 | 用一句話寫收穫。 |

**收工（3 分鐘）**

```bash
python lab/tools/card.py done <卡號> "一句收穫"   # 記錄並顯示進度條
git add -A && git commit -m "card <卡號>: <題目>" && git push
```

做完一張就停。預測錯了不扣分，錯得有趣的值得記下來。

**卡住時**
- 實作卡：`python lab/tools/card.py hint 1`（最多到 3）。
- 超過 30 分鐘：記下停在哪一步，明天從那裡接。
- 想到流程的改進：寫一行到 `lab/ideas.md`，週末再決定。

---

## 步驟 3　33 張卡的路線

| 階段 | 卡 | 你會得到 | 里程碑 |
|---|---|---|---|
| 上手 | 01–05 | 第一張海嘯圖；看懂滑移、時間步、震央定義；第一場拷問 | COMCOT 跑起來 |
| 物理與資料 | 06–16 | 走時計算、真實台灣地形、TWD97、文獻情境、規模換算、線性對非線性、網格收斂、潮位站清理、第一次否證 AI | 海嘯情境敏感度分析 |
| 服務 | 17–21 | 自己寫的模擬 API、Docker 映像、睡前批次跑 5 個情境 | 第一支模擬服務 |
| 自架平台 | 22–28 | 容量估算、k3d 部署、監控指標、故障演練、儲存架構決策紀錄 | 服務跑在 Kubernetes 上 |
| 混合方法 | 29–31 | 方法選擇、代理模型、外插失效 | 物理模擬加代理模型 |
| 作品集 | 32–33 | 否證案例集、陌生人能跑的 README、10 分鐘簡報 | 作品集完成 |

完整卡片在 [lab/cards.toml](lab/cards.toml)；實驗室說明見 [lab/README.md](lab/README.md)。

---

## 步驟 4　成果自動變成履歷

```bash
python tools/resume_gen.py --refresh
```

產出在 `resume/generated/`：
- `resume_table.md`：每條履歷敘述的狀態、還缺哪些卡、面試會被問什麼。
- `bullets_zh.md`、`bullets_en.md`：已解鎖的敘述，可直接貼進履歷。

解鎖條件寫在 [resume/claims.toml](resume/claims.toml)。否證 AI 的紀錄在 [docs/ai-falsification-log.md](docs/ai-falsification-log.md)，履歷只計算作者為「我」的筆數。

---

## 副線（卡片引導到時才做）

| 資料夾 | 內容 | 什麼時候用 |
|---|---|---|
| [reserve-numerics/](reserve-numerics/README.md) | 數值分析儲備課程 13 堂：守恆與驗證、淺水方程有限體積、計算幾何 | 想自己寫求解器，或專案 C 需要時 |
| [projects/A-flood-service](projects/A-flood-service) | 一維潰壩求解器加非同步 API（Claude 寫） | 拷問卡用來拆解求解器原理 |
| [projects/B-rain-etl-spatial](projects/B-rain-etl-spatial) | 雨量 ETL 與空間處理（Claude 寫） | 目前不用 |
| [projects/C-groundwater-bottomup](projects/C-groundwater-bottomup) | 地下水污染傳輸，由你從零寫，6 層關卡 | 實驗室做完之後；用 `python tools/gate.py` 看解鎖狀態 |
| [grill/](grill/README.md) | grill-me 拷問目標與分數 | 拷問卡 |
| [docs/archive/](docs/archive/phases/README.md) | 已封存的課程與舊待辦（附對照表） | 只供查閱 |

---

## 規則摘要

- `lab/mine/` 是你自己寫的程式，Claude 不寫、不改、不貼解答，只跑驗收、指出哪個測試失敗。
- `lab/tools/`、`lab/checks/`、`lab/cases.py` 是 Claude 寫的工具和驗收測試。
- 專案 C 由你從零寫，Claude 只拷問與審查。
- `lab/progress.json`、`lab/log.md`、`grill/scores.json`、`resume/generated/` 都由工具寫入，不手動改。
- 給 Claude Code 的完整規則在 [CLAUDE.md](CLAUDE.md)。

## 前提與限制

- COMCOT 使用中央大學 IHOS 海嘯研究群的 gfortran 版本（github.com/HandsomeAndy/comcot-gfortran）；gfortran 10 以上需要 `-fallow-argument-mismatch`，`setup_comcot.sh` 已處理。
- 卡 01–04 在 Claude 的環境實測過；之後的卡與在你的 WSL2 上的執行，以你實跑為準。
- 卡 08 之後需要下載真實地形與文獻資料，來源要自己核對。
