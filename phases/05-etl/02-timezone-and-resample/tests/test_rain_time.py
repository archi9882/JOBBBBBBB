import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from rain_time import source_a, source_b, to_hourly_end, naive_hourly, TZ


def test_storm_lands_in_hour_ending_15():
    h = to_hourly_end(source_a())
    assert h.loc[pd.Timestamp("2026-06-01 15:00", tz=TZ)] == 6.0
    assert h.sum() == 6.0


def test_two_sources_agree_after_alignment():
    a, b = to_hourly_end(source_a()), source_b()
    both = pd.concat({"A": a, "B": b}, axis=1, sort=True).fillna(0.0)
    assert (both["A"] == both["B"]).all()


def test_default_resample_splits_and_shifts_the_storm():
    n = naive_hourly(source_a())
    assert n.loc[pd.Timestamp("2026-06-01 14:00", tz=TZ)] == 5.0   # 錯一小時
    assert n.loc[pd.Timestamp("2026-06-01 15:00", tz=TZ)] == 1.0   # 最後 10 分鐘被切到下一格


def test_naive_timestamps_rejected():
    with pytest.raises(ValueError):
        to_hourly_end(source_a().tz_localize(None))


def test_utc_mistaken_for_local_shifts_8_hours():
    wrong = to_hourly_end(source_a().tz_localize(None).tz_localize(TZ))
    assert wrong.loc[lambda x: x > 0].index[0] == pd.Timestamp("2026-06-01 07:00", tz=TZ)
