"""卡 42：用你在卡 41 寫的 SpectralConv1d 組一個 FNO，學「初始水位 → T 秒後水位」。

    python lab/tools/fno_run.py                # 預設：訓練 200 組、測範圍內與範圍外各 50 組
    python lab/tools/fno_run.py --modes 8      # 改保留的傅立葉模態數
    python lab/tools/fno_run.py --epochs 300

訓練與測試資料用 lab/tools/wave1d_ref.py 的週期解析解產生（不用跳蛙法：窄波在 128 格上，跳蛙法自己就有數值色散）：高斯隆起，
振幅 A∈[0.5,1]、寬度 w∈[0.2,0.4]、中心 x0∈[-0.5,0.5]。
「範圍外」測試：寬度 w∈[0.06,0.12]（更窄、更高頻），其他相同。
FNO 的外框（提升層、4 層頻譜卷積加 1×1 卷積、投影層）是 Claude 寫的；頻譜卷積本身用你的 lab/mine/fno.py。
輸出：lab/runs/fno/compare.png 與誤差表。
"""
import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

LAB = Path(__file__).resolve().parents[1]
MINE = Path(os.environ["MINE_DIR"]) if os.environ.get("MINE_DIR") else LAB / "mine"
sys.path.insert(0, str(MINE))
sys.path.insert(0, str(LAB / "tools"))
from wave1d_ref import exact_periodic, leapfrog, rel_l2  # noqa: E402
from fno import SpectralConv1d  # noqa: E402

NX, T = 128, 1.0
XG = -2 + (np.arange(NX) + 0.5) * 4 / NX          # 格心，和 leapfrog 同一組點


class FNO1d(torch.nn.Module):
    def __init__(self, modes=16, width=32, layers=4):
        super().__init__()
        self.lift = torch.nn.Conv1d(2, width, 1)          # 輸入：η0 與座標 x
        self.spec = torch.nn.ModuleList(SpectralConv1d(width, width, modes) for _ in range(layers))
        self.skip = torch.nn.ModuleList(torch.nn.Conv1d(width, width, 1) for _ in range(layers))
        self.proj = torch.nn.Sequential(torch.nn.Conv1d(width, 64, 1), torch.nn.GELU(), torch.nn.Conv1d(64, 1, 1))

    def forward(self, eta):                                 # eta: (B, N)
        x = torch.linspace(-1, 1, eta.shape[-1]).expand_as(eta)
        z = self.lift(torch.stack([eta, x], 1))
        for k, (s, c) in enumerate(zip(self.spec, self.skip)):
            z = s(z) + c(z)
            if k < len(self.spec) - 1:
                z = torch.nn.functional.gelu(z)
        return self.proj(z)[:, 0]


def dataset(n, rng, wrange):
    X, Y = [], []
    for _ in range(n):
        A, w, x0 = rng.uniform(0.5, 1), rng.uniform(*wrange), rng.uniform(-0.5, 0.5)
        X.append(exact_periodic(0.0, XG, A=A, w=w, x0=x0)[0])
        Y.append(exact_periodic(T, XG, A=A, w=w, x0=x0)[0])
    return torch.tensor(np.array(X), dtype=torch.float32), torch.tensor(np.array(Y), dtype=torch.float32)


def errors(model, X, Y):
    with torch.no_grad():
        P = model(X).numpy()
    return np.array([rel_l2(p, y) for p, y in zip(P, Y.numpy())]), P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", type=int, default=16)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--n-train", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    rng = np.random.default_rng(a.seed)
    Xtr, Ytr = dataset(a.n_train, rng, (0.2, 0.4))
    Xin, Yin = dataset(50, rng, (0.2, 0.4))
    Xout, Yout = dataset(50, rng, (0.06, 0.12))

    model = FNO1d(a.modes)
    opt = torch.optim.Adam(model.parameters(), 1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.epochs)
    t0 = time.time()
    for ep in range(a.epochs):
        perm = torch.randperm(len(Xtr))
        for i in range(0, len(Xtr), 20):
            b = perm[i:i + 20]
            loss = ((model(Xtr[b]) - Ytr[b]) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
        sched.step()
    train_s = time.time() - t0

    e_in, P_in = errors(model, Xin, Yin)
    t0 = time.time()
    e_out, P_out = errors(model, Xout, Yout)
    infer_ms = (time.time() - t0) / len(Xout) * 1000
    t0 = time.time()
    leapfrog(NX, T)
    fd_ms = (time.time() - t0) * 1000

    print(f"模態數 {a.modes}｜訓練 {a.n_train} 組 {a.epochs} 輪，花 {train_s:.0f} 秒")
    print(f"範圍內  w∈[0.20,0.40]：相對 L2 誤差 中位數 {np.median(e_in):.3f}，最差 {e_in.max():.3f}")
    print(f"範圍外  w∈[0.06,0.12]：相對 L2 誤差 中位數 {np.median(e_out):.3f}，最差 {e_out.max():.3f}")
    print(f"每組推論 {infer_ms:.2f} ms；同網格跳蛙法每組 {fd_ms:.2f} ms（{NX} 格，不含訓練成本 {train_s:.0f} 秒）")

    out = LAB / "runs" / "fno"
    out.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = XG
        fig, ax = plt.subplots(1, 2, figsize=(10, 3.5), sharey=True)
        for k, (title, Y, P, e) in enumerate((("範圍內", Yin, P_in, e_in), ("範圍外（更窄）", Yout, P_out, e_out))):
            j = int(np.argmax(e))
            ax[k].plot(x, Y[j].numpy(), "k", label="解析解")
            ax[k].plot(x, P[j], "r--", label="FNO")
            ax[k].set_title(f"{title}：最差的一組，誤差 {e[j]:.2f}")
            ax[k].set_xlabel("x")
        ax[0].set_ylabel("η(T=1)")
        ax[0].legend()
        fig.tight_layout()
        fig.savefig(out / "compare.png", dpi=120)
        print(f"圖：{(out / 'compare.png').relative_to(LAB.parent)}")
    except ImportError:
        print("沒有 matplotlib，略過畫圖")


if __name__ == "__main__":
    main()
