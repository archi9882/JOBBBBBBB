import importlib
import time
import pytest
from fastapi.testclient import TestClient
from floodsvc import jobs


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOODSVC_DB", str(tmp_path / "t.db"))
    import floodsvc.api as api
    api = importlib.reload(api)
    return TestClient(api.app, raise_server_exceptions=False), api


def test_create_returns_202_and_location(client):
    c, _ = client
    r = c.post("/v1/runs", json={"h_left": 10, "h_right": 1})
    assert r.status_code == 202
    assert r.headers["location"] == f"/v1/runs/{r.json()['id']}"


@pytest.mark.parametrize("body", [
    {"h_left": -1, "h_right": 0},
    {"h_left": 1, "h_right": 2},
    {"h_left": 10, "h_right": 1, "cells": 10_000_000},
    {"h_left": 10},
])
def test_invalid_input_is_problem_json(client, body):
    c, _ = client
    r = c.post("/v1/runs", json=body)
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")
    assert "errors" in r.json()


def test_idempotency_key(client):
    c, _ = client
    b = {"h_left": 10, "h_right": 1}
    r1 = c.post("/v1/runs", json=b, headers={"Idempotency-Key": "k1"})
    r2 = c.post("/v1/runs", json=b, headers={"Idempotency-Key": "k1"})
    assert r1.json()["id"] == r2.json()["id"] and r2.status_code == 200
    r3 = c.post("/v1/runs", json={"h_left": 9, "h_right": 1}, headers={"Idempotency-Key": "k1"})
    assert r3.status_code == 409


def test_unknown_id_404(client):
    c, _ = client
    assert c.get("/v1/runs/nope").status_code == 404


def test_end_to_end_with_worker(client):
    c, api = client
    from floodsvc.worker import run_once
    jid = c.post("/v1/runs", json={"h_left": 10, "h_right": 1, "cells": 200}).json()["id"]
    assert c.get(f"/v1/runs/{jid}").json()["status"] == "queued"
    with api.con() as wc:                      # worker 用自己的連線，與 API 分開
        assert run_once(wc) is True
    out = c.get(f"/v1/runs/{jid}").json()
    assert out["status"] == "done"
    assert out["result"]["mass_rel_error"] < 1e-12
    assert out["result"]["l1_error_vs_analytic_m2"] < 80


def test_claim_is_exclusive(tmp_path):
    db = str(tmp_path / "q.db")
    a, b = jobs.connect(db), jobs.connect(db)
    jobs.create(a, {"x": 1})
    assert jobs.claim(a) is not None
    assert jobs.claim(b) is None


def test_stale_job_requeued_then_failed(tmp_path):
    con = jobs.connect(str(tmp_path / "s.db"))
    jid, _ = jobs.create(con, {"x": 1})
    for i in range(jobs.MAX_ATTEMPTS):
        assert jobs.claim(con)[0] == jid
        back, dead = jobs.requeue_stale(con, stale_after=10, now=time.time() + 100)
    assert jobs.get(con, jid)["status"] == "failed" and dead == 1


def test_solver_exception_marks_failed(tmp_path, monkeypatch):
    import floodsvc.worker as w
    con = jobs.connect(str(tmp_path / "f.db"))
    jid, _ = jobs.create(con, {"h_left": 10, "h_right": 1, "length": 1000, "cells": 100, "t_end": 1})
    monkeypatch.setattr(w, "simulate", lambda p: 1 / 0)
    w.run_once(con)
    row = jobs.get(con, jid)
    assert row["status"] == "failed" and "ZeroDivisionError" in row["error"]
