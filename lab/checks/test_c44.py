"""卡 44 驗收：lab/mine/pinn_swe.py 的 residual_damped（加線性摩擦的殘差）。

用一個「已知是解」的衰減駐波檢查殘差 ≈ 0，用錯的 r 檢查殘差不為 0，
並檢查 r 是 tensor 時梯度傳得回去（卡 45 要學它）。

衰減駐波（g = h = 1、c = 1、ω = √(c²k² - r²/4)）：
    η = e^{-rt/2}(cos ωt + r/(2ω) sin ωt) · cos kx
    u = (c²k/ω) e^{-rt/2} sin(ωt) · sin kx / h
手算驗過它同時滿足 η_t + h u_x = 0 與 u_t + g η_x + r u = 0。
"""
import math

import pytest
import torch
import pinn_swe

K = math.pi / 2
G = H = 1.0


class DampedMode(torch.nn.Module):
    """r 給對就是方程的解；給錯就不是。"""

    def __init__(self, r, k=K, g=G, h=H):
        super().__init__()
        self.r, self.k, self.g, self.h = r, k, g, h

    def forward(self, tx):
        t, x = tx[:, :1], tx[:, 1:]
        c2 = self.g * self.h
        om = math.sqrt(c2 * self.k**2 - (self.r / 2) ** 2)
        dec = torch.exp(-self.r * t / 2)
        eta = dec * (torch.cos(om * t) + (self.r / (2 * om)) * torch.sin(om * t)) * torch.cos(self.k * x)
        u = (c2 * self.k / om / self.h) * dec * torch.sin(om * t) * torch.sin(self.k * x)
        return torch.cat([eta, u], 1)


def pts(n=500, seed=0):
    g = torch.Generator().manual_seed(seed)
    return torch.rand(n, 1, generator=g), torch.rand(n, 1, generator=g) * 4 - 2


def test_shapes_and_types():
    t, x = pts(64)
    rm, rp = pinn_swe.residual_damped(pinn_swe.Net(), t, x, 0.5)
    assert rm.shape == (64, 1) and rp.shape == (64, 1), f"形狀是 {rm.shape}、{rp.shape}，要 (64, 1)"
    assert rm.requires_grad and rp.requires_grad, "殘差要還能對網路參數微分（create_graph=True）"


@pytest.mark.parametrize("r", [0.0, 0.5, 2.0])
def test_residual_vanishes_on_exact_solution(r):
    t, x = pts()
    rm, rp = pinn_swe.residual_damped(DampedMode(r), t, x, r)
    assert rm.abs().max() < 1e-4, f"r={r} 的解析解代進去，質量殘差 {rm.abs().max():.2e} 應該接近 0"
    assert rp.abs().max() < 1e-4, f"r={r} 的解析解代進去，動量殘差 {rp.abs().max():.2e} 應該接近 0"


def test_wrong_damping_gives_nonzero_residual():
    """r=0.8 的解拿 r=0 去算，動量方程少了摩擦項，殘差不該是 0。"""
    t, x = pts()
    _, rp = pinn_swe.residual_damped(DampedMode(0.8), t, x, 0.0)
    assert rp.abs().max() > 1e-2, f"r 沒有真的進動量方程？殘差只有 {rp.abs().max():.2e}"


def test_damping_can_be_a_tensor_with_gradient():
    """卡 45 要把 r 當參數學，所以梯度一定要傳得回去。"""
    t, x = pts(128)
    logr = torch.nn.Parameter(torch.tensor(math.log(0.5)))
    rm, rp = pinn_swe.residual_damped(pinn_swe.Net(), t, x, torch.exp(logr))
    (rm.pow(2).mean() + rp.pow(2).mean()).backward()
    assert logr.grad is not None, "r 的梯度是 None：中間用了 float(r) 或 .item() 把梯度切斷了"
    assert torch.isfinite(logr.grad).all() and logr.grad.abs() > 0, f"r 的梯度是 {logr.grad}"


def test_matches_card35_residual_when_r_is_zero():
    """r=0 時應該退回卡 35 的 residual（有寫的話）。"""
    if not hasattr(pinn_swe, "residual"):
        pytest.skip("pinn_swe 沒有卡 35 的 residual")
    t, x = pts(200)
    net = pinn_swe.Net()
    a = pinn_swe.residual_damped(net, t, x, 0.0)
    b = pinn_swe.residual(net, t, x)
    for i, (p, q) in enumerate(zip(a, b)):
        assert torch.allclose(p, q, atol=1e-6), f"r=0 時第 {i} 個殘差和卡 35 的不一致"
