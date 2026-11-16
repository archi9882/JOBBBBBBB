"""卡 39：公平賽跑。PINN 和跳蛙法在「相同精度」下各要花多少時間？

    python lab/tools/pinn_vs_fd.py           # 用你的 lab/mine/pinn_swe.py
    MINE_DIR=lab/mine_ai python lab/tools/pinn_vs_fd.py   # 卡 43：換成 AI 寫的版本

做法（McGreivy & Hakim 2024 的強基準原則）：
1. 訓練你的 PINN（預設設定），量 t=1 的相對 L2 誤差 e_pinn 與訓練秒數。
2. 找「誤差 ≤ e_pinn 的最粗跳蛙法網格」，量它的秒數（重複 20 次取中位數）。
3. 也列出最細網格（4096 格）的秒數，看看拿弱基準比會得出什麼「結論」。
"""
import os
import statistics
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import torch

LAB = Path(__file__).resolve().parents[1]
MINE = Path(os.environ["MINE_DIR"]) if os.environ.get("MINE_DIR") else LAB / "mine"
sys.path.insert(0, str(MINE))
sys.path.insert(0, str(LAB / "tools"))
from wave1d_ref import exact, leapfrog, rel_l2  # noqa: E402
import pinn_swe  # noqa: E402

warnings.filterwarnings("ignore", category=UserWarning)


def timed(f, n=20):
    ts = []
    for _ in range(n):
        t0 = time.perf_counter()
        r = f()
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts), r


def main():
    t0 = time.perf_counter()
    net, _ = pinn_swe.train()
    train_s = time.perf_counter() - t0
    x = np.linspace(-2, 2, 801)
    q = torch.tensor(np.c_[np.ones_like(x), x], dtype=torch.float32)
    infer_s, out = timed(lambda: net(q).detach().numpy(), 50)
    e_pinn = rel_l2(out[:, 0], exact(1.0, x)[0])

    print(f"PINN：t=1 誤差 {e_pinn:.4f}｜訓練 {train_s:.1f} 秒｜推論 801 點 {infer_s * 1e3:.2f} ms")
    print("\n跳蛙法（週期、Cr=0.5）：")
    print("  格數   誤差      秒數")
    match, fine = None, None
    for nx in (16, 32, 64, 128, 256, 512, 1024, 2048, 4096):
        s, (xg, e) = timed(lambda: leapfrog(nx, 1.0), 20 if nx <= 1024 else 3)
        err = rel_l2(e, exact(1.0, xg)[0])
        mark = ""
        if match is None and err <= e_pinn:
            match, mark = (nx, s, err), "  ← 相同精度的最粗網格"
        print(f"  {nx:5d}  {err:.4f}  {s:.5f}{mark}")
        fine = s
    if match:
        nx, s, err = match
        print(f"\n同精度：跳蛙法 {nx} 格 {s * 1e3:.2f} ms，PINN 訓練 {train_s:.1f} 秒 → 跳蛙法快 {train_s / s:,.0f} 倍")
        print(f"只比推論：PINN {infer_s * 1e3:.2f} ms 對跳蛙法 {s * 1e3:.2f} ms")
    print(f"弱基準的說法（只比推論、拿 4096 格當對手）：「PINN 快 {fine / infer_s:,.0f} 倍」——這句話錯在哪？")
    print("提醒：PINN 換一個初始條件就要重新訓練；跳蛙法不用。")


if __name__ == "__main__":
    main()
