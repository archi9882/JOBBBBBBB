11.16.2026
以下待辦控制在 30 分鐘內，做完就收工。

**明日待辦（一晚一張卡）**

1. **開工檢查（約 5 分鐘）**
   ```bash
   cd ~/JOB && git status && git pull
   python lab/tools/card.py
   ```
   `git status` 要是乾淨的；`card.py` 要顯示 `0/21 張` 和卡 01。
2. **裝 COMCOT 需要的東西（約 5 分鐘，只做一次）**
   ```bash
   sudo apt install gfortran
   conda activate jobprep    # 若環境還沒建：conda env create -f environment.yml
   bash lab/tools/setup_comcot.sh
   ```
   最後要看到 `OK：…/comcot`。失敗就把錯誤訊息貼給我，今天不用再往下。
3. **做卡 01「第一個海嘯」（約 20 分鐘）**
   - 先寫下預測：波從震源傳到島的西南角要幾分鐘？島的哪一側水位最高？
   - 再執行：`python lab/tools/run_case.py toy`
   - 看 `lab/runs/toy/map.png`，對照預測，寫一句收穫。
   - 收尾：`python lab/tools/card.py done 01 "你的一句話"`，然後 `git add -A && git commit -m "card 01" && git push`。

**今天不用做**
- 卡 06 以後的實作卡：等卡 01–05 做完再說。
- 刪舊專案、改文件：留到週末，想到的記在 `lab/ideas.md` 一行。

**有空再看（非必要）**
- 到 GitHub 的 Actions 頁確認 CI 有沒有跑過。`ci.yml` 還沒在 GitHub 上實際驗證過。

我沒有把它存成檔案，因為你的 `CLAUDE.md` 規定不新增文件。想要的話，我可以改成一行寫進 `lab/ideas.md`，或用另一種形式。