# 課程啟動程序

專案位置：WSL 磁碟的 `~/JOB`（不要用 `/mnt/c`，跨檔案系統會變慢）。
Linux 區分大小寫，路徑必須寫 `~/JOB`。

## 1. 開啟 WSL 終端機

從 Windows 任一處進入：

```powershell
# PowerShell：直接進入 Ubuntu 並切到專案目錄
wsl -d Ubuntu --cd ~/JOB
```

或從開始選單開啟「Ubuntu」，再執行：

```bash
# 切換到專案目錄
cd ~/JOB
```

## 2. 用 VS Code 開啟（WSL 遠端模式）

```bash
# 在 ~/JOB 內執行，VS Code 會自動以 WSL 模式開啟
code .
```

確認左下角顯示 `WSL: Ubuntu`。沒有的話，用 `Ctrl+Shift+P` 執行
「WSL: Open Folder in WSL」並選 `~/JOB`。

## 3. 啟動 Claude Code

```bash
# 在 ~/JOB 內執行，會自動讀取專案的 CLAUDE.md 與設定
claude
```

## 4. 開工前檢查

```bash
# 工作樹應為 clean，並與遠端同步
git status
git pull
```

## 5. 收工

```bash
# 查看改動，提交後推送（remote 已改為 SSH）
git status
git add -A
git commit -m "說明本次改動"
git push
```

## 注意事項

- 只開一個 VS Code 視窗（WSL 模式）。關掉舊的 `c:\JOB` 本機視窗，避免混用。
- 不要用 Windows 本機模式開啟 `~/JOB`。
- 用 Windows 檔案總管查看檔案：網址列輸入 `\\wsl$\Ubuntu\home\archi_sung\JOB`。
- COMCOT 需要 `gfortran`：`sudo apt install gfortran`（只需安裝一次）。
- Remote 為 `git@github.com:archi9882/JOBBBBBBB.git`，驗證用 `~/.ssh/id_ed25519`。
