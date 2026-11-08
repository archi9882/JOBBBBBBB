import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from polygon import (signed_area, self_intersections, irregular_polygon, TWD97_OFFSET,
                     SQUARE, L_SHAPE, BOWTIE, FAR)


def test_known_areas():
    assert signed_area(SQUARE) == pytest.approx(4.0)
    assert signed_area(L_SHAPE) == pytest.approx(5.0)
    assert signed_area(FAR) == pytest.approx(10000.0, abs=1e-9)


def test_orientation_sign():
    assert signed_area(SQUARE[::-1]) == pytest.approx(-4.0)


def test_bowtie_detected():
    assert self_intersections(BOWTIE) != []
    assert self_intersections(SQUARE) == [] and self_intersections(L_SHAPE) == []


def test_bowtie_area_is_misleading():
    # 兩個三角形一正一負互相抵銷：面積 0 看起來「合法」，其實多邊形無效
    assert signed_area(BOWTIE) == pytest.approx(0.0)


def test_matches_shapely_and_shapely_flags_invalid():
    shapely = pytest.importorskip("shapely.geometry")
    for poly in (SQUARE, L_SHAPE, FAR):
        assert abs(signed_area(poly)) == pytest.approx(shapely.Polygon(poly).area, rel=1e-9)
    assert not shapely.Polygon(BOWTIE).is_valid


def test_large_coordinates_need_shift():
    loc = irregular_polygon()
    A = signed_area(loc)
    far = loc + TWD97_OFFSET
    assert abs(signed_area(far) - A) < 1e-8            # 減去第一個頂點：誤差約 1e-10 m²
    assert abs(signed_area(far, shift=False) - A) > 1e-6  # 直接算：誤差約 6e-5 m²
