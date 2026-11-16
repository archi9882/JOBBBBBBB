"""卡 40 驗收：lab/mine/pinn_inverse.py 的 fit_depth()。
資料：真實水深 h=0.64（c=0.8），兩個測站 x=0.5、1.0 的水位時序（t∈[0,1] 各 100 點），初始條件已知。
每個測試要訓練一次，CPU 上各約 20–60 秒。"""
import sys
from pathlib import Path

import numpy as np
import pinn_inverse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from wave1d_ref import exact  # noqa: E402

H_TRUE = 0.64


def gauges(noise=0.0, seed=0):
    t = np.tile(np.linspace(0, 1, 100), 2)
    x = np.repeat([0.5, 1.0], 100)
    eta = exact(t, x, h=H_TRUE)[0]
    if noise:
        eta = eta + np.random.default_rng(seed).normal(0, noise, eta.size)
    return t, x, eta


def test_recovers_depth_clean():
    h = pinn_inverse.fit_depth(*gauges(), h_init=1.0)
    assert isinstance(h, float)
    assert abs(h - H_TRUE) / H_TRUE < 0.05, f"反求的水深 {h:.3f}，真值 {H_TRUE}"


def test_recovers_depth_noisy_from_far_guess():
    h = pinn_inverse.fit_depth(*gauges(noise=0.02), h_init=0.3)
    assert abs(h - H_TRUE) / H_TRUE < 0.05, f"有雜訊、初猜 0.3 時反求 {h:.3f}，真值 {H_TRUE}"
