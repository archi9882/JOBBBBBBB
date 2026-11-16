"""跑完整流程並寫出 metrics.json（履歷生產表讀這個檔）。

執行：python projects/B-rain-etl-spatial/metrics.py
"""
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from rainb import synth, etl, spatial  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        a, b = synth.write_sources(d / "raw")
        merged, rep, sha1 = etl.run(a, b, d / "run1", list(synth.STATIONS), synth.HOURS)
        _, _, sha2 = etl.run(a, b, d / "run2", list(synth.STATIONS), synth.HOURS)
    w = spatial.weights(spatial.thiessen(spatial.project(synth.STATIONS)))
    r = subprocess.run([sys.executable, "-m", "pytest", "-o", "addopts=", "-q", "-p", "no:cacheprovider",
                        "--import-mode=importlib", str(HERE / "tests")],
                       capture_output=True, text=True, cwd=HERE.parents[1])
    m = re.search(r"(\d+) passed", r.stdout)
    out = {"project": "B", "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "metrics": {
               "n_sources": 2,
               "n_stations": len(synth.STATIONS),
               "n_records": int(len(merged)),
               "n_rejected": len(rep.rejected),
               "weight_sum_error": float(abs(w.sum() - 1.0)),
               "projection_roundtrip_mm": round(spatial.roundtrip_error_m(synth.STATIONS) * 1000, 9),
               "idempotent": sha1 == sha2,
               "tests_passed": int(m.group(1)) if m and r.returncode == 0 else 0}}
    (HERE / "metrics.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if r.returncode != 0:
        print(r.stdout[-2000:], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
