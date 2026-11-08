import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rainb.api import create_app


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    return TestClient(create_app(tmp_path_factory.mktemp("b_api")))


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_areal_rainfall_window(client):
    r = client.get("/v1/areal-rainfall", params={"start": "2026-06-01T09:00:00+08:00",
                                                 "end": "2026-06-01T12:00:00+08:00"})
    assert r.status_code == 200
    times = [d["time"] for d in r.json()["data"]]
    assert times == ["2026-06-01T10:00:00+08:00", "2026-06-01T11:00:00+08:00", "2026-06-01T12:00:00+08:00"]
    s02_missing = r.json()["data"][0]                # 10:00 S02 缺值 → coverage < 1
    assert 0.5 < s02_missing["coverage"] < 1


def test_missing_param_422(client):
    assert client.get("/v1/areal-rainfall", params={"start": "2026-06-01T09:00:00+08:00"}).status_code == 422


def test_naive_time_400(client):
    r = client.get("/v1/areal-rainfall", params={"start": "2026-06-01T09:00:00", "end": "2026-06-01T12:00:00"})
    assert r.status_code == 400


def test_reversed_window_400(client):
    r = client.get("/v1/areal-rainfall", params={"start": "2026-06-01T12:00:00+08:00",
                                                 "end": "2026-06-01T09:00:00+08:00"})
    assert r.status_code == 400


def test_metrics_exposed(client):
    client.get("/healthz")
    t = client.get("/metrics").text
    assert "rainb_requests_total" in t
    assert "rainb_etl_rejected_rows 6.0" in t
    assert "rainb_etl_last_run_timestamp_seconds" in t


def test_unencoded_plus_in_url_is_422(client):
    # URL 中未編碼的 + 會被解成空白 → 無法解析 → 422（建置時用 curl 實測發現）
    r = client.get("/v1/areal-rainfall?start=2026-06-01T09:00:00+08:00&end=2026-06-01T12:00:00+08:00")
    assert r.status_code == 422


def test_validation_errors_not_counted_in_metrics(client):
    # 已知缺口：422 在處理函式之前回傳，自訂計數器看不到（見 falsification.md）
    client.get("/v1/areal-rainfall", params={"start": "not-a-time", "end": "x"})
    assert 'status="422"' not in client.get("/metrics").text
