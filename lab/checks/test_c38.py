"""卡 38 驗收：lab/mine/pinn_swe.py 的 causal_weights() 與 train(causal_eps=...)。
因果權重（Wang, Sankaran & Perdikaris 2024）：把時間切成幾段，第 i 段的權重 = exp(-ε · 前面各段損失的總和)。"""
import math

import numpy as np
import torch
import pinn_swe


def test_first_chunk_weight_is_one():
    w = pinn_swe.causal_weights(torch.tensor([0.3, 0.2, 0.1]), eps=5.0)
    assert float(w[0]) == 1.0


def test_formula():
    L = torch.tensor([0.1, 0.2, 0.3, 0.4])
    w = pinn_swe.causal_weights(L, eps=2.0)
    expect = [1.0, math.exp(-0.2), math.exp(-0.6), math.exp(-1.2)]
    assert np.allclose(w.detach().numpy(), expect, atol=1e-6)


def test_zero_eps_means_uniform():
    w = pinn_swe.causal_weights(torch.tensor([5.0, 1.0, 2.0]), eps=0.0)
    assert np.allclose(w.detach().numpy(), 1.0)


def test_weights_carry_no_gradient():
    """權重只用來「排順序」：梯度不該穿過權重流回前面時段的損失。"""
    L = torch.tensor([0.5, 0.5, 0.5], requires_grad=True)
    w = pinn_swe.causal_weights(L, eps=1.0)
    assert not w.requires_grad


def test_monotone_nonincreasing():
    w = pinn_swe.causal_weights(torch.rand(16) + 0.01, eps=3.0).detach().numpy()
    assert np.all(np.diff(w) <= 1e-7)


def test_train_accepts_causal_eps():
    net, hist = pinn_swe.train(steps=50, causal_eps=1.0, seed=0)
    assert len(hist) == 50 and all(np.isfinite(hist))
