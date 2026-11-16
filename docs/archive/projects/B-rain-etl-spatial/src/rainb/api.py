"""服務：GET /v1/areal-rainfall、/healthz、/metrics。啟動時跑一次 ETL。"""
import time
from datetime import datetime
from pathlib import Path
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

from . import etl, spatial, synth


def create_app(work_dir: Path) -> FastAPI:
    reg = CollectorRegistry()                  # 每個 app 自己的 registry，測試重複建立也不衝突
    requests = Counter("rainb_requests_total", "HTTP 請求數", ["path", "status"], registry=reg)
    rejected = Gauge("rainb_etl_rejected_rows", "最近一次 ETL 拒收列數", registry=reg)
    last_run = Gauge("rainb_etl_last_run_timestamp_seconds", "最近一次 ETL 完成時間（Unix 秒）", registry=reg)

    a, b = synth.write_sources(work_dir / "raw")
    merged, rep, _ = etl.run(a, b, work_dir / "clean", list(synth.STATIONS), synth.HOURS)
    w = spatial.weights(spatial.thiessen(spatial.project(synth.STATIONS)))
    areal = spatial.areal_rainfall(merged, w, synth.HOURS)
    rejected.set(len(rep.rejected))
    last_run.set(time.time())

    app = FastAPI(title="雨量 ETL＋面積雨量", version="0.1.0")

    @app.get("/healthz")
    def healthz():
        requests.labels("/healthz", "200").inc()
        return {"status": "ok", "hours": int(areal.rain_mm.notna().sum())}

    @app.get("/v1/areal-rainfall")
    def areal_rainfall(start: datetime = Query(...), end: datetime = Query(...)):
        if start.tzinfo is None or end.tzinfo is None:
            requests.labels("/v1/areal-rainfall", "400").inc()
            raise HTTPException(400, "start／end 必須帶時區，例如 2026-06-01T10:00:00+08:00")
        if start >= end:
            requests.labels("/v1/areal-rainfall", "400").inc()
            raise HTTPException(400, "start 必須早於 end")
        sel = areal[(areal.index > start) & (areal.index <= end)]   # 區間 (start, end]，與時雨量一致
        requests.labels("/v1/areal-rainfall", "200").inc()
        return {"unit": "mm/h", "interval": "(t-1h, t]", "min_coverage": spatial.MIN_COVERAGE,
                "data": [{"time": t.isoformat(),
                          "rain_mm": None if np.isnan(r.rain_mm) else round(float(r.rain_mm), 3),
                          "coverage": round(float(r.coverage), 4)} for t, r in sel.iterrows()]}

    @app.get("/metrics")
    def metrics():
        return PlainTextResponse(generate_latest(reg), media_type=CONTENT_TYPE_LATEST)

    return app


def default_app():
    """uvicorn 入口：uvicorn rainb.api:default_app --factory"""
    import os
    return create_app(Path(os.environ.get("RAINB_WORK_DIR", "/tmp/rainb")))
