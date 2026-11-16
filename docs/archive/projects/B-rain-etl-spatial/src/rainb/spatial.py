"""空間：WGS84 → TWD97（EPSG:3826）、虛構流域、徐昇式多邊形權重、面積雨量。"""
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import Voronoi
from shapely.geometry import Polygon

TO_TWD97 = Transformer.from_crs("EPSG:4326", "EPSG:3826", always_xy=True)   # (經度, 緯度) 順序
TO_WGS84 = Transformer.from_crs("EPSG:3826", "EPSG:4326", always_xy=True)
MIN_COVERAGE = 0.5          # 有資料站的權重和低於此值 → 該小時面積雨量為缺值

# 虛構流域（TWD97 公尺）。S06 刻意落在外面。
BASIN = Polygon([(233000, 2652000), (246000, 2648000), (251000, 2654000),
                 (250000, 2663000), (240000, 2667500), (232000, 2664000)])


def project(stations):
    """{站: (lon, lat)} → {站: (x, y)}，TWD97 公尺。"""
    return {s: TO_TWD97.transform(lon, lat) for s, (lon, lat) in stations.items()}


def roundtrip_error_m(stations):
    """經緯度 → TWD97 → 經緯度 → TWD97，比較兩次投影座標的最大差（公尺）。"""
    worst = 0.0
    for lon, lat in stations.values():
        x, y = TO_TWD97.transform(lon, lat)
        x2, y2 = TO_TWD97.transform(*TO_WGS84.transform(x, y))
        worst = max(worst, float(np.hypot(x2 - x, y2 - y)))
    return worst


def thiessen(xy, basin=BASIN, far=1e6):
    """徐昇式多邊形裁切到流域。

    scipy 的 Voronoi 在外圍站點會產生無界區域（頂點索引 -1）。做法：在流域外 far 公尺
    加 4 個虛擬點，讓所有真實站的區域都有界；再檢查虛擬點的區域沒有碰到流域。
    回傳 {站: 裁切後多邊形}（可能為空）。
    """
    if not basin.is_valid:
        raise ValueError("流域多邊形無效（自相交等），面積權重沒有意義")
    names = list(xy)
    pts = np.array([xy[s] for s in names])
    cx, cy = pts.mean(axis=0)
    dummy = np.array([[cx - far, cy - far], [cx + far, cy - far], [cx + far, cy + far], [cx - far, cy + far]])
    vor = Voronoi(np.vstack([pts, dummy]))
    cells = {}
    for i, s in enumerate(names):
        reg = vor.regions[vor.point_region[i]]
        if -1 in reg or len(reg) == 0:
            raise RuntimeError(f"{s} 的區域仍無界：虛擬點不夠遠")
        cells[s] = Polygon(vor.vertices[reg]).intersection(basin)
    for j in range(len(names), len(names) + 4):
        reg = vor.regions[vor.point_region[j]]
        if -1 not in reg and Polygon(vor.vertices[reg]).intersects(basin):
            raise RuntimeError("虛擬點的區域碰到流域：far 太小")
    return cells


def weights(cells, basin=BASIN):
    """權重＝裁切後面積／流域面積。"""
    return pd.Series({s: c.area / basin.area for s, c in cells.items()}, name="weight")


def areal_rainfall(hourly, w, hours):
    """面積雨量。缺值規則：只用有資料的站，權重重新正規化；
    有資料站的原始權重和（coverage）< MIN_COVERAGE 時該小時為 NaN。"""
    p = hourly.pivot(index="time", columns="station", values="rain_mm").reindex(hours)
    w = w[w > 0]
    p = p.reindex(columns=w.index)
    have = p.notna()
    cov = have.mul(w, axis=1).sum(axis=1)
    val = p.fillna(0).mul(w, axis=1).sum(axis=1) / cov.where(cov > 0)
    val[cov < MIN_COVERAGE] = np.nan
    return pd.DataFrame({"rain_mm": val, "coverage": cov})
