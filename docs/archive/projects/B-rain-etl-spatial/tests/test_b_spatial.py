import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rainb import synth, spatial

XY = spatial.project(synth.STATIONS)


def test_roundtrip_below_1mm():
    assert spatial.roundtrip_error_m(synth.STATIONS) < 1e-3


def test_axis_order_matters():
    # always_xy=True：輸入 (經度, 緯度)。台灣 TWD97 東距約 15–35 萬 m、北距約 240–280 萬 m
    x, y = XY["S01"]
    assert 150_000 < x < 350_000 and 2_400_000 < y < 2_800_000


def test_basin_valid_and_contains_inner_stations():
    from shapely.geometry import Point
    assert spatial.BASIN.is_valid
    inside = {s for s, p in XY.items() if spatial.BASIN.contains(Point(p))}
    assert inside == {"S01", "S02", "S03", "S04", "S05"}


def test_weights_sum_to_one_and_cells_clipped():
    cells = spatial.thiessen(XY)
    w = spatial.weights(cells)
    assert abs(w.sum() - 1) < 1e-9
    assert all(c.within(spatial.BASIN.buffer(1e-6)) for c in cells.values() if not c.is_empty)
    assert (w > 0).sum() >= 4


def test_symmetric_case_matches_hand_calculation():
    square = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    xy = {"L": (0.5, 1.0), "R": (1.5, 1.0)}          # 中垂線 x=1，各占一半
    w = spatial.weights(spatial.thiessen(xy, basin=square), basin=square)
    assert w["L"] == pytest.approx(0.5) and w["R"] == pytest.approx(0.5)


def test_invalid_basin_rejected():
    bow = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    with pytest.raises(ValueError):
        spatial.thiessen({"A": (0.2, 0.5), "B": (0.8, 0.5)}, basin=bow)


def test_far_too_small_detected():
    with pytest.raises(RuntimeError):
        spatial.thiessen(XY, far=100.0)


def test_missing_station_renormalized_and_low_coverage_nan():
    w = pd.Series({"A": 0.6, "B": 0.4})
    hours = pd.date_range("2026-06-01 01:00", periods=2, freq="1h", tz=synth.TZ)
    hourly = pd.DataFrame({"station": ["A", "B", "B"], "time": [hours[0], hours[0], hours[1]],
                           "rain_mm": [10.0, 20.0, 5.0]})
    ar = spatial.areal_rainfall(hourly, w, hours)
    assert ar.rain_mm.iloc[0] == pytest.approx(0.6 * 10 + 0.4 * 20)
    assert ar.coverage.iloc[1] == pytest.approx(0.4) and np.isnan(ar.rain_mm.iloc[1])   # 0.4 < 0.5
