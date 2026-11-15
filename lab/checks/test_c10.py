"""卡 10 驗收：lab/mine/twd97.py"""
import numpy as np
import pytest
from twd97 import distance_m, from_twd97, to_twd97


def haversine(lon1, lat1, lon2, lat2, R=6_371_008.8):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def test_central_meridian_false_easting():
    x, _ = to_twd97(121.0, 23.5)
    assert x == pytest.approx(250_000.0, abs=0.01)      # TWD97 TM2：中央經線 121°E，假東距 250000 m


def test_lon_lat_order_not_swapped():
    x, y = to_twd97(121.5, 25.0)                         # 台北附近
    assert 295_000 < x < 305_000 and 2_740_000 < y < 2_800_000


def test_roundtrip():
    lon, lat = from_twd97(*to_twd97(120.3, 22.6))
    assert lon == pytest.approx(120.3, abs=1e-8) and lat == pytest.approx(22.6, abs=1e-8)


@pytest.mark.parametrize("p,q", [((121.0, 23.0), (121.0, 24.0)),
                                 ((121.0, 23.0), (122.0, 23.0)),
                                 ((120.3, 22.6), (119.5, 20.0))])
def test_distance_close_to_great_circle(p, q):
    assert distance_m(p, q) == pytest.approx(haversine(*p, *q), rel=0.005)
