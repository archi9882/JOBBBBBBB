"""合成資料：先有「真值」，再由真值產生兩個格式、品質都不同的來源。

站點座標為虛構（台灣中部附近的合理數值），不是任何真實測站。
"""
import json
import numpy as np
import pandas as pd

TZ = "Asia/Taipei"
STATIONS = {               # 站號: (經度, 緯度)  WGS84，虛構
    "S01": (120.86, 24.07),
    "S02": (120.95, 24.09),
    "S03": (120.90, 24.01),
    "S04": (120.99, 24.02),
    "S05": (120.93, 23.95),
    "S06": (121.04, 23.93),   # 在流域外：權重應為 0
}
A_STATIONS = ["S01", "S02", "S03", "S04", "S05"]   # 10 分鐘、UTC、0.1 mm
B_STATIONS = ["S04", "S05", "S06"]                 # 時雨量、台灣時間、mm
HOURS = pd.date_range("2026-06-01 01:00", periods=24, freq="1h", tz=TZ)  # 整點「結束」標記


def truth_10min(seed=42):
    """真值：每站每 10 分鐘的雨量（整數，單位 0.1 mm）。一場中午前後的降雨。"""
    rng = np.random.default_rng(seed)
    ends = pd.date_range(HOURS[0] - pd.Timedelta("50min"), HOURS[-1], freq="10min", tz=TZ)
    t = (ends - ends[0]).total_seconds() / 3600.0
    shape = np.exp(-((t - 12.0) / 3.0) ** 2)            # 降雨強度的時間形狀
    rows = []
    for k, s in enumerate(STATIONS):
        scale = 20 + 6 * k                                # 各站強度不同（0.1 mm／10 分鐘）
        vals = rng.poisson(scale * shape)
        rows += [(s, e, int(v)) for e, v in zip(ends, vals)]
    return pd.DataFrame(rows, columns=["station", "end", "rain_01mm"])


def truth_hourly(t10=None):
    """真值時雨量（mm），區間 (t−1h, t]。用整數加總避免浮點誤差。"""
    t10 = truth_10min() if t10 is None else t10
    hour = t10["end"].dt.ceil("1h")                       # 10:10…11:00 → 11:00
    g = t10.assign(hour=hour).groupby(["station", "hour"])["rain_01mm"].sum()
    return (g / 10.0).rename("rain_mm")


def write_sources(out_dir):
    """寫出來源 A（CSV）與 B（JSON），並刻意放入已知的資料問題。回傳兩個路徑。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    t10 = truth_10min()
    a = t10[t10.station.isin(A_STATIONS)].copy()
    a["time"] = a["end"].dt.tz_convert("UTC").dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    a["value"] = a["rain_01mm"].astype(str)
    a = a[["station", "time", "value"]].reset_index(drop=True)

    def at(st, local):                                    # 找某站某 10 分鐘結束時刻的列號
        utc = pd.Timestamp(local, tz=TZ).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
        return a.index[(a.station == st) & (a.time == utc)][0]

    a.loc[at("S02", "2026-06-01 09:30"), "value"] = "-999"   # 缺值：S02 只有 A，該小時應缺
    a.loc[at("S04", "2026-06-01 12:20"), "value"] = "-999"   # 缺值：S04 由 B 補
    a.loc[at("S05", "2026-06-01 13:40"), "value"] = "-5"     # 負值：拒收，S05 由 B 補
    a.loc[at("S03", "2026-06-01 15:10"), "value"] = "abc"    # 非數字：schema 拒收
    extra = [a.loc[at("S01", "2026-06-01 11:10")].copy() for _ in range(2)]  # 2 筆完全重複
    naive = a.loc[at("S03", "2026-06-01 08:10")].copy()
    naive["time"] = naive["time"].rstrip("Z")              # 沒有時區：拒收（原列仍在）
    a = pd.concat([a, pd.DataFrame(extra), pd.DataFrame([naive])], ignore_index=True)
    a.to_csv(out_dir / "source_a_10min.csv", index=False)

    th = truth_hourly(t10)
    b = []
    for s in B_STATIONS:
        for h in HOURS:
            v = float(th[(s, h)])
            if s == "S06" and h.hour == 7:
                v = None                                   # B 自己的缺值
            b.append({"station": s, "time": h.isoformat(), "rain_mm": v})
    (out_dir / "source_b_hourly.json").write_text(json.dumps(b, indent=1), encoding="utf-8")
    return out_dir / "source_a_10min.csv", out_dir / "source_b_hourly.json"
