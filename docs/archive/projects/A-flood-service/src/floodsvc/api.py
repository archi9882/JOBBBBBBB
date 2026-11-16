"""模擬服務 API。

POST /v1/runs        建立潰壩模擬工作，回 202 與 Location；支援 Idempotency-Key 標頭
GET  /v1/runs/{id}   查狀態；done 時附結果
GET  /healthz        存活檢查（資料庫可連線）
錯誤回應採 RFC 9457 problem+json。

執行：uvicorn floodsvc.api:app --port 8000
"""
import json
import os
from contextlib import closing
from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator
from . import jobs

app = FastAPI(title="Flood simulation service", version="1.0")


def db_path():
    return os.environ.get("FLOODSVC_DB", "floodsvc.db")


def con():
    """每個請求開一條新連線。FastAPI 的同步端點在執行緒池中執行，
    sqlite3 連線預設不能跨執行緒共用（見 falsification.md）。"""
    return closing(jobs.connect(db_path()))


class RunRequest(BaseModel):
    h_left: float = Field(gt=0, le=50, description="上游初始水深 m")
    h_right: float = Field(ge=0, le=50, description="下游初始水深 m；0 為乾床")
    length: float = Field(default=1000.0, gt=0, le=1e5, description="渠道長 m，壩位於中點")
    cells: int = Field(default=400, ge=50, le=20000, description="網格數（上限防止單一請求耗盡資源）")
    t_end: float = Field(default=20.0, gt=0, le=3600, description="模擬時間 s")

    @model_validator(mode="after")
    def check(self):
        if self.h_right >= self.h_left:
            raise ValueError("h_right 必須小於 h_left（本服務只處理向下游潰壩）")
        return self


def problem(status, title, detail, **extra):
    return JSONResponse({"type": "about:blank", "title": title, "status": status, "detail": detail, **extra},
                        status_code=status, media_type="application/problem+json")


@app.exception_handler(RequestValidationError)
async def _validation(request: Request, exc: RequestValidationError):
    errs = [{"loc": list(e["loc"]), "msg": e["msg"]} for e in exc.errors()]
    return problem(422, "輸入參數不合法", "見 errors 欄位", errors=errs)


@app.exception_handler(Exception)
async def _internal(request: Request, exc: Exception):
    return problem(500, "伺服器內部錯誤", "請稍後再試；錯誤已記錄")   # 不把堆疊追蹤回給使用者


@app.post("/v1/runs", status_code=202)
def create_run(req: RunRequest, idempotency_key: str | None = Header(default=None)):
    with con() as c:
        try:
            jid, new = jobs.create(c, req.model_dump(), idempotency_key)
        except ValueError as e:
            return problem(409, "Idempotency-Key 衝突", str(e))
        status = "queued" if new else jobs.get(c, jid)["status"]
    return JSONResponse({"id": jid, "status": status},
                        status_code=202 if new else 200, headers={"Location": f"/v1/runs/{jid}"})


@app.get("/v1/runs/{jid}")
def get_run(jid: str):
    with con() as c:
        row = jobs.get(c, jid)
    if row is None:
        return problem(404, "找不到工作", f"id={jid}")
    out = {"id": jid, "status": row["status"], "params": json.loads(row["params"]), "attempts": row["attempts"]}
    if row["status"] == "done":
        out["result"] = json.loads(row["result"])
    if row["status"] == "failed":
        out["error"] = row["error"]
    return out


@app.get("/healthz")
def healthz():
    with con() as c:
        c.execute("SELECT 1")
    return {"ok": True}
