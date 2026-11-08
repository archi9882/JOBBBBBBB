import numpy as np
import pytest
from floodsvc.solver import dam_break
from floodsvc.analytic import stoker, stoker_middle_state, ritter


def l1(hl, hr, N):
    r = dam_break(hl, hr, N=N, t_end=20.0)
    he, _ = stoker(r.x, r.t, hl, hr, 500.0)
    return np.abs(r.h - he).sum() * (1000.0 / N), r


def test_stoker_middle_state_known_case():
    # h_l=10、h_r=1 的經典案例：中間水深約 3.96 m
    hm, um, S = stoker_middle_state(10.0, 1.0)
    assert hm == pytest.approx(3.9617, abs=1e-3)
    assert S > um > 0


def test_analytic_conserves_mass():
    x = np.linspace(0, 1000, 200001)
    for hr in (1.0, 0.0):
        h, _ = stoker(x, 20.0, 10.0, hr, 500.0)
        h0 = np.where(x < 500, 10.0, hr)
        assert np.trapezoid(h, x) == pytest.approx(np.trapezoid(h0, x), rel=1e-4)


def test_mass_conserved_and_depth_nonnegative():
    for hr in (1.0, 0.0):
        _, r = l1(10.0, hr, 400)
        assert abs(r.mass - r.mass0) / r.mass0 < 1e-12
        assert r.h.min() >= 0.0


def test_converges_to_stoker():
    e = [l1(10.0, 1.0, N)[0] for N in (200, 400, 800)]
    assert e[0] > e[1] > e[2]
    p = np.log2(e[1] / e[2])
    assert 0.6 < p < 1.1          # 激波＋稀疏波：一階格式，實測約 0.8–0.9


def front_lag(N, thr=1e-3):
    r = dam_break(10.0, 0.0, N=N, t_end=20.0)
    he, _ = ritter(r.x, r.t, 10.0, 500.0)
    return r.x[he > thr].max() - r.x[r.h > thr].max()


def test_dry_bed_front_lags_but_converges():
    # 實測：以 h > 1 mm 定義前緣，數值前緣落後 Ritter 解（N=400 約 57 m），隨網格加密緩慢縮小
    lags = [front_lag(N) for N in (400, 800, 1600)]
    assert all(l > 0 for l in lags)            # 落後，不是超前
    assert lags[0] > lags[1] > lags[2]
    assert lags[1] < 60.0


def test_bad_cfl_rejected():
    with pytest.raises(ValueError):
        dam_break(10.0, 1.0, cfl=1.2)
