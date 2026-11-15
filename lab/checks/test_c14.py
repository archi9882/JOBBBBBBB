"""卡 14 驗收：lab/mine/convergence.py"""
import math
import numpy as np
import pytest
from convergence import extrapolate, observed_order, richardson_order


def test_observed_order_exact_power_law():
    h = np.array([4.0, 2.0, 1.0, 0.5])
    assert observed_order(h, 3.0 * h ** 2) == pytest.approx(2.0, abs=1e-9)
    assert observed_order(h, 0.7 * h) == pytest.approx(1.0, abs=1e-9)


def test_observed_order_needs_positive_errors():
    with pytest.raises(ValueError):
        observed_order([2.0, 1.0], [0.1, 0.0])                              # 誤差 0 取不了 log


def test_richardson_order_and_extrapolate():
    f0, C, p = 5.0, 0.8, 1.5
    f = lambda h: f0 + C * h ** p
    f1, f2, f3 = f(4.0), f(2.0), f(1.0)                                     # 粗 → 細，r = 2
    assert richardson_order(f1, f2, f3, r=2) == pytest.approx(p, abs=1e-9)
    assert extrapolate(f2, f3, p, r=2) == pytest.approx(f0, abs=1e-9)


def test_not_in_asymptotic_range_is_rejected():
    with pytest.raises(ValueError):
        richardson_order(1.0, 2.0, 1.5)                                     # 先增後減：不是單調收斂，不能硬算階數
    with pytest.raises(ValueError):
        richardson_order(1.0, 1.0, 1.0)                                     # 完全沒變：0/0
