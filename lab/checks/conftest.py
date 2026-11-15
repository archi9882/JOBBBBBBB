"""驗收測試的共用設定：讓測試找得到你寫的程式（lab/mine/）。
這些測試不在 pytest.ini 的 testpaths 內，所以不會讓 CI 在你還沒做到那張卡時失敗。
用法：python lab/tools/card.py check（MINE_DIR=lab/mine_ai 可改測別的目錄）"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MINE = (ROOT / os.environ["MINE_DIR"]) if os.environ.get("MINE_DIR") else ROOT / "lab" / "mine"
sys.path.insert(0, str(MINE))
