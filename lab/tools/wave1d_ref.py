"""一維線性淺水方程的參考解（Claude 寫，PINN 卡 35–43 共用）。

    η_t + h u_x = 0,   u_t + g η_x = 0,   c = √(g h)
初始條件：η0 = A·exp(-((x - x0)/w)²)，u0 = 0。
- exact(t, x, ...)：解析解（d'Alembert 分成左右各半的兩個波），在波碰到邊界前有效。
- exact_periodic(...)：週期邊界版的解析解（卡 42 的訓練與測試資料）。
- leapfrog(...)：交錯網格跳蛙法（和 COMCOT 同一類），週期邊界；當作「強基準」。
"""
import numpy as np


def eta0(x, A=1.0, w=0.3, x0=0.0):
    return A * np.exp(-(((np.asarray(x, float) - x0) / w) ** 2))


def exact(t, x, A=1.0, w=0.3, x0=0.0, g=1.0, h=1.0):
    """回傳 (η, u)。t、x 可廣播。"""
    c = np.sqrt(g * h)
    t, x = np.asarray(t, float), np.asarray(x, float)
    fr, fl = eta0(x - c * t, A, w, x0), eta0(x + c * t, A, w, x0)
    return 0.5 * (fr + fl), 0.5 * (c / h) * (fr - fl)


def exact_periodic(t, x, L=4.0, **kw):
    """週期區間 [-L/2, L/2) 上的解析解：把左右鄰近的映像加起來（波繞出邊界會從另一邊回來）。"""
    eta = sum(exact(t, np.asarray(x, float) + k * L, **kw)[0] for k in (-2, -1, 0, 1, 2))
    u = sum(exact(t, np.asarray(x, float) + k * L, **kw)[1] for k in (-2, -1, 0, 1, 2))
    return eta, u


def leapfrog(nx, T, L=4.0, cr=0.5, A=1.0, w=0.3, x0=0.0, g=1.0, h=1.0, eta_init=None):
    """週期區間 [-L/2, L/2)，nx 格。η 在格心、u 在格面（錯開半格），u 也錯開半個時間步。
    回傳 (x, η(T))。eta_init 可直接給格心上的初始 η（卡 42 產資料用）。"""
    dx = L / nx
    x = -L / 2 + (np.arange(nx) + 0.5) * dx
    c = np.sqrt(g * h)
    nt = int(np.ceil(T / (cr * dx / c)))
    dt = T / nt
    eta = eta0(x, A, w, x0) if eta_init is None else np.array(eta_init, float)
    u = np.zeros(nx)                      # u[i] 在 x[i] + dx/2，時間 n - 1/2
    # 第一個半步：u 從 0 推到 dt/2（初始 u=0，用 η 梯度推半步，保持二階）
    u -= 0.5 * dt * g * (np.roll(eta, -1) - eta) / dx
    for _ in range(nt):
        eta -= dt * h * (u - np.roll(u, 1)) / dx
        u -= dt * g * (np.roll(eta, -1) - eta) / dx
    return x, eta


def rel_l2(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))
