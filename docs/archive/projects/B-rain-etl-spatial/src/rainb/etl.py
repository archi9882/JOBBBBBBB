"""ETL：讀兩個來源 → 驗證與清理 → 對齊成「台灣時間、整點結束」的時雨量 → 合併 → 品質報表。

合併優先順序（寫死在 merge()）：
  1. 來源 A 該站該小時 6 筆 10 分鐘資料都有效 → 用 A 加總（解析度較高）。
  2. 否則若來源 B 有值 → 用 B。
  3. 否則該站該小時缺值（不補、不內插）。
"""
import hashlib
import json
from dataclasses import dataclass, field
import pandas as pd

TZ = "Asia/Taipei"
SENTINELS = {-999}
MAX_10MIN_MM = 50.0        # 物理範圍上限（10 分鐘 50 mm；超過視為異常）
MAX_HOUR_MM = 200.0


@dataclass
class Report:
    rejected: list = field(default_factory=list)   # (來源, 站, 原始時間, 原因)
    duplicates: dict = field(default_factory=dict)  # 站 → 重複列數

    def reject(self, src, st, t, why):
        self.rejected.append((src, st, t, why))


def parse_time(s):
    """解析 ISO8601；沒有時區就回 None（呼叫端拒收），不猜。"""
    try:
        t = pd.Timestamp(s)
    except (ValueError, TypeError):
        return None
    return t if t.tzinfo is not None else None


def load_a(path, rep):
    """來源 A：10 分鐘、UTC、0.1 mm、哨兵 -999。回傳 (station, end[台灣時間], rain_mm)。"""
    raw = pd.read_csv(path, dtype=str)
    dup = raw.duplicated()                             # 完全相同的列才算重複（保留第一筆）
    for st, n in raw[dup].station.value_counts().items():
        rep.duplicates[st] = rep.duplicates.get(st, 0) + int(n)
    raw = raw[~dup]
    keep = []
    for st, ts, v in raw[["station", "time", "value"]].itertuples(index=False):
        t = parse_time(ts)
        if t is None:
            rep.reject("A", st, ts, "time_without_timezone"); continue
        try:
            x = float(v)
        except (ValueError, TypeError):
            rep.reject("A", st, ts, "not_a_number"); continue
        if x in SENTINELS:
            rep.reject("A", st, ts, "sentinel_missing"); continue
        mm = x / 10.0                                  # 0.1 mm → mm
        if mm < 0 or mm > MAX_10MIN_MM:
            rep.reject("A", st, ts, "out_of_physical_range"); continue
        keep.append((st, t.tz_convert(TZ), mm))
    return pd.DataFrame(keep, columns=["station", "end", "rain_mm"])


def hourly_from_a(a):
    """10 分鐘 → 整點結束時雨量。區間 (t−1h, t]、標籤 t；同時數有效筆數。"""
    out = []
    for st, g in a.groupby("station"):
        r = g.set_index("end")["rain_mm"].resample("1h", closed="right", label="right")
        out.append(pd.DataFrame({"station": st, "rain_mm": r.sum(), "n": r.count()}))
    h = pd.concat(out).rename_axis("time").reset_index()
    return h


def load_b(path, rep):
    """來源 B：時雨量、台灣時間、mm、整點結束標記。"""
    keep = []
    for rec in json.loads(path.read_text(encoding="utf-8")):
        st, ts, v = rec.get("station"), rec.get("time"), rec.get("rain_mm")
        t = parse_time(ts)
        if t is None:
            rep.reject("B", st, ts, "time_without_timezone"); continue
        if v is None:
            rep.reject("B", st, ts, "null_value"); continue
        if not (0 <= float(v) <= MAX_HOUR_MM):
            rep.reject("B", st, ts, "out_of_physical_range"); continue
        keep.append((st, t.tz_convert(TZ), float(v)))
    return pd.DataFrame(keep, columns=["station", "time", "rain_mm"])


def merge(ha, b):
    """依模組說明的優先順序合併。回傳 station, time, rain_mm, source。"""
    full = ha[ha.n == 6][["station", "time", "rain_mm"]].assign(source="A")
    key = set(zip(full.station, full.time))
    fill = b[[(s, t) not in key for s, t in zip(b.station, b.time)]].assign(source="B")
    m = pd.concat([full, fill], ignore_index=True)
    return m.sort_values(["station", "time"]).reset_index(drop=True)


def quality(merged, rep, stations, hours):
    """各站：應有時數、實有時數、缺值率、重複列、拒收列。"""
    rows = []
    for s in stations:
        n = int((merged.station == s).sum())
        rows.append({"station": s, "expected_hours": len(hours), "hours": n,
                     "missing_rate": round(1 - n / len(hours), 4),
                     "duplicates": rep.duplicates.get(s, 0),
                     "rejected": sum(1 for r in rep.rejected if r[1] == s)})
    return pd.DataFrame(rows)


def to_csv_bytes(merged):
    """確定性輸出：固定排序、固定格式，讓重跑的 sha256 相同。"""
    d = merged.sort_values(["station", "time"]).copy()
    d["time"] = d["time"].map(lambda t: t.isoformat())
    return d.to_csv(index=False, float_format="%.1f", lineterminator="\n").encode("utf-8")


def run(path_a, path_b, out_dir, stations, hours):
    """完整 ETL。寫出 hourly.csv、quality.csv、rejected.csv，回傳 (merged, report, sha256)。"""
    rep = Report()
    merged = merge(hourly_from_a(load_a(path_a, rep)), load_b(path_b, rep))
    out_dir.mkdir(parents=True, exist_ok=True)
    data = to_csv_bytes(merged)
    (out_dir / "hourly.csv").write_bytes(data)                       # 覆寫，不 append
    quality(merged, rep, stations, hours).to_csv(out_dir / "quality.csv", index=False, lineterminator="\n")
    pd.DataFrame(rep.rejected, columns=["source", "station", "time", "reason"]).to_csv(
        out_dir / "rejected.csv", index=False, lineterminator="\n")
    return merged, rep, hashlib.sha256(data).hexdigest()
