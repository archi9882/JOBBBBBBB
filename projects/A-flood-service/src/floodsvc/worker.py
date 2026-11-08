"""Worker：從佇列取工作 → 跑求解器 → 與解析解比較 → 寫回結果。

執行：python -m floodsvc.worker（環境變數 FLOODSVC_DB 指定資料庫路徑）
"""
import os
import time
import numpy as np
from . import jobs
from .solver import dam_break
from .analytic import stoker

DB = os.environ.get("FLOODSVC_DB", "floodsvc.db")


def simulate(p):
    r = dam_break(p["h_left"], p["h_right"], L=p["length"], x0=p["length"] / 2, N=p["cells"], t_end=p["t_end"])
    he, ue = stoker(r.x, r.t, p["h_left"], p["h_right"], p["length"] / 2)
    dx = p["length"] / p["cells"]
    step = max(1, p["cells"] // 200)                       # 回傳的剖面最多約 200 點
    return {
        "t": r.t, "steps": r.steps,
        "mass_rel_error": abs(r.mass - r.mass0) / r.mass0,
        "l1_error_vs_analytic_m2": float(np.abs(r.h - he).sum() * dx),
        "min_depth": float(r.h.min()),
        "profile": {"x": r.x[::step].round(3).tolist(), "h": r.h[::step].round(5).tolist(),
                    "h_exact": he[::step].round(5).tolist()},
    }


def run_once(con):
    """處理一筆工作；佇列空的時候回傳 False。"""
    got = jobs.claim(con)
    if got is None:
        return False
    jid, params = got
    try:
        jobs.finish(con, jid, simulate(params))
    except Exception as e:                                  # 求解失敗要記錄，不能讓工作卡在 running
        jobs.fail(con, jid, f"{type(e).__name__}: {e}")
    return True


def main(poll=1.0):
    con = jobs.connect(DB)
    back, dead = jobs.requeue_stale(con)
    print(f"worker 啟動：重排 {back} 筆、判失敗 {dead} 筆", flush=True)
    while True:
        if not run_once(con):
            time.sleep(poll)


if __name__ == "__main__":
    main()
