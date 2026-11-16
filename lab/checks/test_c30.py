"""卡 30 驗收：lab/mine/surrogate.py（用合成資料；不需要 COMCOT）"""
import numpy as np
import surrogate


def synth(n, seed=1, mw=(8.0, 8.8)):
    rng = np.random.default_rng(seed)
    m = rng.uniform(*mw, n)
    strike = rng.uniform(340, 360, n)
    slip = 10 ** (1.5 * m - 12.0)                       # 示意：滑移隨規模指數成長
    y = 0.5 * slip * (1 + 0.01 * (strike - 350)) + rng.normal(0, 0.02, n)
    return np.c_[slip, strike], y


def test_fit_returns_self_and_predict_shapes():
    X, y = synth(30)
    s = surrogate.Surrogate()
    assert s.fit(X, y) is s
    yh, ok = s.predict(X[:5])
    assert yh.shape == (5,) and ok.shape == (5,) and ok.dtype == bool and ok.all()


def test_holdout_error_is_small():
    X, y = synth(40)
    err = surrogate.Surrogate().holdout_error(X, y, frac=0.2, seed=0)
    assert 0 <= err < 0.10, f"測試集相對誤差 {err:.3f} 應小於 0.10"


def test_holdout_is_reproducible():
    X, y = synth(40)
    s = surrogate.Surrogate()
    assert s.holdout_error(X, y, seed=3) == s.holdout_error(X, y, seed=3)


def test_flags_extrapolation():
    X, y = synth(30)
    s = surrogate.Surrogate().fit(X, y)
    far = X[:2].copy()
    far[0, 0] = X[:, 0].max() * 3                      # 滑移量遠超訓練範圍
    far[1, 1] = X[:, 1].min() - 5                      # 走向低於訓練範圍
    _, ok = s.predict(far)
    assert not ok.any()
