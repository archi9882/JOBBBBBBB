"""卡 23 驗收：lab/mine/capacity.py"""
import math
import pytest
import capacity


def test_run_bytes_matches_toy_measurement():
    # 玩具情境：241×241、7 個輸出時刻（0–60 分鐘每 10 分鐘）、3 個場、每值約 9.07 位元組
    b = capacity.run_bytes(241, 241, 7, n_fields=3, bytes_per_value=9.07)
    assert b == pytest.approx(241 * 241 * 3 * 7 * 9.07)


def test_run_bytes_default_fields_and_bytes():
    assert capacity.run_bytes(10, 20, 2) == pytest.approx(10 * 20 * 3 * 2 * 9.07)


def test_days_until_full():
    assert capacity.days_until_full(100.0, 4.0) == pytest.approx(25.0)
    assert capacity.days_until_full(100.0, 0) == math.inf


def test_first_bottleneck():
    res = {"disk": (500e9, 20e9), "ram": (16e9, 0), "cpu_hours": (24 * 30, 10)}
    assert capacity.first_bottleneck(res) == "disk"          # 25 天 vs 72 天 vs 永不
    res10 = {"disk": (500e9, 2e9), "cpu_hours": (24 * 30, 100)}
    assert capacity.first_bottleneck(res10) == "cpu_hours"   # 250 天 vs 7.2 天
    assert capacity.first_bottleneck({"ram": (16e9, 0)}) is None
