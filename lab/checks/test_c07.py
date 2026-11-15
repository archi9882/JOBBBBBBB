"""卡 07 驗收：lab/mine/zmax.py（用迷你的假輸出目錄測，不需要 COMCOT）"""
import numpy as np
import pytest
from zmax import max_over_snapshots, shoreline_max


def make_run(tmp_path, h, snaps):
    ny, nx = h.shape
    np.savetxt(tmp_path / "layer01_x.dat", np.arange(nx, dtype=float))
    np.savetxt(tmp_path / "layer01_y.dat", np.arange(ny, dtype=float))
    (tmp_path / "layer01.dat").write_text(" ".join(map(str, h.ravel())))
    for k, z in enumerate(snaps, start=1):
        (tmp_path / f"z_01_{k:06d}.dat").write_text(" ".join(map(str, z.ravel())))
    return tmp_path


H = np.array([[100, 100, 100, -5, -5],
              [100, 100, 100, -5, -5],
              [100, 100, 100, 100, -5]], float)   # 海為正、陸地為負


def test_max_over_snapshots(tmp_path):
    a = np.zeros(H.shape); a[0, 0] = 1.0; a[1, 1] = 0.5
    b = np.zeros(H.shape); b[1, 1] = 2.0; b[2, 4] = 9.0
    c = np.full(H.shape, -0.2)
    run = make_run(tmp_path, H, [a, b, c])
    zm = max_over_snapshots(run)
    assert zm.shape == H.shape
    assert zm[0, 0] == 1.0 and zm[1, 1] == 2.0 and zm[2, 4] == 9.0
    assert zm[2, 0] == pytest.approx(0.0)           # 0 大於 -0.2：要真的取最大值，不是平均或最後一張


def test_shoreline_max_only_looks_at_sea_cells_next_to_land():
    zmax = np.zeros(H.shape)
    zmax[0, 0] = 50.0        # 海，但離陸地遠 → 不算
    zmax[1, 2] = 3.0         # 海，右邊鄰陸地 → 算
    zmax[1, 4] = 99.0        # 陸地 → 不算
    zmax[2, 3] = 4.5         # 海，右邊與上方鄰陸地 → 算
    value, (j, i) = shoreline_max(H, zmax)
    assert value == 4.5 and (j, i) == (2, 3)


def test_shoreline_max_no_coast_raises():
    with pytest.raises(ValueError):
        shoreline_max(np.full((3, 3), 100.0), np.ones((3, 3)))
