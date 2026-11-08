import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from convergence import observed_orders


def test_upwind_is_first_order_on_fine_grids():
    _, p = observed_orders([100, 200, 400], "upwind")
    assert 0.9 < p[-1] < 1.1


def test_lax_wendroff_is_second_order_on_fine_grids():
    _, p = observed_orders([100, 200, 400], "lax-wendroff")
    assert 1.9 < p[-1] < 2.1


def test_error_decreases_monotonically():
    e, _ = observed_orders([50, 100, 200, 400], "upwind")
    assert all(e[i + 1] < e[i] for i in range(len(e) - 1))


def test_discontinuity_degrades_upwind_to_half_order():
    # 線性對流的不連續解：一階上風在 L1 只剩約 1/2 階
    _, p = observed_orders([200, 400, 800], "upwind", "square")
    assert 0.45 < p[-1] < 0.55
