11.17.2026
以下待辦控制在 30 分鐘內，做完就收工。

**下次開工（一晚一張卡：卡 35）**

1. **開工檢查（約 3 分鐘）**
   ```bash
   cd ~/JOB && git status && git pull
   conda activate jobprep
   python -c "import torch; print(torch.__version__)"
   python lab/tools/card.py
   ```
   `git status` 要是乾淨的；`torch` 要印出版本（沒有的話：`pip install torch --index-url https://download.pytorch.org/whl/cpu`）；`card.py` 要顯示 `0/34 張`、海嘯 `0/24`、PINN `0/10`。

2. **先寫下預測，寫完才准往下（約 2 分鐘）**

   一個隨機初始化、還沒訓練的網路，把淺水方程的殘差算出來，大概是哪個量級？

   > 我的預測：＿＿＿＿（0.01 / 0.1 / 1 / 10，選一個，並寫一行理由）

   寫在這裡或紙上都可以，重點是**在跑之前定案**。猜錯不扣分。

3. **做卡 35「自動微分殘差」（約 25 分鐘）**

   在 `~/JOB` 裡開 Claude Code，說「做卡 35」最省事：
   ```bash
   claude
   ```
   自己來也可以：
   ```bash
   python lab/tools/card.py 35          # 看全文與 spec
   # 寫 lab/mine/pinn_swe.py：class Net 與 residual()
   python lab/tools/card.py check 35    # 六個驗收測試
   python lab/tools/card.py hint 1 35   # 卡住才看，最多到 3
   ```
   測試全過之後，用一個隨機網路把殘差印出來，對照第 2 步的預測，寫一句收穫。

   收尾：
   ```bash
   python lab/tools/card.py done 35 "你的一句話"
   git add -A && git commit -m "card 35: 自動微分殘差" && git push
   ```

**今天不用做**
- **卡 34（文獻）**：它的預測欄問 Brecht 表 1 的計時和 McGreivy 的弱基準比例，而這兩個答案我已經寫進水文學那份報告裡了。要讀隨時可以讀，但不要再當成預測卡。
- 卡 36 以後：做完一張就停。
- COMCOT 與海嘯軌（卡 01–05）：PINN 軌只需要 PyTorch 和 `lab/tools/wave1d_ref.py` 的解析解，兩軌互不相欠，想先推哪條都行。

**不要做**
- 不要看 `lab/answers.md`。

**有空再看（非必要）**
- 水文學 × PINN 的查證報告：https://claude.ai/artifact/PWN3Ypfwan2grTxCNYdPgs
- 本週後段會用到的卡 44、45（摩擦項、反求摩擦係數）已經寫好，工具與驗收測試都在。
