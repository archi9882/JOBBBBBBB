"""跑驗證案例與測試，寫出 metrics.json（履歷生產表讀這個檔）。

執行：python projects/A-flood-service/metrics.py
"""
import datetime, json, re, subprocess, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from floodsvc.solver import dam_break
from floodsvc.analytic import stoker

def l1(N):
    r = dam_break(10.0, 1.0, N=N, t_end=20.0)
    he, _ = stoker(r.x, r.t, 10.0, 1.0, 500.0)
    return float(np.abs(r.h - he).sum() * 1000.0 / N), r

e = {N: l1(N) for N in (200, 400, 800)}
r400 = e[400][1]
dry = dam_break(10.0, 0.0, N=400, t_end=20.0)
t = subprocess.run([sys.executable, "-m", "pytest", "-o", "addopts=--import-mode=importlib", "-q",
                    "-p", "no:cacheprovider", str(HERE / "tests")],
                   capture_output=True, text=True)
m = re.search(r"(\d+) passed", t.stdout)
e2e = json.loads((HERE / "e2e.json").read_text()) if (HERE / "e2e.json").exists() else {}
out = {"project": "A", "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "metrics": {
           "stoker_l1_error_m2": round(e[400][0], 3),
           "observed_order": round(float(np.log2(e[400][0] / e[800][0])), 3),
           "mass_rel_error": float(abs(r400.mass - r400.mass0) / r400.mass0),
           "min_depth_dry_bed": float(dry.h.min()),
           "tests_passed": int(m.group(1)) if m else 0,
           "tests_failed": t.returncode != 0,
           "e2e_ok": bool(e2e.get("ok")),
           "e2e_mode": e2e.get("mode", "none"),
       }}
(HERE / "metrics.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(json.dumps(out, ensure_ascii=False, indent=2))
