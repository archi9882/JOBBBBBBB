"""畫 COMCOT 輸出：某一時刻的水面與最大水位。用法：python lab/tools/plot.py <run 目錄> [輸出時刻步數]"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load(run):
    run = Path(run)
    x, y = np.loadtxt(run / "layer01_x.dat"), np.loadtxt(run / "layer01_y.dat")
    g = lambda f: np.array((run / f).read_text().split(), float).reshape(len(y), len(x))
    return run, x, y, g


def geo_style(ax, x, y, step=1.0):
    """GMT 風格地圖框：°E/°N 刻度、黑白交替邊框、左下角比例尺。所有地圖圖都用這個。"""
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import FixedLocator, FuncFormatter
    x0, x1, y0, y1 = float(x.min()), float(x.max()), float(y.min()), float(y.max())
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal")
    xt, yt = np.arange(np.ceil(x0), x1 + 1e-9, step), np.arange(np.ceil(y0), y1 + 1e-9, step)
    ax.xaxis.set_major_locator(FixedLocator(xt)); ax.yaxis.set_major_locator(FixedLocator(yt))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):g}°{'E' if v >= 0 else 'W'}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):g}°{'N' if v >= 0 else 'S'}"))
    ax.tick_params(length=0, labelsize=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    wx, wy = 0.012 * (x1 - x0), 0.012 * (y1 - y0)              # 邊框寬度
    for k, a in enumerate(np.arange(x0, x1 - 1e-9, step)):     # 上下邊
        c = "k" if k % 2 == 0 else "w"
        for yy in (y0 - wy, y1):
            ax.add_patch(Rectangle((a, yy), min(step, x1 - a), wy, fc=c, ec="k", lw=0.5, clip_on=False))
    for k, b in enumerate(np.arange(y0, y1 - 1e-9, step)):     # 左右邊
        c = "k" if k % 2 == 0 else "w"
        for xx in (x0 - wx, x1):
            ax.add_patch(Rectangle((xx, b), wx, min(step, y1 - b), fc=c, ec="k", lw=0.5, clip_on=False))
    km = 200.0                                                 # 比例尺（以圖中緯度換算）
    deg = km / (111.19 * np.cos(np.radians((y0 + y1) / 2)))
    bx, by = x0 + 0.04 * (x1 - x0), y0 + 0.05 * (y1 - y0)
    ax.plot([bx, bx + deg], [by, by], "k-", lw=2.5, solid_capstyle="butt")
    ax.text(bx + deg / 2, by + 0.015 * (y1 - y0), f"{km:g} km", ha="center", va="bottom", fontsize=8)


def main(run, step=None):
    run, x, y, g = load(run)
    h = g("layer01.dat")                                   # 水深（陸地為負）
    snaps = sorted(run.glob("z_01_*.dat"))
    snap = run / f"z_01_{int(step):06d}.dat" if step else snaps[len(snaps) // 2]
    z, zmax = g(snap.name), g("zmax_layer01.dat")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
    im0 = ax[0].pcolormesh(x, y, z, cmap="RdBu_r", vmin=-1, vmax=1, shading="auto")
    zm = np.where(h > 0, zmax, np.nan)
    im1 = ax[1].pcolormesh(x, y, zm, cmap="viridis", vmin=0, vmax=np.nanpercentile(zm, 99), shading="auto")
    for a, im, t in ((ax[0], im0, f"water surface {snap.stem} (m)"), (ax[1], im1, "max water level (m)")):
        a.contour(x, y, h, levels=[0], colors="k", linewidths=0.8)
        a.set_title(t); geo_style(a, x, y); fig.colorbar(im, ax=a, shrink=0.85)
    fig.tight_layout()
    out = run / "map.png"
    fig.savefig(out, dpi=110)
    print(f"{out}　最大水位 {np.nanmax(zm):.3f} m")


if __name__ == "__main__":
    main(*sys.argv[1:])
