# JOBBBBBBB：海嘯實驗室

用真正的海嘯模式 COMCOT 跑台灣海嘯情境，一晚 30 分鐘、一張卡，練出目標職缺要的三種能力：**數值模擬與物理判斷**、**自架基礎設施**、**否證 AI 的產出**。完成的卡會自動轉成履歷敘述。

```
第一次設定（一次，約 30 分鐘）
        │
        ▼
每晚一張卡（30 分鐘）：先猜 → 再跑 → 看圖 → 一句收穫 → 推上 GitHub
        │                         ▲
        └── 34 張卡，兩條軌各自往前 ──┘
        │
        ▼
里程碑解鎖 → 履歷敘述自動產生
```

---

## 步驟 1　第一次設定（只做一次）

**先確認環境**（PowerShell）：`wsl --list --verbose`，VERSION 要是 2（WSL 1 不支援 Claude Code）。專案放在 WSL 的 `~/JOB`，不要放 `/mnt/c`（跨檔案系統會變慢）。

在 WSL 的 Ubuntu 終端機執行：

```bash
# 1. 下載專案
git clone git@github.com:archi9882/JOBBBBBBB.git ~/JOB     # 用 SSH，推送時不問密碼
cd ~/JOB

# 2. 建立 Python 環境
conda env create -f environment.yml
conda activate jobprep
pip install torch --index-url https://download.pytorch.org/whl/cpu   # PINN 軌（卡 34 起）需要

# 3. 安裝 Fortran 編譯器並編譯 COMCOT（海嘯軌的卡 01–16 才需要）
sudo apt install gfortran
bash lab/tools/setup_comcot.sh          # 最後要看到「OK：…/comcot」

# 4. 安裝 Claude Code（不需要先裝 Node.js）
curl -fsSL https://claude.ai/install.sh | bash

# 5. 確認一切正常
pytest                                   # 全部通過
python lab/tools/card.py                 # 顯示「0/34 張」、海嘯 0/24、PINN 0/10
```

**VS Code**：先在 Windows 的 VS Code 安裝「WSL」擴充套件（Microsoft 出的），之後在 `~/JOB` 執行 `code .`，左下角出現 `WSL: Ubuntu` 就對了。內建終端機（`` Ctrl+` ``）要選 **bash**，不要用 PowerShell、cmd、Git Bash。

**完成條件**：上面五步都沒有錯誤。卡住就把錯誤訊息貼給 Claude。推送到 GitHub 的方法見 [WSL2GITHUB.md](WSL2GITHUB.md)。

---

## 步驟 2　每晚一張卡（30 分鐘）

**開工前置流程（2 分鐘，每次都照這個順序）**

```bash
cd ~/JOB            # 1. 進專案（提示列要像 你@電腦:~/JOB$，不是 /mnt/c）
conda activate jobprep   # 2. 進 Python 環境，提示列前面會出現 (jobprep)
git pull            # 3. 同步；若出現衝突，先貼給 Claude，不要自己硬解
code .              # 4. 要用 VS Code 才需要；確認左下角 WSL: Ubuntu
claude              # 5. 啟動 Claude Code
```

在 Claude Code 說：**「下一張卡」**（或「今天做什麼」）。它會顯示兩條軌各自的下一張，要做另一條就說軌名或卡號。

出狀況時先查這三件：

| 症狀 | 原因與處理 |
|---|---|
| `conda: command not found` | conda 沒裝在 WSL；照步驟 1 重做環境 |
| `ModuleNotFoundError`（torch、numpy…） | 忘了 `conda activate jobprep`，每開一個新終端機都要做 |
| `claude` 出現 `Exec format error` | 你在 WSL 1；用 `wsl --set-version <發行版> 2` 升級 |

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

## 步驟 3　34 張卡的路線（兩條軌，可以平行做）

**海嘯軌（24 張）**

| 階段 | 卡 | 你會得到 | 里程碑 |
|---|---|---|---|
| 上手 | 01、03、05 | 第一張海嘯圖；看懂星號與隆起區；第一場拷問 | COMCOT 跑起來 |
| 物理與資料 | 06–16 | 走時、真實台灣地形、TWD97、文獻情境、規模換算、網格收斂、潮位站清理、第一次否證 AI | 海嘯情境敏感度分析 |
| 服務 | 17–21 | 模擬 API、Docker 映像、睡前批次跑 5 個情境 | 第一支模擬服務 |
| 自架平台 | 23–28 | 容量計算器、k3d 部署、監控指標、儲存架構決策紀錄 | 服務跑在 Kubernetes 上 |
| 混合方法 | 30 | 代理模型 | 物理模擬加代理模型 |
| 作品集（最後做） | 32–33 | 否證案例集、陌生人能跑的 README | 作品集完成 |

**PINN 軌（10 張）**

| 卡 | 你會得到 | 里程碑 |
|---|---|---|
| 34–36 | 一頁紙看懂 PINN；自己寫自動微分殘差與第一個 PINN | 第一個 PINN |
| 38–40 | 因果權重；和跳蛙法公平賽跑；從測站反求水深 | 公平比較 |
| 41 | 傅立葉神經算子的核心層 | FNO |
| 43 | 叫 AI 寫 PINN，用你的驗收否證它 | PINN 的真正用武之地 |
| 44–45 | 摩擦項；只給水位能不能反求摩擦係數 | 水文學延伸 |

除了卡 01，預測都併進各張卡的開頭：先猜，寫完才能跑。

完整卡片在 [lab/cards.toml](lab/cards.toml)；實驗室說明見 [lab/README.md](lab/README.md)。

---

## 步驟 4　成果自動變成履歷

```bash
python tools/resume_gen.py
```

產出在 `resume/generated/`：
- `resume_table.md`：每條履歷敘述的狀態、還缺哪些卡、面試會被問什麼。
- `bullets_zh.md`、`bullets_en.md`：已解鎖的敘述，可直接貼進履歷。

解鎖條件寫在 [resume/claims.toml](resume/claims.toml)。否證 AI 的紀錄在 [docs/ai-falsification-log.md](docs/ai-falsification-log.md)，履歷只計算作者為「我」的筆數。

---

## 副線（卡片引導到時才做）

| 資料夾 | 內容 | 什麼時候用 |
|---|---|---|
| [reserve-numerics/](reserve-numerics/README.md) | 數值分析儲備課程 13 堂：守恆與驗證、淺水方程有限體積、計算幾何 | 想自己寫求解器，或 PINN 卡需要對照基準時 |
| [grill/](grill/README.md) | grill-me 拷問目標與分數 | 拷問卡 |
| [docs/archive/](docs/archive/phases/README.md) | 已封存的課程、舊待辦，以及 2026-11-16 封存的專案 A、B、C | 只供查閱 |

---

## 規則摘要

- `lab/mine/` 是你自己寫的程式，Claude 不寫、不改、不貼解答，只跑驗收、指出哪個測試失敗。
- `lab/tools/`、`lab/checks/`、`lab/cases.py` 是 Claude 寫的工具和驗收測試。
- `lab/progress.json`、`lab/log.md`、`grill/scores.json`、`resume/generated/` 都由工具寫入，不手動改。
- 給 Claude Code 的完整規則在 [CLAUDE.md](CLAUDE.md)。

## 前提與限制

- COMCOT 使用中央大學 IHOS 海嘯研究群的 gfortran 版本（github.com/HandsomeAndy/comcot-gfortran）；gfortran 10 以上需要 `-fallow-argument-mismatch`，`setup_comcot.sh` 已處理。
- 卡 01–04 在 Claude 的環境實測過；之後的卡與在你的 WSL2 上的執行，以你實跑為準。
- 卡 08 之後需要下載真實地形與文獻資料，來源要自己核對。
