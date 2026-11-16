"""一維線性淺水方程的參考解（Claude 寫，PINN 卡 35–45 共用）。

    η_t + h u_x = 0,   u_t + g η_x = 0,   c = √(g h)
初始條件：η0 = A·exp(-((x - x0)/w)²)，u0 = 0。
- exact(t, x, ...)：解析解（d'Alembert 分成左右各半的兩個波），在波碰到邊界前有效。
- exact_periodic(...)：週期邊界版的解析解（卡 42 的訓練與測試資料）。
- leapfrog(...)：交錯網格跳蛙法（和 COMCOT 同一類），週期邊界；當作「強基準」。

加線性摩擦（卡 44–45）：u_t + g η_x = -r u，消去 u 得 η_tt + r η_t = c² η_xx。
- exact_damped_periodic(...)：逐個傅立葉模態的解析解。
- leapfrog_damped(...)：摩擦項半隱式的跳蛙法。
兩者互相驗證過（Claude 於 2026-11-17 實測）：r=0 時 exact_damped_periodic 與
exact_periodic 差 ~5e-16；r=0.5、T=1 時跳蛙法以二階收斂（nx 加倍、誤差除以 4.0）。
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


def exact_damped_periodic(t, x, r=0.0, L=4.0, A=1.0, w=0.3, x0=0.0, g=1.0, h=1.0, nk=4096):
    """加線性摩擦 -r u 的解析解，週期區間 [-L/2, L/2)，回傳 (η, u)。t 是純量，x 可為陣列。

    模態 k 滿足 X'' + r X' + c²k² X = 0，初始 η=η0、η_t(0) = -h u_x(0) = 0：
        η_k(t) = η0_k · e^{-rt/2} · (cos ωt + r/(2ω) · sin ωt),  ω = √(c²k² - r²/4)
        η_k'(t) = -η0_k · e^{-rt/2} · (c²k²/ω) · sin ωt
        u_k(t)  = -η_k'(t) / (i k h)        （k=0 時 u=0）
    ω 在過阻尼模態（r > 2ck）是虛數，一路用複數算到底再取實部。
    """
    c = np.sqrt(g * h)
    xg = -L / 2 + np.arange(nk) * (L / nk)
    e0 = np.fft.rfft(eta0(xg, A, w, x0)) / nk
    k = 2 * np.pi * np.fft.rfftfreq(nk, d=L / nk)
    om = np.lib.scimath.sqrt((c * k) ** 2 - (r / 2) ** 2)
    decay = np.exp(-r * t / 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        f = np.where(om == 0, 1.0 + r * t / 2, np.cos(om * t) + (r / (2 * om)) * np.sin(om * t))
        fp = np.where(om == 0, 0.0, -((c * k) ** 2 / om) * np.sin(om * t))
        eta_k = e0 * decay * f
        u_k = np.where(k == 0, 0.0, -(e0 * decay * fp) / (1j * np.where(k == 0, 1.0, k) * h))
    xq = np.atleast_1d(np.asarray(x, float))
    phase = np.exp(1j * np.outer(xq + L / 2, k))      # rfft 的相位基準是取樣起點 -L/2
    mult = np.where(np.arange(k.size) == 0, 1.0, 2.0)  # 單邊譜補回共軛項
    return (phase * (eta_k * mult)).sum(1).real, (phase * (u_k * mult)).sum(1).real


def leapfrog_damped(nx, T, r=0.0, L=4.0, cr=0.5, A=1.0, w=0.3, x0=0.0, g=1.0, h=1.0):
    """跳蛙法加摩擦項（半隱式，避免 r 大時出現額外的時間步限制）。回傳 (x, η(T), u(T))。"""
    dx = L / nx
    xc = -L / 2 + (np.arange(nx) + 0.5) * dx
    c = np.sqrt(g * h)
    nt = int(np.ceil(T / (cr * dx / c)))
    dt = T / nt
    eta = eta0(xc, A, w, x0)
    u = -0.5 * dt * g * (np.roll(eta, -1) - eta) / dx   # u^0 = 0，第一個半步的摩擦項為 0
    for _ in range(nt):
        eta = eta - dt * h * (u - np.roll(u, 1)) / dx
        u = (u * (1 - 0.5 * r * dt) - dt * g * (np.roll(eta, -1) - eta) / dx) / (1 + 0.5 * r * dt)
    return xc, eta, u


def rel_l2(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))
