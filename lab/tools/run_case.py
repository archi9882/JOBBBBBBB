"""跑一個情境：python lab/tools/run_case.py <情境名>，情境定義在 lab/cases.py。

在 lab/runs/<情境名>/ 產生控制檔、地形、COMCOT 輸出與 map.png。
"""
import importlib.util
import shutil
import subprocess
import sys
import time
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
import comcot_ctl, plot, synth_bathy  # noqa: E402

BIN = LAB / "vendor" / "comcot-gfortran" / "comcot"


def main(name):
    spec = importlib.util.spec_from_file_location("cases", LAB / "cases.py")
    cases = importlib.util.module_from_spec(spec); spec.loader.exec_module(cases)
    c = cases.CASES[name]
    run = LAB / "runs" / name
    if run.exists():
        shutil.rmtree(run)
    run.mkdir(parents=True)
    if c["layer1"]["bathy"] == "synthetic":
        synth_bathy.write(run / "bathy.xyz")
        c["layer1"]["bathy"] = "bathy.xyz"
    else:
        src = (LAB / c["layer1"]["bathy"]).resolve()
        (run / "bathy.xyz").symlink_to(src)
        c["layer1"]["bathy"] = "bathy.xyz"
    for f in ("fault_multi.ctl", "landslide.ctl", "ts_name.dat"):
        shutil.copy(BIN.parent / f, run / f)
    (run / "ts_location.dat").write_text("\n".join(f"{lon} {lat}" for lon, lat in c.get("gauges", [(120.3, 22.6)])) + "\n")
    comcot_ctl.write_ctl(run / "comcot.ctl", run_time=c["run_time"], save_every=c["save_every"],
                         fault=c["fault"], layer1=c["layer1"])
    t0 = time.time()
    r = subprocess.run([str(BIN)], cwd=run, capture_output=True, text=True)
    (run / "run.log").write_text(r.stdout + r.stderr)
    if r.returncode != 0 or not (run / "zmax_layer01.dat").exists():
        print(f"COMCOT 失敗（結束碼 {r.returncode}），看 {run/'run.log'}")
        sys.exit(1)
    print(f"完成：{time.time()-t0:.1f} 秒")
    plot.main(run)


if __name__ == "__main__":
    main(sys.argv[1])
