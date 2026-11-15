"""卡 12 驗收：lab/mine/moment.py"""
import math
import pytest
from moment import moment_from_mw, mw_from_moment, slip_for_mw


def test_moment_of_mw9():
    assert moment_from_mw(9.0) == pytest.approx(10 ** 22.6, rel=1e-9)       # N·m


def test_roundtrip():
    for mw in (6.0, 7.7, 8.5, 9.0, 9.2):
        assert mw_from_moment(moment_from_mw(mw)) == pytest.approx(mw, abs=1e-12)


def test_slip_for_mw9_large_fault():
    # 500 km × 150 km、剛性 3e10 Pa：D = M0 / (μ A)
    d = slip_for_mw(9.0, length=500e3, width=150e3)
    assert d == pytest.approx(10 ** 22.6 / (3e10 * 500e3 * 150e3), rel=1e-9)
    assert 17 < d < 18.5


def test_same_area_half_magnitude_unit_ratio():
    r = slip_for_mw(9.0, 400e3, 120e3) / slip_for_mw(8.5, 400e3, 120e3)
    assert r == pytest.approx(10 ** 0.75, rel=1e-9)                          # 規模差 0.5 → 滑移量差 10^0.75


def test_units_guard():
    with pytest.raises(ValueError):
        slip_for_mw(9.0, length=500, width=150)                              # 用了公里卻當公尺：面積太小，直接擋下
