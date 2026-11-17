"""卡 36、38：用你寫的 train() 做實驗，量 PINN 的誤差怎麼隨時間長大。

    python lab/tools/pinn_run.py                         # 預設 w=0.3、T=1
    python lab/tools/pinn_run.py --w 0.05 --T 1.5        # 窄波、時間拉長（卡 38 前半）
    python lab/tools/pinn_run.py --w 0.05 --T 1.5 --causal-eps 1   # 加因果權重（卡 38）

對照的真值是 lab/tools/wave1d_ref.py 的解析解。輸出：lab/runs/pinn/<標籤>.png 與誤差表。
"""
import argparse
import os
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
from wave1d_ref import exact, rel_l2  # noqa: E402
import pinn_swe  # noqa: E402

warnings.filterwarnings("ignore", category=UserWarning)


def predict(net, t, x):
    with torch.no_grad():
        o = net(torch.tensor(np.c_[np.full_like(x, t), x], dtype=torch.float32)).numpy()
    return o[:, 0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=float, default=0.3)
    ap.add_argument("--T", type=float, default=1.0)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--causal-eps", type=float, default=None)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    kw = dict(steps=a.steps, w=a.w, T=a.T, seed=a.seed)
    if a.causal_eps is not None:
        kw["causal_eps"] = a.causal_eps
    t0 = time.time()
    net, hist = pinn_swe.train(**kw)
    secs = time.time() - t0

    x = np.linspace(-2, 2, 1601)
    ts = np.linspace(0, a.T, 7)
    errs = [rel_l2(predict(net, t, x), exact(t, x, w=a.w)[0]) for t in ts]
    tag = f"w{a.w}_T{a.T}" + (f"_causal{a.causal_eps}" if a.causal_eps is not None else "")
    print(f"{tag}｜訓練 {a.steps} 步，花 {secs:.0f} 秒，最後損失 {hist[-1]:.2e}")
    print("t      " + "  ".join(f"{t:5.2f}" for t in ts))
    print("誤差   " + "  ".join(f"{e:5.3f}" for e in errs))

    out = LAB / "runs" / "pinn"
    out.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 3, figsize=(13, 3.5))
        ax[0].semilogy(hist)
        ax[0].set_title("訓練損失")
        ax[0].set_xlabel("步數")
        ax[1].plot(ts, errs, "o-")
        ax[1].set_title("相對 L2 誤差 vs 時間")
        ax[1].set_xlabel("t")
        ax[1].set_ylim(bottom=0)
        ax[2].plot(x, exact(a.T, x, w=a.w)[0], "k", label="解析解")
        ax[2].plot(x, predict(net, a.T, x), "r--", label="PINN")
        ax[2].set_title(f"t = {a.T} 的水位")
        ax[2].legend()
        fig.suptitle(tag)
        fig.tight_layout()
        fig.savefig(out / f"{tag}.png", dpi=110)
        print(f"圖：{(out / f'{tag}.png').relative_to(LAB.parent)}")
    except ImportError:
        print("沒有 matplotlib，略過畫圖")


if __name__ == "__main__":
    main()
