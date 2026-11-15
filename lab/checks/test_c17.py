"""卡 17 驗收：lab/mine/api.py（只測 202／Location／狀態流程；不需要 COMCOT）"""
import time
import pytest
from fastapi.testclient import TestClient
import api

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 16


@pytest.fixture
def client(tmp_path, monkeypatch):
    png = tmp_path / "map.png"; png.write_bytes(PNG)
    monkeypatch.setattr(api, "run_case", lambda name: str(png))
    monkeypatch.setattr(api, "CASE_NAMES", {"toy", "toy_slip10"}, raising=False)
    return TestClient(api.app)


def wait_done(c, loc, timeout=5.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        body = c.get(loc).json()
        if body["status"] in ("done", "failed"):
            return body
        time.sleep(0.05)
    raise AssertionError("工作一直沒結束")


def test_post_returns_202_and_location(client):
    r = client.post("/runs", json={"case": "toy"})
    assert r.status_code == 202
    loc = r.headers["location"]
    assert loc.startswith("/runs/") and r.json()["id"] == loc.rsplit("/", 1)[1]
    assert r.json()["status"] in ("queued", "running", "done")


def test_poll_until_done_then_get_map(client):
    loc = client.post("/runs", json={"case": "toy"}).headers["location"]
    body = wait_done(client, loc)
    assert body["status"] == "done"
    m = client.get(loc + "/map")
    assert m.status_code == 200 and m.headers["content-type"] == "image/png" and m.content == PNG


def test_two_posts_two_ids(client):
    a = client.post("/runs", json={"case": "toy"}).json()["id"]
    b = client.post("/runs", json={"case": "toy_slip10"}).json()["id"]
    assert a != b


def test_unknown_id_is_404(client):
    assert client.get("/runs/does-not-exist").status_code == 404
