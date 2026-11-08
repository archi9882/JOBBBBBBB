"""01/02 網格收斂與觀測收斂階。

對流方程 ∂c/∂t + u ∂c/∂x = 0，週期域 [0,1)，初始 c = sin(2πx)，解析解 c = sin(2π(x − ut))。
比較一階上風（upwind）與二階 Lax–Wendroff，量出觀測收斂階 p。

執行：python code/convergence.py
"""
import numpy as np


def init(x, shape):
    if shape == "sine":
        return np.sin(2 * np.pi * x)
    if shape == "square":                        # 不連續：線性對流下不會變平滑
        return ((x > 0.25) & (x < 0.5)).astype(float)
    raise ValueError(shape)


def solve(N, scheme="upwind", u=1.0, T=0.5, cr=0.5, shape="sine"):
    dx = 1.0 / N
    x = (np.arange(N) + 0.5) * dx
    nsteps = int(round(T / (cr * dx / u)))
    dt = T / nsteps                      # 讓最終時間恰好是 T
    C = u * dt / dx
    c = init(x, shape)
    for _ in range(nsteps):
        cm, cp = np.roll(c, 1), np.roll(c, -1)
        if scheme == "upwind":
            c = c - C * (c - cm)
        elif scheme == "lax-wendroff":
            c = c - 0.5 * C * (cp - cm) + 0.5 * C**2 * (cp - 2 * c + cm)
        else:
            raise ValueError(scheme)
    exact = init((x - u * T) % 1.0, shape)
    return np.abs(c - exact).mean()          # 離散 L1 誤差（格平均）


def observed_orders(Ns, scheme, shape="sine"):
    e = np.array([solve(N, scheme, shape=shape) for N in Ns])
    p = np.log(e[:-1] / e[1:]) / np.log(np.array(Ns[1:]) / np.array(Ns[:-1]))
    return e, p


if __name__ == "__main__":
    Ns = [25, 50, 100, 200, 400]
    for shape in ("sine", "square"):
      for s in ("upwind", "lax-wendroff"):
        e, p = observed_orders(Ns, s, shape)
        print(f"{shape} / {s}")
        print("   N      L1 誤差      p")
        for i, N in enumerate(Ns):
            print(f"  {N:4d}  {e[i]:.3e}  " + ("   —" if i == 0 else f"{p[i-1]:.3f}"))
