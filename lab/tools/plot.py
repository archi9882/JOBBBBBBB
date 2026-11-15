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
        a.set_title(t); a.set_aspect("equal"); fig.colorbar(im, ax=a, shrink=0.85)
    fig.tight_layout()
    out = run / "map.png"
    fig.savefig(out, dpi=110)
    print(f"{out}　最大水位 {np.nanmax(zm):.3f} m")


if __name__ == "__main__":
    main(*sys.argv[1:])
