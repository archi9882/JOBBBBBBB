import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rainb import synth, etl

TZ = synth.TZ


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    d = tmp_path_factory.mktemp("b_etl")
    a, b = synth.write_sources(d / "raw")
    merged, rep, sha = etl.run(a, b, d / "clean", list(synth.STATIONS), synth.HOURS)
    return dict(d=d, a=a, b=b, merged=merged, rep=rep, sha=sha)


def test_clean_equals_truth(out):
    m = out["merged"].set_index(["station", "time"]).rain_mm
    truth = synth.truth_hourly()
    assert (m - truth.reindex(m.index)).abs().max() < 1e-9


def test_only_expected_hours_missing(out):
    m = out["merged"]
    got = set(zip(m.station, m.time))
    missing = {(s, t.strftime("%H:%M")) for s, t in set(synth.truth_hourly().index) - got}
    # S02 10:00（哨兵、無 B）、S03 16:00（非數字、無 B）、S06 07:00（B 為 null）
    assert missing == {("S02", "10:00"), ("S03", "16:00"), ("S06", "07:00")}


def test_rejection_reasons(out):
    reasons = sorted(r[3] for r in out["rep"].rejected)
    assert reasons == sorted(["sentinel_missing", "sentinel_missing", "not_a_number",
                              "out_of_physical_range", "time_without_timezone", "null_value"])


def test_sentinel_not_summed_and_b_fills_gap(out):
    m = out["merged"].set_index(["station", "time"])
    row = m.loc[("S04", pd.Timestamp("2026-06-01 13:00", tz=TZ))]   # A 在 12:20 為 -999
    assert row.source == "B"
    assert row.rain_mm == synth.truth_hourly()[("S04", pd.Timestamp("2026-06-01 13:00", tz=TZ))]


def test_duplicates_counted_and_dropped(out):
    assert out["rep"].duplicates == {"S01": 2}


def test_utc_is_converted_not_relabelled(out):
    # 來源 A 的第一筆是 UTC 16:10（前一天），應落在台灣時間 01:00 那一小時
    first = out["merged"].query("station == 'S01'").time.min()
    assert first == pd.Timestamp("2026-06-01 01:00", tz=TZ)


def test_resample_closed_right():
    ends = pd.date_range("2026-06-01 14:10", periods=6, freq="10min", tz=TZ)
    a = pd.DataFrame({"station": "X", "end": ends, "rain_mm": 1.0})
    h = etl.hourly_from_a(a)
    assert list(h.time) == [pd.Timestamp("2026-06-01 15:00", tz=TZ)] and h.rain_mm.iloc[0] == 6.0
    assert h.n.iloc[0] == 6


def test_naive_time_rejected():
    assert etl.parse_time("2026-06-01T10:00:00") is None
    assert etl.parse_time("2026-06-01T10:00:00Z") is not None


def test_idempotent(out, tmp_path):
    _, _, sha2 = etl.run(out["a"], out["b"], tmp_path / "again", list(synth.STATIONS), synth.HOURS)
    _, _, sha3 = etl.run(out["a"], out["b"], tmp_path / "again", list(synth.STATIONS), synth.HOURS)
    assert out["sha"] == sha2 == sha3


def test_quality_report(out):
    q = pd.read_csv(out["d"] / "clean" / "quality.csv").set_index("station")
    assert q.loc["S01", "duplicates"] == 2
    assert q.loc["S02", "missing_rate"] == pytest.approx(1 / 24, abs=1e-4)
    assert q.loc["S01", "missing_rate"] == 0
