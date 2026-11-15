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
| 卡 | 能力 |
|---|---|
| 02、04、10、11 | 物理判斷與數值誤差敏感度（M1） |
| 06、08 | 空間資料、文獻與資料處理 |
| 05 等拷問卡 | 回頭拆解專案 A 的求解器 |
| 12 | 否證 AI 產出（M3） |
| 13 之後 | 自架平台：批次跑情境（M2） |

## 檔案
- `cards.toml`：卡片佇列；`progress.json`、`log.md`：進度與日誌（由 card.py 寫入）
- `cases.py`：情境定義；`runs/`：輸出（不進 git）
- `tools/setup_comcot.sh`：下載並編譯 COMCOT（gfortran 版，中央大學 IHOS 海嘯研究群，github.com/HandsomeAndy/comcot-gfortran）
- `tools/comcot_ctl.py`、`run_case.py`、`plot.py`、`synth_bathy.py`：Claude 寫的工具
- `answers.md`：參考答案，做卡前不要看

## 已知事項（Claude 在 2026-11-15 實測）
- gfortran 13 需要 `-fallow-argument-mismatch` 才編得過（原始 README 標示支援到 gfortran 8.2）。
- 控制檔是固定欄位：第 49 字元為冒號；檔名欄位前不能有空白，否則開檔失敗後程式繼續執行並崩潰（Segmentation fault）。
- 玩具情境 60 分鐘模擬約 3 秒。
