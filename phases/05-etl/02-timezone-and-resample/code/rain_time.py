"""05/02 時區與重新取樣：把兩種來源的雨量對齊成「整點結束的時雨量」。

來源 A：10 分鐘雨量，時間戳記為 UTC、標示「該 10 分鐘結束的時刻」。
來源 B：時雨量，台灣時間（UTC+8），標示「該小時結束的時刻」。
目標：台灣時間、區間 (t−1h, t]、標籤 t 的時雨量。

執行：python code/rain_time.py
"""
import pandas as pd

TZ = "Asia/Taipei"


def source_a():
    """一場 6 mm 的短延時降雨：台灣時間 14:10–15:00 每 10 分鐘 1 mm（以 UTC 儲存）。"""
    end_local = pd.date_range("2026-06-01 14:10", periods=6, freq="10min", tz=TZ)
    return pd.Series(1.0, index=end_local.tz_convert("UTC"), name="rain_mm")


def source_b():
    """同一場雨在另一個測站系統的時雨量：15:00（台灣時間）結束的那一小時 6 mm。"""
    idx = pd.date_range("2026-06-01 13:00", periods=4, freq="1h", tz=TZ)
    return pd.Series([0.0, 0.0, 6.0, 0.0], index=idx, name="rain_mm")


def to_hourly_end(s: pd.Series) -> pd.Series:
    """轉成台灣時間、整點結束的時雨量。輸入必須帶時區（naive 時間直接拒收）。"""
    if s.index.tz is None:
        raise ValueError("時間沒有時區資訊；請先確認來源是 UTC 還是台灣時間再 tz_localize")
    return s.tz_convert(TZ).resample("1h", closed="right", label="right").sum()


def naive_hourly(s: pd.Series) -> pd.Series:
    """常見錯誤寫法：用 pandas 預設（區間左閉、標籤在左）。"""
    return s.tz_convert(TZ).resample("1h").sum()


if __name__ == "__main__":
    a = source_a()
    print("來源 A 原始（UTC）：", list(a.index.strftime("%H:%M")))
    print("\n預設 resample（錯誤）：")
    print(naive_hourly(a).to_string())
    print("\nclosed='right', label='right'（正確）：")
    print(to_hourly_end(a).to_string())
    merged = pd.concat({"A": to_hourly_end(a), "B": source_b()}, axis=1, sort=True).fillna(0.0)
    print("\n兩來源對齊：")
    print(merged.to_string())
    wrong_tz = a.tz_localize(None).tz_localize(TZ)       # 把 UTC 數字誤當台灣時間
    print("\n把 UTC 誤當台灣時間時，降雨被標在：", list(to_hourly_end(wrong_tz).loc[lambda x: x > 0].index.strftime("%m-%d %H:%M")))
