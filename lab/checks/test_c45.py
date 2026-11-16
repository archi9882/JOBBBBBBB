"""卡 45 驗收：lab/mine/pinn_inverse.py 的 fit_damping()。
真值 r = 0.5，兩個測站 x = 0.5、1.0 各 20 筆（t ∈ [0.05, 1]），初猜 r = 0.1。
每個測試要訓練一次，CPU 上各約 20–40 秒。

門檻訂在 15%：Claude 於 2026-11-17 用參考實作實測，乾淨資料下
只給 η 是 5.7%、η 與 u 都給是 3.8%（都偏低估），15% 留了足夠的餘裕。
"""
import sys
from pathlib import Path

import numpy as np
import pinn_inverse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from wave1d_ref import exact_damped_periodic  # noqa: E402

R_TRUE = 0.5


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


def test_recovers_damping_from_eta_only():
    """只給水位。這是卡 45 的主問題：Radfar 說只給水深反求不出 Manning n。"""
    t, x, eta, _ = gauges()
    r = pinn_inverse.fit_damping(t, x, eta_obs=eta, r_init=0.1)
    assert isinstance(r, float), f"要回傳 float，拿到 {type(r)}"
    assert r > 0, f"摩擦係數要是正的，拿到 {r}"
    assert abs(r - R_TRUE) / R_TRUE < 0.15, f"只給 η 反求 {r:.4f}，真值 {R_TRUE}"


def test_recovers_damping_from_eta_and_u():
    t, x, eta, u = gauges()
    r = pinn_inverse.fit_damping(t, x, eta_obs=eta, u_obs=u, r_init=0.1)
    assert abs(r - R_TRUE) / R_TRUE < 0.15, f"η 與 u 都給時反求 {r:.4f}，真值 {R_TRUE}"


def test_accepts_u_only_without_crashing():
    """只給流速也要跑得完（準不準由 damping_sweep.py 回答，這裡只驗介面）。"""
    t, x, _, u = gauges(n_per=5)
    r = pinn_inverse.fit_damping(t, x, u_obs=u, r_init=0.1, steps=300)
    assert isinstance(r, float) and r > 0 and np.isfinite(r), f"只給 u 時回傳 {r}"
