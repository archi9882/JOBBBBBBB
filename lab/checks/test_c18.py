"""卡 18 驗收：lab/mine/api.py 的錯誤格式、冪等、失敗處理（建立在卡 17 之上）"""
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


def wait_end(c, loc):
    for _ in range(100):
        b = c.get(loc).json()
        if b["status"] in ("done", "failed"):
            return b
        time.sleep(0.05)
    raise AssertionError("沒結束")


def is_problem(r, status):
    b = r.json()
    return (r.status_code == status and r.headers["content-type"].startswith("application/problem+json")
            and b["status"] == status and {"type", "title", "detail"} <= set(b))


def test_unknown_case_is_422_problem(client):
    assert is_problem(client.post("/runs", json={"case": "nope"}), 422)


def test_missing_field_is_also_problem_format(client):
    assert is_problem(client.post("/runs", json={}), 422)


def test_unknown_run_is_404_problem(client):
    assert is_problem(client.get("/runs/nope"), 404)


def test_failed_run_reports_error_and_map_is_409(client):
    loc = client.post("/runs", json={"case": "boom"}).headers["location"]
    b = wait_end(client, loc)
    assert b["status"] == "failed" and "COMCOT" in b["error"]
    assert is_problem(client.get(loc + "/map"), 409)


def test_idempotency_key_same_body_same_id(client):
    h = {"Idempotency-Key": "k1"}
    a = client.post("/runs", json={"case": "toy"}, headers=h)
    b = client.post("/runs", json={"case": "toy"}, headers=h)
    assert a.json()["id"] == b.json()["id"]
    assert a.headers["location"] == b.headers["location"]


def test_idempotency_key_different_body_is_422(client):
    h = {"Idempotency-Key": "k2"}
    client.post("/runs", json={"case": "toy"}, headers=h)
    assert is_problem(client.post("/runs", json={"case": "boom"}, headers=h), 422)


def test_without_key_each_post_is_new(client):
    assert client.post("/runs", json={"case": "toy"}).json()["id"] != client.post("/runs", json={"case": "toy"}).json()["id"]
