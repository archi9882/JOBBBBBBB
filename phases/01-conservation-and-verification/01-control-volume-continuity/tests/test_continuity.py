import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from continuity import run


def test_mass_conserved_to_machine_precision():
    r = run()
    assert abs(r["V"] - r["V0"]) / r["V0"] < 1e-12


def test_hump_moves_u_times_t():
    # 上風格式在常速度下，質心每步恰好前進 u·Δt，前提是水丘的尾巴沒有繞過週期邊界。
    # L=10 時擴散後的尾巴會繞回 x≈0，位移少 3e-4 m（見 falsification.md），所以用 L=20、同樣的 Δx。
    r = run(L=20.0, N=400)
    assert abs((r["c"] - r["c0"]) - r["u"] * r["t"]) < 1e-9


def test_wraparound_bias_on_short_domain_is_visible():
    # 反向檢查：L=10 時偏差確實存在，證明上一個測試的前提是必要的
    r = run()
    assert 1e-4 < abs((r["c"] - r["c0"]) - r["u"] * r["t"]) < 1e-3


def test_peak_is_diffused_not_amplified():
    # 單調格式不會產生新的極值
    assert run()["peak"] < 1.5
