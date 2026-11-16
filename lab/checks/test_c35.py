"""卡 35 驗收：lab/mine/pinn_swe.py 的 Net 與 residual（自動微分殘差）。
用「已知是解」的小網路檢查殘差 ≈ 0，用「錯的波速」檢查殘差不為 0。"""
import math

import pytest
import torch
import pinn_swe


class Wave(torch.nn.Module):
    """η = f(x - c t)、u = (c/h) f(x - c t)，f 是高斯。c 給對就是線性淺水方程的解。"""

    def __init__(self, c, h):
        super().__init__()
        self.c, self.h = c, h

    def forward(self, tx):
        t, x = tx[:, :1], tx[:, 1:]
        f = torch.exp(-((x - self.c * t) / 0.3) ** 2)
        return torch.cat([f, self.c / self.h * f], 1)


def pts(n=500, seed=0):
    g = torch.Generator().manual_seed(seed)
    return torch.rand(n, 1, generator=g), torch.rand(n, 1, generator=g) * 4 - 2


def test_net_maps_tx_to_eta_u():
    net = pinn_swe.Net(width=16, depth=2)
    out = net(torch.zeros(7, 2))
    assert out.shape == (7, 2), "Net 的輸入是 (N, 2) 的 [t, x]，輸出是 (N, 2) 的 [η, u]"


def test_residual_zero_for_exact_wave():
    t, x = pts()
    rm, rp = pinn_swe.residual(Wave(1.0, 1.0), t, x)
    assert rm.shape[0] == 500 and rp.shape[0] == 500
    assert rm.abs().max() < 1e-5 and rp.abs().max() < 1e-5, "真解代進去，兩條方程的殘差都應該約等於 0"


def test_residual_uses_g_and_h():
    g, h = 9.81, 4.0
    t, x = pts(seed=1)
    rm, rp = pinn_swe.residual(Wave(math.sqrt(g * h), h), t, x, g=g, h=h)
    assert rm.abs().max() < 1e-3 and rp.abs().max() < 1e-3, "c = √(g h) 的波在 g=9.81、h=4 也該是真解"


def test_residual_nonzero_for_wrong_speed():
    t, x = pts(seed=2)
    rm, rp = pinn_swe.residual(Wave(0.5, 1.0), t, x)
    assert rm.abs().max() > 0.1 or rp.abs().max() > 0.1, "波速錯了，殘差不該是 0"


def test_residual_accepts_tensor_depth_and_keeps_graph():
    """卡 40 的反問題會把 h 當成要學的參數，所以 h 可以是 tensor，而且梯度要傳得回去。"""
    t, x = pts(100, seed=3)
    h = torch.tensor(1.0, requires_grad=True)
    rm, rp = pinn_swe.residual(Wave(1.0, 1.0), t, x, h=h + 0.0)
    (rm ** 2 + rp ** 2).mean().backward()
    assert h.grad is not None


def test_inputs_without_requires_grad_are_fine():
    t, x = pts(10)
    assert not t.requires_grad and not x.requires_grad
    pinn_swe.residual(Wave(1.0, 1.0), t, x)          # 不該丟例外
