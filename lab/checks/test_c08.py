"""卡 08 驗收：lab/mine/etopo_to_xyz.py"""
import numpy as np
import pytest
from etopo_to_xyz import crop_to_xyz, write_xyz

LON = np.arange(115.0, 125.0 + 1e-9, 1.0)           # 11 個
LAT = np.arange(15.0, 27.0 + 1e-9, 1.0)             # 13 個
Z = np.add.outer(LAT * 10, LON)                      # z[j, i] = 10*lat + lon，方便核對順序


def test_crop_and_order():
    xyz = crop_to_xyz(LON, LAT, Z, bbox=(116, 118, 16, 17))     # x0, x1, y0, y1，含邊界
    assert xyz.shape == (3 * 2, 3)
    # 緯度由小到大排，每個緯度內經度由小到大（和 synth_bathy 一樣）
    assert xyz[0].tolist() == [116, 16, 276]
    assert xyz[2].tolist() == [118, 16, 278]
    assert xyz[3].tolist() == [116, 17, 286]
    assert xyz[-1].tolist() == [118, 17, 288]


def test_descending_latitude_gives_same_result():
    a = crop_to_xyz(LON, LAT, Z, bbox=(116, 118, 16, 17))
    b = crop_to_xyz(LON, LAT[::-1], Z[::-1], bbox=(116, 118, 16, 17))
    assert np.array_equal(a, b)


def test_nan_in_crop_is_rejected():
    z = Z.copy(); z[2, 2] = np.nan                                # (lat 17, lon 117) 在範圍內
    with pytest.raises(ValueError):
        crop_to_xyz(LON, LAT, z, bbox=(116, 118, 16, 18))


def test_nan_outside_crop_is_fine():
    z = Z.copy(); z[0, 0] = np.nan
    assert crop_to_xyz(LON, LAT, z, bbox=(116, 118, 16, 18)).shape[0] == 9


def test_empty_or_outside_bbox_is_rejected():
    with pytest.raises(ValueError):
        crop_to_xyz(LON, LAT, Z, bbox=(200, 210, 16, 17))


def test_write_xyz_format(tmp_path):
    p = tmp_path / "t.xyz"
    write_xyz(p, np.array([[116.0, 16.0, -3000.04], [116.01667, 16.0, 12.0]]))
    assert p.read_text().splitlines() == ["116.00000 16.00000 -3000.0", "116.01667 16.00000 12.0"]
