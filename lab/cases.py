"""情境定義。每張預測卡通常只改一兩個數字，複製一個情境改名即可。"""

TOY_FAULT = dict(depth=15000.0, length=200e3, width=80e3, slip=5.0,
                 strike=355.0, dip=20.0, rake=90.0, lat=20.0, lon=119.5)
TOY_LAYER = dict(x0=116.0, x1=124.0, y0=16.0, y1=24.0, dx_min=2.0, dt=3.0, bathy="synthetic")

CASES = {
    # 卡 01：第一次跑
    "toy": dict(run_time=3600.0, save_every=600.0, fault=TOY_FAULT, layer1=TOY_LAYER),
    # 卡 02：滑移量加倍
    "toy_slip10": dict(run_time=3600.0, save_every=600.0, fault={**TOY_FAULT, "slip": 10.0}, layer1=TOY_LAYER),
    # 卡 04：時間步放大
    "toy_dt30": dict(run_time=3600.0, save_every=600.0, fault=TOY_FAULT, layer1={**TOY_LAYER, "dt": 30.0}),
}

# 卡 09：真實台灣地形（需要先完成卡 08，產生 lab/data/taiwan_1min.xyz）。台灣北端到 25.3N，所以北界放到 26N。
# 卡 12、14 的 real_mw85、real_mw90、real_dx4、real_dx2 由你自己複製這一條改出來。
REAL_LAYER = {**TOY_LAYER, "y1": 26.0, "bathy": "data/taiwan_1min.xyz"}
CASES["real"] = dict(run_time=3600.0, save_every=600.0, fault=TOY_FAULT, layer1=REAL_LAYER,
                     gauges=[(120.3, 22.6)])   # 恆春外海附近的一個虛擬測站
