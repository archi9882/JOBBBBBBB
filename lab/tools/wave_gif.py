"""把 COMCOT 的水面快照串成 gif，並標出島周圍的測站。
用法：python lab/tools/wave_gif.py <run 目錄>   輸出 <run>/wave.gif"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
sys.path.insert(0, str(Path(__file__).parent))
from plot import load, geo_style

STATIONS = {"W": (120.9, 23.0), "SW": (120.9, 21.9), "S": (121.5, 21.9), "SE": (122.1, 21.9), "E": (122.1, 23.0)}


def main(run):
    run, x, y, g = load(run)
    h = g("layer01.dat")
    t = np.loadtxt(run / "time.dat")                       # 每個時間步的秒數
    snaps = sorted(run.glob("z_01_*.dat"))
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    im = ax.pcolormesh(x, y, g(snaps[0].name), cmap="RdBu_r", vmin=-1, vmax=1, shading="auto")
    ax.contour(x, y, h, levels=[0], colors="k", linewidths=0.8)
    for name, (lo, la) in STATIONS.items():
        ax.plot(lo, la, "k^", ms=6)
        ax.annotate(name, (lo, la), textcoords="offset points", xytext=(5, 4), fontsize=9)
    geo_style(ax, x, y); fig.colorbar(im, ax=ax, shrink=0.85, label="water surface (m)")
    title = ax.set_title("")

    def update(i):
        im.set_array(g(snaps[i].name).ravel())
        sec = t[int(snaps[i].stem.split("_")[-1])]
        title.set_text(f"t = {sec/60:.0f} min")
        return im, title

    out = run / "wave.gif"
    FuncAnimation(fig, update, frames=len(snaps)).save(out, writer=PillowWriter(fps=2), dpi=90)
    print(out, f"{len(snaps)} 幀")


if __name__ == "__main__":
    main(sys.argv[1])
