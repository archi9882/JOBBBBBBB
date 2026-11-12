# CLAUDE.md：給 Claude Code 的專案規則

這個 repo 是使用者應徵「數值模擬 × 自架基礎設施 × 生成式 AI 否證」職缺的作品集與訓練場。全程用繁體中文回覆，技術名詞附英文，回報簡短。

## 開工時先做
1. 讀 `TODO.md`，從第一個未勾選的步驟接著做或引導使用者做。步驟的完成條件實際驗證通過後才打勾並 commit。
2. 需要背景時讀 `README.md`（路線與目錄）與 `docs/depth-tiers.md`（每堂課由誰做）。

## 路線
速成專案 A、B（Claude 寫好）→ 講解（拷問前先逐元件白話講解，假設使用者沒有背景，附小數字例子，不計分；使用者說「先教」或拷問中卡住時進入）→ grill-me 拷問拆解 → 補課（`phases/`）→ 使用者從零寫專案 C → `tools/resume_gen.py` 依證據解鎖履歷。

## 誰寫程式（最重要）
- **專案 C（`projects/C-groundwater-bottomup/`）**：Claude 不寫任何程式碼，只拷問、審查、查文件。使用者要求代寫時，提醒這條規則並改成提示或拷問。
- **課程依 `docs/depth-tiers.md` 分級**：
  - A 親手做：不產生該課的 `code/`、`tests/`、`math.md` 內容；只出題、審查、指出錯誤位置，不直接給修正。
  - B Agent 做、使用者驗收：可以寫，但要先請使用者寫出或確認驗收條件，寫完由使用者跑測試並讀懂結果。
  - C 只讀懂：可以直接做，做完用一兩句說明重點。
  - 校準規則照該檔：同類事情 Claude 連續錯兩次 → 升一級；連續三次都對 → 降一級。調整時更新該檔並說明理由。
- 專案 A、B：可以修改，但改動要寫進該專案的 `falsification.md` 或 commit 訊息說明原因。

## 不可以做的事
- 不手動修改 `grill/scores.json`；只有 grill-me 拷問結束時依實際表現寫入。使用者要求灌分時拒絕。
- 不手動修改 `resume/generated/`；那是 `tools/resume_gen.py` 的輸出。
- `docs/ai-falsification-log.md` 的「作者」欄：使用者自己抓到的寫「我」，Claude 抓到或犯的寫「Claude」。履歷只計「我」，不可混淆。
- 不在專案 C 的未解鎖層放 `.py`（`tools/gate.py` 會讓 CI 失敗）。

## 常用指令
```bash
pytest                                  # 全部測試（2026-11-08 為 62 個）
python tools/ship_check.py --run        # 42 堂課出貨狀態
python tools/gate.py                    # 專案 C 關卡
python tools/resume_gen.py --refresh    # 履歷生產表
python tools/gen.py                     # 改 tools/curriculum.py 後重產課程骨架
```
- `pytest.ini` 已有 `addopts = -q`。在子程序中解析「N passed」時要用 `-o addopts=--import-mode=importlib -q`，否則兩個 `-q` 會讓摘要行消失。
- 專案 A 的測試靠 `tests/conftest.py` 加入 `src/`；單獨跑：`PYTHONPATH=src python -m pytest -o addopts= -q tests`。

## 技能
- `grill-me`（`.claude/skills/grill-me/`）：使用者說「grill me <目標>」時使用。目標清單在 `grill/targets.toml`。進場條件：使用者必須先讀懂該目標的程式並親自跑過（說得出指令與實際結果），否則不開始拷問。

## 驗證習慣
- 數值、API 用法、套件預設值都以實跑為準；說法被測試推翻就記到對應的 `falsification.md`。
- 套件 API（FastAPI、pandas、pyproj、k3d 等）以官方文件確認，不憑記憶。

## 已知未實測
Docker 映像建置、Docker Compose、k3d 部署、在使用者 WSL2 上的執行（見 TODO 02–07）。
