"""卡 45：用你寫的 fit_damping 掃描「觀測類型 × 雜訊」，對照 Radfar 的結論。

    python lab/tools/damping_sweep.py              # 9 組設定，CPU 上約 3–4 分鐘
    python lab/tools/damping_sweep.py --quick      # 3 組，約 1 分鐘
    python lab/tools/damping_sweep.py --steps 1500 # 想更快就少訓練幾步（會變不準）

真值 r = 0.5，兩個測站 x = 0.5、1.0，初猜 r = 0.1。
Radfar（arXiv 2606.18149）反求 Manning n 的對照數字：
    只給水深 95.7%、只給流速 61.9%、兩者一起給 14.5%（2D 斜槽、20 個觀測點、無雜訊）
輸出：lab/runs/damping/sweep.md
"""
import argparse
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
MINE = Path(os.environ["MINE_DIR"]) if os.environ.get("MINE_DIR") else LAB / "mine"
sys.path.insert(0, str(MINE))
sys.path.insert(0, str(LAB / "tools"))
from wave1d_ref import exact_damped_periodic  # noqa: E402
import pinn_inverse  # noqa: E402

warnings.filterwarnings("ignore", category=UserWarning)

R_TRUE = 0.5
RADFAR = {"只給 η": "95.7%", "只給 u": "61.9%", "η 與 u": "14.5%"}


def gauges(n_per=20, noise=0.0, seed=0, stations=(0.5, 1.0)):
    t = np.tile(np.linspace(0.05, 1.0, n_per), len(stations))
    x = np.repeat(stations, n_per)
    eta = np.empty_like(t)
    u = np.empty_like(t)
    for i, (ti, xi) in enumerate(zip(t, x)):
        e, uu = exact_damped_periodic(ti, [xi], r=R_TRUE, nk=1024)
        eta[i], u[i] = e[0], uu[0]
    if noise:
        rng = np.random.default_rng(seed)
        eta = eta + rng.normal(0, noise * eta.std(), eta.size)
        u = u + rng.normal(0, noise * u.std(), u.size)
    return t, x, eta, u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="只跑無雜訊的三種觀測類型")
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--n-per", type=int, default=20, help="每個測站的觀測筆數")
    a = ap.parse_args()

    noises = [0.0] if a.quick else [0.0, 0.02, 0.10]
    kinds = ["η 與 u", "只給 η", "只給 u"]
    rows = []
    print(f"真值 r = {R_TRUE}，初猜 0.1，每站 {a.n_per} 筆，{a.steps} 步\n")
    print(f"{'觀測類型':<10}{'雜訊':>7}{'反求 r':>11}{'相對誤差':>11}{'秒':>7}")
    for kind in kinds:
        for noise in noises:
            t, x, eta, u = gauges(n_per=a.n_per, noise=noise)
            kw = {"r_init": 0.1, "steps": a.steps}
            if kind in ("η 與 u", "只給 η"):
                kw["eta_obs"] = eta
            if kind in ("η 與 u", "只給 u"):
                kw["u_obs"] = u
            t0 = time.perf_counter()
            r = pinn_inverse.fit_damping(t, x, **kw)
            dt = time.perf_counter() - t0
            err = abs(r - R_TRUE) / R_TRUE
            rows.append((kind, noise, r, err, dt))
            print(f"{kind:<10}{noise:>7.0%}{r:>11.4f}{err:>10.1%}{dt:>7.1f}")

    out = LAB / "runs" / "damping"
    out.mkdir(parents=True, exist_ok=True)
    p = out / "sweep.md"
    with p.open("w", encoding="utf-8") as f:
        f.write(f"# 反求摩擦係數：觀測類型 × 雜訊\n\n真值 r = {R_TRUE}，初猜 0.1，"
                f"每站 {a.n_per} 筆，{a.steps} 步。\n\n")
        f.write("| 觀測類型 | 雜訊 | 反求 r | 相對誤差 | Radfar 的 Manning n |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for kind, noise, r, err, _ in rows:
            ref = RADFAR[kind] if noise == 0.0 else ""
            f.write(f"| {kind} | {noise:.0%} | {r:.4f} | {err:.1%} | {ref} |\n")
        f.write("\nRadfar（arXiv 2606.18149）的對照是 2D 斜槽、反求 Manning n、20 個觀測點、無雜訊。\n")
        f.write("\n## 一句話收穫\n\n（在這裡寫：你的結果和 Radfar 差在哪、為什麼差）\n")
    print(f"\n表：{p}")
    print(f"總時間 {sum(r[4] for r in rows) / 60:.1f} 分鐘")
    print("\n對照 Radfar 的 Manning n：只給水深 95.7%、只給流速 61.9%、兩者 14.5%")


if __name__ == "__main__":
    main()
