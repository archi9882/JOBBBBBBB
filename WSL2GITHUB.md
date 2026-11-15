# 如何將WSL的更新推到github上

在 `~/JOB` 裡執行這三步：

```bash
cd ~/JOB
git status                      # 看改了哪些檔案
git add -A                      # 把所有改動加入暫存
git commit -m "card 06: 一維走時"   # 寫一句說明改了什麼
git push                        # 推上 GitHub
```

**做卡時的 commit 訊息格式**

card 技能規定用 `card <卡號>: <題目>`，例如 `card 01: 第一個海嘯`、`card 06: 一維走時`。

**推送前建議先拉一次**

如果你在別的地方（例如這個對話）也改過 repo，先同步比較不會被拒絕：

```bash
git pull
```

**常見狀況**

- **`git push` 被拒絕（rejected）**：雲端有你本機沒有的新 commit。先執行 `git pull`，再 `git push`。有衝突就把訊息貼給我，不要自己硬解。
- **要求輸入帳號密碼**：你的 `startup.md` 寫 remote 已改成 SSH（`git@github.com:archi9882/JOBBBBBBB.git`）。如果還是跳出密碼，用 `git remote -v` 確認網址開頭是 `git@github.com`，不是 `https://`。
- **`git add -A` 會加到不該加的東西嗎**：`lab/runs/`、`lab/vendor/`、`lab/data/`（COMCOT 輸出和下載資料）都已經在 `.gitignore`，不會被推上去，不用擔心檔案太大。
- **推送後怎麼確認**：到 `https://github.com/archi9882/JOBBBBBBB` 看最新一筆 commit 的訊息和時間。或在終端機執行 `git status`，會顯示 `Your branch is up to date with 'origin/main'`。

**一個好習慣**

每做完一張卡就 commit 並 push 一次。這樣 GitHub 上永遠有最新進度，你之前說希望本機和 GitHub 保持一致，也靠這個做到。
