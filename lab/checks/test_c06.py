"""卡 06 驗收：lab/mine/wave1d.py"""
import numpy as np
import pytest
from wave1d import cumulative_time, travel_time

G = 9.81


def test_constant_depth():
    h = np.full(1001, 4000.0)                       # 100 km，每格 100 m
    assert travel_time(h, dx=100.0) == pytest.approx(100_000 / np.sqrt(G * 4000), rel=1e-3)


def test_linear_shoaling_matches_integral():
    # h(x) = h0 - s x，解析解：t = 2(√h0 - √h1) / (s √g)
    h0, h1, L = 4000.0, 100.0, 100_000.0
    h = np.linspace(h0, h1, 1001)
    s = (h0 - h1) / L
    expected = 2 * (np.sqrt(h0) - np.sqrt(h1)) / (s * np.sqrt(G))
    assert travel_time(h, dx=L / 1000) == pytest.approx(expected, rel=1e-3)


def test_cumulative_time_shape_and_end():
    h = np.linspace(3000.0, 200.0, 501)
    t = cumulative_time(h, dx=200.0)
    assert t.shape == h.shape and t[0] == 0.0
    assert np.all(np.diff(t) > 0)
    assert t[-1] == pytest.approx(travel_time(h, dx=200.0))


@pytest.mark.parametrize("bad", [0.0, -5.0])
def test_land_or_zero_depth_is_rejected(bad):
    h = np.array([100.0, 50.0, bad, 20.0])
    with pytest.raises(ValueError):
        travel_time(h, dx=100.0)
