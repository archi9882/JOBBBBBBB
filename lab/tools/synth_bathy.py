"""合成地形（ETOPO 格式：經度 緯度 高程，海為負），給第一張卡用，不需要下載資料。"""
import numpy as np


def write(path, x0=116, x1=124, y0=16, y1=24, res_min=1.0):
    lon = np.arange(x0, x1 + 1e-9, res_min / 60)
    lat = np.arange(y0, y1 + 1e-9, res_min / 60)
    L, A = np.meshgrid(lon, lat)
    z = -3000 + 250 * np.clip(L - 118, 0, None) * np.clip(A - 19, 0, None) / 3   # 往東北變淺
    z = np.where((L > 121) & (L < 122) & (A > 22), 200.0, z)                       # 一座方形的「島」
    with open(path, "w") as f:
        for j in range(len(lat)):
            for i in range(len(lon)):
                f.write(f"{lon[i]:.5f} {lat[j]:.5f} {z[j, i]:.1f}\n")
