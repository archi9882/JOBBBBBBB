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
