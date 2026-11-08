"""用 SQLite 手寫的最小工作佇列。

狀態機：queued → running → done | failed
- claim：在 BEGIN IMMEDIATE 交易內把最舊的 queued 改成 running，兩個 worker 不會拿到同一筆。
- 心跳：running 的工作定期更新 heartbeat；超過 stale_after 秒沒更新，視為 worker 已死，
  重新排入佇列，嘗試次數達上限則標為 failed。
"""
import json
import sqlite3
import time
import uuid

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  idem_key TEXT UNIQUE,
  params TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('queued','running','done','failed')),
  attempts INTEGER NOT NULL DEFAULT 0,
  result TEXT,
  error TEXT,
  created REAL NOT NULL,
  heartbeat REAL
);
CREATE INDEX IF NOT EXISTS jobs_status_created ON jobs(status, created);
"""
MAX_ATTEMPTS = 3


def connect(path):
    con = sqlite3.connect(path, timeout=30, isolation_level=None)   # 自己控制交易
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(SCHEMA)
    return con


def create(con, params, idem_key=None):
    """回傳 (job_id, created_new)。相同 idem_key 重送時回傳既有工作。"""
    if idem_key:
        row = con.execute("SELECT id, params FROM jobs WHERE idem_key=?", (idem_key,)).fetchone()
        if row:
            if json.loads(row["params"]) != params:
                raise ValueError("同一個 Idempotency-Key 不能搭配不同參數")
            return row["id"], False
    jid = uuid.uuid4().hex
    con.execute("INSERT INTO jobs (id, idem_key, params, status, created) VALUES (?,?,?,?,?)",
                (jid, idem_key, json.dumps(params, sort_keys=True), "queued", time.time()))
    return jid, True


def get(con, jid):
    row = con.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
    return dict(row) if row else None


def claim(con):
    con.execute("BEGIN IMMEDIATE")
    try:
        row = con.execute("SELECT id, params FROM jobs WHERE status='queued' ORDER BY created LIMIT 1").fetchone()
        if row is None:
            con.execute("COMMIT")
            return None
        con.execute("UPDATE jobs SET status='running', attempts=attempts+1, heartbeat=? WHERE id=?",
                    (time.time(), row["id"]))
        con.execute("COMMIT")
        return row["id"], json.loads(row["params"])
    except Exception:
        con.execute("ROLLBACK")
        raise


def heartbeat(con, jid):
    con.execute("UPDATE jobs SET heartbeat=? WHERE id=? AND status='running'", (time.time(), jid))


def finish(con, jid, result):
    con.execute("UPDATE jobs SET status='done', result=? WHERE id=?", (json.dumps(result), jid))


def fail(con, jid, error):
    con.execute("UPDATE jobs SET status='failed', error=? WHERE id=?", (error, jid))


def requeue_stale(con, stale_after=60.0, now=None):
    """回傳 (重排數, 判失敗數)。"""
    now = time.time() if now is None else now
    cut = now - stale_after
    con.execute("BEGIN IMMEDIATE")
    dead = con.execute("UPDATE jobs SET status='failed', error='worker 逾時次數達上限' "
                       "WHERE status='running' AND heartbeat<? AND attempts>=?", (cut, MAX_ATTEMPTS)).rowcount
    back = con.execute("UPDATE jobs SET status='queued' WHERE status='running' AND heartbeat<?", (cut,)).rowcount
    con.execute("COMMIT")
    return back, dead
