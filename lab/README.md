# 海嘯實驗室（主線，2026-11-15 起）

一晚一張卡，每張 30 分鐘：**先猜 → 再跑 → 看圖 → 一句收穫**。

在 Claude Code 說「下一張卡」就開始；或自己執行：

```bash
python lab/tools/card.py                         # 各軌的下一張卡與進度
python lab/tools/card.py PINN                    # 只看某一軌的下一張卡（全文）
python lab/tools/card.py 35                      # 指定卡號看全文（跳著做用這個）
python lab/tools/run_case.py toy                 # 跑一個情境（定義在 lab/cases.py）
python lab/tools/card.py done 01 "一句收穫"      # 完成
```

## 兩條平行軌
卡片分成**海嘯**（01–33，COMCOT、空間資料、服務與平台）與 **PINN**（34–45，物理資訊神經網路與神經算子）兩軌，各自獨立推進，一晚還是只做一張。PINN 軌只需要 PyTorch CPU 版與 `lab/tools/wave1d_ref.py` 的解析解，不必等 COMCOT 編譯好，所以兩軌誰先誰後都可以。`done`、`check`、`hint` 本來就吃卡號，跳著做不必改佇列。

## 為什麼改成這樣
原本的流程（先讀程式、再寫說明、再拷問、再補課）每一步都在「準備」，一週下來沒有一個看得到的成果。實驗室反過來：用真正的海嘯模式 COMCOT 跑真實情境，問「如果這樣會怎樣」，需要時才回頭拆解原理。

## 職缺能力在哪裡練到
**實作卡**（粗體）是你自己寫程式，寫在 `lab/mine/`，`python lab/tools/card.py check` 自動驗收，沒過就不能 done。每一張卡都有「先預測」那一欄（不只實作卡），先猜才准跑。

| 卡 | 能力 |
|---|---|
| **06、07、12、14** | 物理判斷與數值誤差敏感度（M1）：走時、後處理、規模換滑移量與線性對非線性、收斂階 |
| **08、10、15**、11 | 空間資料與 ETL：水深格式與真實地形情境、TWD97、潮位站清理、文獻 |
| **17、18** | REST API：202／Location、problem+json、冪等 |
| **19、20、23、24、26、28** | 自架平台：容器、批次排程、容量估算、k3d、監控與故障演練、方法選擇與架構決策紀錄 |
| 16、**21**、**32** | 否證 AI：先預測它的錯，再用你自己的驗收測試抓它；最後整理成案例集 |
| **30** | 混合方法：代理模型與它的外插失效 |
| 34–45 | 波動與水文 × PINN：自動微分殘差、訓練與頻譜偏差、因果權重、公平計時、反問題、FNO 代理與外插、摩擦項、從稀疏測站反求摩擦係數 |
| 33 | 作品集：陌生人照 README 跑起來、10 分鐘簡報 |
| 01 | 讓 COMCOT 跑起來，並看滑移量加倍會怎樣 |
| 05 | COMCOT 的時間步與邊界：先驗算 CFL，再被拷問 |

## 檔案
- `cards.toml`：卡片佇列；`progress.json`、`log.md`：進度與日誌（由 card.py 寫入）
- `cases.py`：情境定義；`runs/`：輸出（不進 git）
- `tools/setup_comcot.sh`：下載並編譯 COMCOT（gfortran 版，中央大學 IHOS 海嘯研究群，github.com/HandsomeAndy/comcot-gfortran）
- `tools/comcot_ctl.py`、`run_case.py`、`plot.py`、`synth_bathy.py`：Claude 寫的工具（海嘯軌）
- `tools/wave1d_ref.py`、`pinn_run.py`、`pinn_vs_fd.py`、`fno_run.py`、`damping_run.py`、`damping_sweep.py`：Claude 寫的工具（PINN 軌）
- `mine/`：你寫的程式；`checks/`：Claude 寫的驗收測試（不在 CI 的 testpaths，不會因為你還沒做到而失敗）；`data/`：下載的資料（不進 git）
- `answers.md`：參考答案，做卡前不要看

## 已知事項（Claude 在 2026-11-15 實測）
- gfortran 13 需要 `-fallow-argument-mismatch` 才編得過（原始 README 標示支援到 gfortran 8.2）。
- 控制檔是固定欄位：第 49 字元為冒號；檔名欄位前不能有空白，否則開檔失敗後程式繼續執行並崩潰（Segmentation fault）。
- 玩具情境 60 分鐘模擬約 3 秒。
- PINN 在 CPU 上的成本（2 核 2.1 GHz 實測，2026-11-17）：一維正問題與反問題每步約 5.3 ms，3000 步約 16 秒；二維淺水（10000 配置點、寬 64 深 5）每步約 221 ms，3000 步要 11 分鐘。**一維的卡在本機都是秒級，GPU 買不到東西；只有二維才需要考慮雲端。**
- `wave1d_ref.py` 的阻尼解析解與跳蛙法互相驗過：r=0 時與無摩擦解析解差 ~5e-16，r=0.5 時跳蛙法以二階收斂（網格加倍、誤差除以 4.00）。
