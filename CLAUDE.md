# CLAUDE.md：給 Claude Code 的專案規則

這個 repo 是使用者應徵「數值模擬 × 自架基礎設施 × 生成式 AI 否證」職缺的作品集與訓練場。全程用繁體中文回覆，技術名詞附英文，回報簡短。

## 主線：海嘯實驗室（2026-11-15 起）
- 使用者每次只有約 30 分鐘。**一晚一張卡**：先猜 → 再跑 → 看圖 → 一句收穫。卡片在 `lab/cards.toml`，流程見 `.claude/skills/card/`。
- 使用者說「下一張卡」「今天做什麼」或開新工作階段沒有特別指示時：執行 `python lab/tools/card.py`，照 card 技能進行。
- 做完一張就停，問要不要再一張。不主動延長，不在卡片中途提出新流程。

## 流程預算（重要）
- 新增任何規則、文件或步驟之前，必須先刪掉或合併一個，並在 commit 訊息說明刪了什麼。
- 想到的改進一律寫進 `lab/ideas.md` 一行，留到使用者週末決定。
- 不要求使用者寫說明文件（ARCHITECTURE.md 之類）；需要時由 Claude 寫。

## 誰寫程式
- `lab/tools/`、`lab/cases.py`、`lab/checks/`：Claude 可以寫（工具與驗收測試）。卡片的預測、判讀與收穫由使用者做。
- **`lab/mine/`：使用者自己寫的程式（實作卡）。Claude 不寫、不改、不貼解答**，只讀、跑驗收、指出哪個測試失敗；規則細節見 card 技能。
- `reserve-numerics/`（數值分析儲備課程）依 `docs/depth-tiers.md` 分級（A 親手做、B Agent 做使用者驗收、C 只讀懂）。儲備課程是副線，卡片引導到時才做。

## 不可以做的事
- 不手動修改 `grill/scores.json`（只由 grill-me 依實際表現寫入）與 `resume/generated/`（由 `tools/resume_gen.py` 產生）。
- 不手動修改 `lab/progress.json`、`lab/log.md`（由 `lab/tools/card.py` 寫入）。
- `docs/ai-falsification-log.md` 的「作者」欄：使用者抓到的寫「我」，Claude 抓到或犯的寫「Claude」。

## 常用指令
```bash
python lab/tools/card.py                # 下一張卡與進度
python lab/tools/run_case.py <情境>     # 跑 COMCOT 情境
pytest                                  # 全部測試
python tools/resume_gen.py              # 履歷生產表
```
- `pytest.ini` 已有 `addopts = -q`；子程序解析「N passed」時用 `-o addopts=--import-mode=importlib -q`。

## 驗證習慣
- 數值、API 用法、套件預設值都以實跑為準；說法被推翻就記到對應的 `falsification.md`。
- 文獻與外部資料來源要實際查證，查不到標「未查證」。

## 繪圖規則
- 地圖類的圖一律呼叫 `lab/tools/plot.py` 的 `geo_style()`（GMT 風格：°E/°N 刻度、黑白交替邊框、比例尺），不另寫樣式。
