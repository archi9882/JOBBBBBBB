"""卡 15 驗收：lab/mine/tide_etl.py"""
import pandas as pd
import pytest
from tide_etl import clean_tide


def messy():
    rows = [
        ("A", "2026-01-01 08:00", 120),
        ("A", "2026-01-01 09:00", -999),      # 缺測哨兵值
        ("A", "2026-01-01 10:00", 130),
        ("A", "2026-01-01 10:00", 130),       # 完全重複
        ("B", "2026-01-01 08:00", 100),
        ("B", "2026-01-01 08:00", 105),       # 同站同時刻、數值衝突
        ("A", "2026-01-01 11:00", 5000),      # 超出物理範圍（±1000 cm）
    ]
    return pd.DataFrame(rows, columns=["station", "time", "level_cm"])


def test_clean_rows_and_timezone():
    clean, rejected = clean_tide(messy(), tz="Asia/Taipei")
    assert len(clean) == 2
    assert str(clean["time"].dt.tz) == "UTC"
    assert clean["time"].tolist() == [pd.Timestamp("2026-01-01 00:00", tz="UTC"), pd.Timestamp("2026-01-01 02:00", tz="UTC")]
    assert clean["level_cm"].tolist() == [120, 130]
    assert clean["time"].is_monotonic_increasing


def test_rejected_has_reasons_and_nothing_is_lost():
    clean, rejected = clean_tide(messy(), tz="Asia/Taipei")
    reasons = rejected["reason"].value_counts().to_dict()
    assert reasons == {"sentinel": 1, "duplicate_conflict": 2, "out_of_range": 1}
    assert len(clean) + len(rejected) + 1 == 7                               # +1：完全重複的那一列被合併掉
    assert set(rejected.columns) >= {"station", "time", "level_cm", "reason"}


def test_input_not_mutated():
    df = messy(); before = df.copy()
    clean_tide(df, tz="Asia/Taipei")
    pd.testing.assert_frame_equal(df, before)
