# 海嘯實驗室（主線，2026-11-15 起）

一晚一張卡，每張 30 分鐘：**先猜 → 再跑 → 看圖 → 一句收穫**。

在 Claude Code 說「下一張卡」就開始；或自己執行：

```bash
python lab/tools/card.py                         # 下一張卡與進度
python lab/tools/run_case.py toy                 # 跑一個情境（定義在 lab/cases.py）
python lab/tools/card.py done 01 "一句收穫"      # 完成
```

## 為什麼改成這樣
原本的流程（先讀程式、再寫說明、再拷問、再補課）每一步都在「準備」，一週下來沒有一個看得到的成果。實驗室反過來：用真正的海嘯模式 COMCOT 跑真實情境，問「如果這樣會怎樣」，需要時才回頭拆解原理。

## 職缺能力在哪裡練到
**實作卡**（粗體）是你自己寫程式，寫在 `lab/mine/`，`python lab/tools/card.py check` 自動驗收，沒過就不能 done。

| 卡 | 能力 |
|---|---|
| **06、07、14**、02、04、12、13 | 物理判斷與數值誤差敏感度（M1）：走時、後處理、收斂階、線性對非線性 |
| **08、10、15**、11 | 空間資料與 ETL：水深格式、TWD97、潮位站清理、文獻 |
| **17、18** | REST API：202／Location、problem+json、冪等 |
| **19、20** | 自架平台：容器、批次排程 |
| 16、**21** | 否證 AI：先預測它的錯，再用你自己的驗收測試抓它 |
| 05 | 回頭拆解專案 A 的求解器（拷問） |

## 檔案
- `cards.toml`：卡片佇列；`progress.json`、`log.md`：進度與日誌（由 card.py 寫入）
- `cases.py`：情境定義；`runs/`：輸出（不進 git）
- `tools/setup_comcot.sh`：下載並編譯 COMCOT（gfortran 版，中央大學 IHOS 海嘯研究群，github.com/HandsomeAndy/comcot-gfortran）
- `tools/comcot_ctl.py`、`run_case.py`、`plot.py`、`synth_bathy.py`：Claude 寫的工具
- `mine/`：你寫的程式；`checks/`：Claude 寫的驗收測試（不在 CI 的 testpaths，不會因為你還沒做到而失敗）；`data/`：下載的資料（不進 git）
- `answers.md`：參考答案，做卡前不要看

## 已知事項（Claude 在 2026-11-15 實測）
- gfortran 13 需要 `-fallow-argument-mismatch` 才編得過（原始 README 標示支援到 gfortran 8.2）。
- 控制檔是固定欄位：第 49 字元為冒號；檔名欄位前不能有空白，否則開檔失敗後程式繼續執行並崩潰（Segmentation fault）。
- 玩具情境 60 分鐘模擬約 3 秒。
