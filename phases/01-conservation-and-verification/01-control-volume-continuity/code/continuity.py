"""01/01 控制體積與連續方程：用進出流量更新水深，檢查總水量守恆。

執行：python code/continuity.py
"""
import numpy as np


def setup(L=10.0, N=200, u=1.0, cr=0.5):
    dx = L / N
    x = (np.arange(N) + 0.5) * dx            # 控制體積中心
    h = 1.0 + 0.5 * np.exp(-((x - 3.0) / 0.5) ** 2)   # 1 m 底水＋水丘
    dt = cr * dx / u
    return x, h, dx, dt


def step(h, u, dx, dt):
    """一步上風有限體積更新（u > 0，週期邊界）。
    q_out：每格右側面流出；q_in：左鄰格右側面流進（= 本格左側面）。"""
    q_out = u * h
    q_in = np.roll(q_out, 1)
    return h - dt / dx * (q_out - q_in)


def center(x, h, base=1.0):
    """水丘（扣掉底水）的質心位置。"""
    w = h - base
    return (x * w).sum() / w.sum()


def run(nsteps=200, **kw):
    u = kw.get("u", 1.0)
    x, h, dx, dt = setup(**kw)
    V0, c0 = h.sum() * dx, center(x, h)
    for _ in range(nsteps):
        h = step(h, u, dx, dt)
    return dict(t=nsteps * dt, V0=V0, V=h.sum() * dx, c0=c0, c=center(x, h),
                peak=h.max(), u=u)


if __name__ == "__main__":
    r = run()
    print(f"t = {r['t']:.2f} s")
    print(f"總水量 初始 {r['V0']:.12f}  最終 {r['V']:.12f}  相對誤差 {abs(r['V']-r['V0'])/r['V0']:.1e}")
    print(f"水丘峰值 初始 1.500 m  最終 {r['peak']:.3f} m（數值擴散，02/02 與 01/02 解釋）")
    print(f"水丘中心 {r['c0']:.3f} → {r['c']:.3f} m；位移 {r['c']-r['c0']:.6f} m，理論 u·t = {r['u']*r['t']:.6f} m")
