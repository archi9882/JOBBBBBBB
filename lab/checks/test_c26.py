"""卡 26 驗收：lab/mine/api.py 的 /metrics（建立在卡 17、18 之上）"""
import re
import time
import pytest
from fastapi.testclient import TestClient
import api

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 16


@pytest.fixture
def client(tmp_path, monkeypatch):
    png = tmp_path / "map.png"; png.write_bytes(PNG)

    def fake(name):
        if name == "boom":
            raise RuntimeError("COMCOT 崩潰")
        return str(png)

    monkeypatch.setattr(api, "run_case", fake)
    monkeypatch.setattr(api, "CASE_NAMES", {"toy", "boom"}, raising=False)
    return TestClient(api.app)


def metric(text, name, labels=""):
    m = re.search(rf"^{re.escape(name)}{re.escape(labels)} ([0-9.eE+-]+)$", text, re.M)
    return float(m.group(1)) if m else None


def run_and_wait(c, case):
    loc = c.post("/runs", json={"case": case}).headers["location"]
    for _ in range(100):
        if c.get(loc).json()["status"] in ("done", "failed"):
            return
        time.sleep(0.05)
    raise AssertionError("沒結束")


def test_metrics_endpoint_is_prometheus_text(client):
    r = client.get("/metrics")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/plain")


def test_counts_done_and_failed(client):
    before = client.get("/metrics").text
    d0 = metric(before, "tsunami_runs_total", '{status="done"}') or 0.0
    f0 = metric(before, "tsunami_runs_total", '{status="failed"}') or 0.0
    run_and_wait(client, "toy"); run_and_wait(client, "toy"); run_and_wait(client, "boom")
    after = client.get("/metrics").text
    assert metric(after, "tsunami_runs_total", '{status="done"}') == d0 + 2
    assert metric(after, "tsunami_runs_total", '{status="failed"}') == f0 + 1


def test_duration_histogram_and_in_progress_gauge(client):
    run_and_wait(client, "toy")
    t = client.get("/metrics").text
    assert metric(t, "tsunami_run_seconds_count") is not None, "缺 tsunami_run_seconds（histogram）"
    assert metric(t, "tsunami_runs_in_progress") == 0.0, "全部結束後 in_progress 應為 0"
