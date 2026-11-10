# JOBBBBBBB：科學模擬職缺的作品集與訓練場

目標職缺要求三件事串成一條決策鏈：用**物理判斷**設計模擬與驗證，用**自架基礎設施**把它跑起來，用**生成式 AI** 加速並**否證** AI 的產出。這個 repo 用三個專案和一套課程把這條鏈練出來，並把完成的證據自動轉成履歷敘述。

## 路線：速成 → 講解 → 拷問 → 從零重建

```
① 速成       專案 A、B（Claude 寫好、能跑、有測試）
               │
②a 講解      拷問前先由 Claude 逐元件講解：假設你沒有背景，白話＋小數字例子，
               │  順序依拆解地圖；講完一段再進拷問。講解不計分
②b 拷問      grill-me 逐元件追問：做什麼 → 為什麼 → 改了會怎樣 → 不看程式重寫
               │  分數記在 grill/scores.json；暴露的缺口對應到 phases/ 的課程
               │
③ 補課       完成對應課程（推導＋程式＋測試＋否證，四項齊全才算出貨）
               │
④ 從零重建   專案 C 由你自己寫，由下往上 6 層；條件未滿足的層放程式碼，CI 直接失敗
               │
⑤ 履歷       tools/resume_gen.py 依證據解鎖履歷敘述，數字自動帶入
```

| 專案 | 誰寫 | 內容 | 狀態 |
|---|---|---|---|
| [A 淹水模擬服務](projects/A-flood-service) | Claude | 1D 淺水方程 HLL 有限體積求解器、Stoker／Ritter 驗證、FastAPI 非同步工作、SQLite 佇列、Docker Compose | 17 個測試通過 |
| [B 雨量 ETL＋空間](projects/B-rain-etl-spatial) | Claude | 多來源雨量 ETL、TWD97、徐昇式多邊形面積雨量、Prometheus 指標、k8s manifest | 26 個測試通過 |
| [C 地下水污染傳輸服務](projects/C-groundwater-bottomup) | **你** | ADE 求解器 → 反求延散係數 → 監測井 ETL → API → 自架平台 → 架構決策 | 6 層全部鎖定 |

## 常用指令

```bash
conda env create -f environment.yml && conda activate jobprep
pytest                                  # 全部測試（目前 62 個）
python tools/ship_check.py --run        # 42 堂課的出貨狀態
python tools/gate.py                    # 專案 C 每一層解鎖了沒、還缺什麼
python tools/resume_gen.py --refresh    # 履歷生產表 → resume/generated/
```

## 目錄

```
projects/A-flood-service/         速成專案 A（README 有拆解地圖）
projects/B-rain-etl-spatial/      速成專案 B（README 有拆解地圖）
projects/C-groundwater-bottomup/  bottom-up 專案 C（gate.toml 定義關卡）
grill/targets.toml                grill-me 的 14 個拆解目標
grill/scores.json                 拷問分數（只由 grill-me 寫入）
grill/log/                        每場拷問的紀錄
phases/NN-phase/NN-lesson/        42 堂課（問題、推導、程式、測試、否證）
resume/claims.toml                每條履歷敘述的解鎖條件與模板
resume/generated/                 自動產生的履歷生產表與敘述
docs/ai-falsification-log.md      否證紀錄總表（「作者」欄區分你與 Claude）
tools/                            ship_check、gate、resume_gen、課程產生器
```

## 履歷生產表怎麼運作

`resume/claims.toml` 的每一條敘述都有解鎖條件，例如：

- **A1-solver**：grill 目標 `A/conservation-form`、`A/hll-flux`、`A/analytic-and-convergence`、`A/wet-dry` 都 ≥ 2 分，且專案 A 測試全過。解鎖後敘述自動帶入 metrics.json 的 L1 誤差與收斂階。
- **C1-ade**：專案 C 第一層通過。
- **M3-falsification**：課程 00/04、08/03 出貨，且你自己寫的否證紀錄 ≥ 15 筆。

產出 `resume_table.md`（每條的狀態、還缺什麼、面試會被問什麼）、`resume_table.csv`、`bullets_zh.md`、`bullets_en.md`。CI 每次 push 都會重產，並上傳成 Actions 的 artifact。

誠實原則：A、B 是 Claude 寫的，所以只有在你通過拷問後才解鎖，用詞是「建置／驗證」；專案 C 由你從零寫，才用「從零實作」。

## 課程（phases/）

課程形式參考 [AI Engineering from Scratch](https://aiengineeringfromscratch.com/)：編號的 phase／lesson、每堂課固定的學習迴圈、「推導、程式、測試都寫完才算出貨」。在這個 repo 裡，課程是**補課清單**：grill-me 暴露的缺口對應到哪堂課，就去完成那堂；專案 C 的每一層也要求對應課程先出貨。完整目錄見 [CATALOG.md](CATALOG.md)。

已出貨的示範課：01/01 連續方程、01/02 收斂階、04/02 多邊形面積、05/02 時區與時雨量。

## 與其他教材的關係

淹水＋PINN 課程（第三冊）與 PINN 相關教材保留，不再是主線。專案 A 的物理內容與第三冊第 1–6 週重疊；專案 C 的 L1、L2 與第二冊第 12–14 章重疊。

## 前提與限制

- 全部測試只在 Claude 的 Linux 環境跑過，尚未在 WSL2 上執行。
- Docker 映像未建置（工作區連不到 Docker Hub）；k8s manifest 未部署（環境沒有 k3d）。
- 專案 A、B 用合成資料；B 的流域與測站座標為虛構。
- CI 檔未在 GitHub 上實際執行過。
- 尚未選定授權條款。
