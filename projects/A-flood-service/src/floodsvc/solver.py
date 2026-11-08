"""1D 淺水方程（Saint-Venant，無摩擦、平底）有限體積求解器。

守恆形式：U = [h, hu]，F(U) = [hu, hu² + g h²/2]
通量：HLL 近似 Riemann 解；時間：前進 Euler，每步依 CFL 重算 Δt。
邊界：兩端透射（零梯度）。乾床：h < H_DRY 時速度設為 0，水深截為非負。
"""
from dataclasses import dataclass
import numpy as np

G = 9.81
H_DRY = 1e-8


@dataclass
class Result:
    x: np.ndarray
    h: np.ndarray
    u: np.ndarray
    t: float
    steps: int
    mass0: float
    mass: float


def _velocity(h, hu):
    return np.where(h > H_DRY, hu / np.maximum(h, H_DRY), 0.0)


def _flux(h, hu):
    u = _velocity(h, hu)
    return np.stack([hu, hu * u + 0.5 * G * h * h])


def hll_flux(hL, huL, hR, huR):
    """每個介面的 HLL 通量。波速估計採 Einfeldt/Davis 型：取左右特徵速度的極值。"""
    uL, uR = _velocity(hL, huL), _velocity(hR, huR)
    cL, cR = np.sqrt(G * hL), np.sqrt(G * hR)
    SL = np.minimum(uL - cL, uR - cR)
    SR = np.maximum(uL + cL, uR + cR)
    FL, FR = _flux(hL, huL), _flux(hR, huR)
    UL, UR = np.stack([hL, huL]), np.stack([hR, huR])
    denom = np.where(SR - SL > 1e-14, SR - SL, 1e-14)
    Fhll = (SR * FL - SL * FR + SL * SR * (UR - UL)) / denom
    return np.where(SL >= 0, FL, np.where(SR <= 0, FR, Fhll))


def dam_break(h_left, h_right, L=1000.0, x0=500.0, N=400, t_end=20.0, cfl=0.9):
    if not 0 < cfl <= 1:
        raise ValueError("CFL 必須在 (0, 1]")
    dx = L / N
    x = (np.arange(N) + 0.5) * dx
    h = np.where(x < x0, h_left, h_right).astype(float)
    hu = np.zeros(N)
    mass0 = h.sum() * dx
    t, steps = 0.0, 0
    while t < t_end - 1e-12:
        u = _velocity(h, hu)
        smax = np.max(np.abs(u) + np.sqrt(G * h))
        dt = min(cfl * dx / smax, t_end - t)
        # 透射邊界：各補一個與邊界格相同的虛擬格
        hg = np.concatenate([[h[0]], h, [h[-1]]])
        hug = np.concatenate([[hu[0]], hu, [hu[-1]]])
        F = hll_flux(hg[:-1], hug[:-1], hg[1:], hug[1:])      # N+1 個介面
        h = h - dt / dx * (F[0, 1:] - F[0, :-1])
        hu = hu - dt / dx * (F[1, 1:] - F[1, :-1])
        dry = h < H_DRY
        h = np.where(dry, np.maximum(h, 0.0), h)
        hu = np.where(dry, 0.0, hu)
        t += dt
        steps += 1
    return Result(x, h, _velocity(h, hu), t, steps, mass0, h.sum() * dx)
