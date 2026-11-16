"""卡 44：線性摩擦的參考曲線。

    python lab/tools/damping_run.py

做兩件事：
1. 畫 t=1 的最大水位對 r 的曲線——卡 44 的預測就是在猜這條曲線的形狀。
2. 把解析解用中央差分代回方程，確認 lab/tools 的參考解和卡 44 的方程式一致
   （這是對工具本身的檢查；你寫的 residual_damped 由 lab/checks/test_c44.py 驗收）。

輸出：lab/runs/damping/amplitude_vs_r.png
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
from wave1d_ref import exact_damped_periodic  # noqa: E402

T = 1.0
L = 4.0
G = H = 1.0


def amplitude_curve():
    rs = np.concatenate([np.linspace(0, 6, 61), np.linspace(6.5, 30, 48)])
    xq = np.linspace(-L / 2, L / 2, 401, endpoint=False)
    amps = np.array([np.abs(exact_damped_periodic(T, xq, r=r, g=G, h=H, nk=1024)[0]).max() for r in rs])
    i = int(amps.argmin())
    c = np.sqrt(G * H)
    r_crit = 2 * c * (2 * np.pi / L)        # 最低模態的臨界阻尼 2ck
    print(f"最大水位最小值：r = {rs[i]:.2f} 時 max|η(1)| = {amps[i]:.4f}")
    print(f"最低模態（k = 2π/L = {2 * np.pi / L:.3f}）的臨界阻尼 2ck = {r_crit:.3f}")
    print(f"r = 0 時 {amps[0]:.4f}　｜　r = 30 時 {amps[-1]:.4f}")

    out = LAB / "runs" / "damping"
    out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(rs, amps, lw=2)
    ax.plot(rs[i], amps[i], "o", ms=8, label=f"min at r={rs[i]:.2f}")
    ax.axvline(r_crit, ls="--", c="gray", label=f"2ck={r_crit:.2f} (lowest mode)")
    ax.set_xlabel("damping r")
    ax.set_ylabel(f"max|eta| at t={T}")
    ax.set_title("more friction does not mean a smaller wave")
    ax.legend()
    fig.tight_layout()
    p = out / "amplitude_vs_r.png"
    fig.savefig(p, dpi=130)
    print(f"\n圖：{p}")


def verify_reference(r=0.5):
    """解析解代回方程（中央差分），質量與動量殘差都該接近 0。"""
    nx, nt = 401, 401
    xs = np.linspace(-L / 2, L / 2, nx, endpoint=False)
    ts = np.linspace(0.2, 0.8, nt)
    E = np.empty((nt, nx))
    U = np.empty((nt, nx))
    for i, tt in enumerate(ts):
        E[i], U[i] = exact_damped_periodic(tt, xs, r=r, g=G, h=H, nk=1024)
    dt, dx = ts[1] - ts[0], xs[1] - xs[0]
    Et = (E[2:] - E[:-2]) / (2 * dt)
    Ut = (U[2:] - U[:-2]) / (2 * dt)
    Ux = (np.roll(U, -1, 1) - np.roll(U, 1, 1))[1:-1] / (2 * dx)
    Ex = (np.roll(E, -1, 1) - np.roll(E, 1, 1))[1:-1] / (2 * dx)
    scale = max(np.abs(Et).max(), np.abs(Ut).max())
    m = np.abs(Et + H * Ux).max() / scale
    p = np.abs(Ut + G * Ex + r * U[1:-1]).max() / scale
    print(f"\n參考解自檢（r={r}）：質量殘差 {m:.2e}、動量殘差 {p:.2e}（相對於導數量級）")


if __name__ == "__main__":
    amplitude_curve()
    verify_reference()
