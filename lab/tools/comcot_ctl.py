"""產生 COMCOT 控制檔 comcot.ctl。

COMCOT 用固定欄位讀值：每行第 49 個字元是冒號，值從第 50 個字元開始。
- 數值欄位前面有空白沒關係；
- 檔名欄位前面**不能**有空白，否則會連空白一起當成檔名，開檔失敗後程式不會停，接著存取空陣列而崩潰（Segmentation fault）。
"""
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "vendor" / "comcot-gfortran" / "comcot.ctl"
FILENAME_KEYS = ("File Name", "FileName", "Specify Input")


def set_value(lines, key, value, start=0):
    for i in range(start, len(lines)):
        if lines[i].strip().startswith(key):
            if len(lines[i]) < 49 or lines[i][48] != ":":
                raise ValueError(f"第 {i+1} 行第 49 字元不是冒號：{lines[i]!r}")
            sep = "" if key.startswith(FILENAME_KEYS) else "  "
            lines[i] = lines[i][:49] + f"{sep}{value}"
            return i
    raise KeyError(key)


def write_ctl(path, *, run_time, save_every, fault, layer1, output=0):
    """fault：dict(depth, length, width, slip, strike, dip, rake, lat, lon)，單位 m 與度。
    layer1：dict(x0, x1, y0, y1, dx_min, dt, bathy, nonlinear=False, manning=None)。"""
    L = TEMPLATE.read_text().splitlines()
    set_value(L, "Total run time", run_time)
    set_value(L, "Time interval to Save Data", save_every)
    set_value(L, "Output Zmax & TS", output)
    set_value(L, "Faulting Option", 0)
    set_value(L, "Focal Depth", fault["depth"])
    set_value(L, "Length of source area", fault["length"])
    set_value(L, "Width of source area", fault["width"])
    set_value(L, "Dislocation of fault plate", fault["slip"])
    set_value(L, "Strike direction", fault["strike"])
    set_value(L, "Dip  angle", fault["dip"])
    set_value(L, "Slip angle", fault["rake"])
    set_value(L, "Origin of Comp. Domain (Layer 01) (Lat", layer1["y0"])
    set_value(L, "Origin of Comp. Domain (Layer 01) (Lon", layer1["x0"])
    set_value(L, "Epicenter Location: Latitude", fault["lat"])
    set_value(L, "Epicenter Location: Longitude", fault["lon"])
    i = set_value(L, "Run This Layer", 0)
    set_value(L, "Governing Equations", 1 if layer1.get("nonlinear") else 0, i)
    set_value(L, "Grid Size", layer1["dx_min"], i)
    set_value(L, "Time step", layer1["dt"], i)
    if layer1.get("manning") is not None:
        set_value(L, "Bottom Friction Switch", 0, i)
        set_value(L, "Manning's Roughness Coef.", layer1["manning"], i)
    set_value(L, "X_start", layer1["x0"], i)
    set_value(L, "X_end", layer1["x1"], i)
    set_value(L, "Y_Start", layer1["y0"], i)
    set_value(L, "Y_end", layer1["y1"], i)
    set_value(L, "File Name of Bathymetry Data", layer1["bathy"], i)
    Path(path).write_text("\n".join(L) + "\n")
