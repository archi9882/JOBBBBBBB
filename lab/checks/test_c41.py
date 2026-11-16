"""卡 41 驗收：lab/mine/fno.py 的 SpectralConv1d（傅立葉神經算子的核心層）。"""
import math

import torch
import fno


def layer(i=2, o=3, m=5, seed=0):
    torch.manual_seed(seed)
    return fno.SpectralConv1d(i, o, m)


def test_weight_shape_and_dtype():
    L = layer()
    assert tuple(L.weight.shape) == (2, 3, 5) and L.weight.is_complex()
    assert any(p is L.weight for p in L.parameters()), "weight 要是 nn.Parameter 才會被訓練"


def test_output_shape():
    y = layer()(torch.randn(4, 2, 64))
    assert y.shape == (4, 3, 64) and not y.is_complex()


def test_matches_definition():
    L = layer()
    x = torch.randn(3, 2, 32)
    X = torch.fft.rfft(x)
    Y = torch.zeros(3, 3, 17, dtype=torch.cfloat)
    Y[:, :, :5] = torch.einsum("bim,iom->bom", X[:, :, :5], L.weight.detach())
    assert torch.allclose(L(x), torch.fft.irfft(Y, n=32), atol=1e-5)


def test_high_modes_are_dropped():
    """只保留前 m 個模態：純高頻輸入（第 10 個模態）的輸出應該是 0。"""
    L = layer(1, 1, 5)
    n = torch.arange(64)
    x = torch.cos(2 * math.pi * 10 * n / 64).reshape(1, 1, 64)
    assert L(x).abs().max() < 1e-5


def test_resolution_invariance():
    """同一個平滑函數在 64 點和 128 點取樣，輸出在共同的點上要一致（FNO 可以換網格推論）。"""
    L = layer(1, 1, 4)
    f = lambda n: (torch.sin(2 * math.pi * torch.arange(n) / n) + 0.5 * torch.cos(4 * math.pi * torch.arange(n) / n)).reshape(1, 1, n)
    y64, y128 = L(f(64)), L(f(128))
    assert torch.allclose(y64[0, 0], y128[0, 0, ::2], atol=1e-5)


def test_gradients_flow():
    L = layer()
    L(torch.randn(2, 2, 16)).pow(2).sum().backward()
    assert L.weight.grad is not None
