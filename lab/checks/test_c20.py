"""卡 20 驗收：lab/mine/batch.py"""
import csv
import threading
import time
import batch


def test_runs_in_parallel_but_bounded_and_keeps_order(tmp_path):
    lock, state = threading.Lock(), {"now": 0, "peak": 0}

    def runner(name):
        with lock:
            state["now"] += 1; state["peak"] = max(state["peak"], state["now"])
        time.sleep(0.2)
        with lock:
            state["now"] -= 1
        return {"max_level": float(len(name))}

    names = ["a", "bb", "ccc", "dddd", "eeeee"]
    out = tmp_path / "r.csv"
    t0 = time.time()
    res = batch.run_batch(names, runner, max_workers=2, out_csv=out)
    dt = time.time() - t0
    assert [r["case"] for r in res] == names
    assert all(r["status"] == "ok" for r in res)
    assert state["peak"] == 2
    assert dt < 0.2 * 5 * 0.8                                               # 真的有並行


def test_one_failure_does_not_stop_the_rest(tmp_path):
    def runner(name):
        if name == "bad":
            raise RuntimeError("segfault")
        return {"max_level": 1.0}

    out = tmp_path / "r.csv"
    res = batch.run_batch(["a", "bad", "c"], runner, max_workers=2, out_csv=out)
    assert [r["status"] for r in res] == ["ok", "failed", "ok"]
    assert "segfault" in res[1]["error"]
    rows = list(csv.DictReader(out.open()))
    assert [r["case"] for r in rows] == ["a", "bad", "c"]
    assert set(rows[0]) >= {"case", "status", "max_level", "seconds", "error"}
    assert rows[1]["max_level"] == ""                                       # 失敗的那列沒有數值，不要填 0
