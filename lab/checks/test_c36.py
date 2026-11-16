"""卡 36 驗收：lab/mine/pinn_swe.py 的 train()。真值是 lab/tools/wave1d_ref.py 的解析解。
這張卡的測試要訓練一次 PINN，CPU 上大約 20–60 秒。"""
import sys
import time
from pathlib import Path

import numpy as np
import pytest
import torch
import pinn_swe

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from wave1d_ref import exact, rel_l2  # noqa: E402


def predict(net, t, x):
    with torch.no_grad():
        return net(torch.tensor(np.c_[np.full_like(x, t), x], dtype=torch.float32)).numpy()


@pytest.fixture(scope="module")
def trained():
    t0 = time.time()
    net, hist = pinn_swe.train(seed=0)
    return net, hist, time.time() - t0


def test_returns_net_and_history(trained):
    net, hist, _ = trained
    assert isinstance(net, torch.nn.Module)
    assert len(hist) > 100 and all(np.isfinite(hist)), "hist 是每一步的損失（有限的數字）"
    assert hist[-1] < 0.1 * hist[0], "損失至少要下降 10 倍"


def test_matches_initial_condition(trained):
    net = trained[0]
    x = np.linspace(-2, 2, 401)
    o = predict(net, 0.0, x)
    assert rel_l2(o[:, 0], exact(0.0, x)[0]) < 0.05, "t=0 的 η 要接近初始高斯"
    assert np.abs(o[:, 1]).max() < 0.05, "t=0 的 u 要接近 0"


def test_accurate_at_final_time(trained):
    net = trained[0]
    x = np.linspace(-2, 2, 401)
    e = rel_l2(predict(net, 1.0, x)[:, 0], exact(1.0, x)[0])
    assert e < 0.08, f"t=1 的相對 L2 誤差 {e:.3f} 應小於 0.08（兩個各一半高的波要分開到 x=±1）"


def test_reasonable_runtime(trained):
    assert trained[2] < 300, f"預設設定訓練花了 {trained[2]:.0f} 秒；30 分鐘的卡片，請讓它在 5 分鐘內跑完"
