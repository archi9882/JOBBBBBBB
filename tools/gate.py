"""專案 C 的關卡檢查：由下往上，條件未滿足的層不准放程式碼。

用法：
    python tools/gate.py          # 列出每層狀態；有違規時結束碼 1（CI 會失敗）

每層的條件（projects/C-groundwater-bottomup/gate.toml）：
    lessons  對應課程已出貨（tools/ship_check.py 判定，含測試通過）
    grill    對應 grill 目標分數 ≥ 2（grill/scores.json）
    below    下一層已通過
一層「通過」＝ 已解鎖、有 tests/test_*.py 且全過、有 math.md 或 design.md、有 falsification.md。
"""
import json
import subprocess
import sys
import tomllib
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "projects" / "C-groundwater-bottomup"
sys.path.insert(0, str(ROOT / "tools"))
from ship_check import status as lesson_status  # noqa: E402

GRILL_PASS = 2


@lru_cache(maxsize=None)
def shipped(lesson_id):
    p, l = lesson_id.split("/")
    hits = [d for d in (ROOT / "phases").glob(f"{p}-*/{l}-*") if d.is_dir()]
    return bool(hits) and lesson_status(hits[0], run=True)[-1]


def grill_scores():
    f = ROOT / "grill" / "scores.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def _tests_pass(d):
    if not any(d.glob("tests/test_*.py")):
        return False
    r = subprocess.run([sys.executable, "-m", "pytest", "-o", "addopts=--import-mode=importlib", "-q",
                        "-p", "no:cacheprovider", str(d / "tests")], cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def layer_status():
    """回傳 [{id, title, unlocked, has_code, passed, missing}]，依 gate.toml 順序。"""
    gate = tomllib.loads((C / "gate.toml").read_text(encoding="utf-8"))["layer"]
    scores = grill_scores()
    out, passed_ids = [], set()
    for L in gate:
        d = C / "layers" / L["id"]
        missing = [f"課程 {x} 未出貨" for x in L.get("lessons", []) if not shipped(x)]
        missing += [f"grill {g} < {GRILL_PASS}（目前 {scores.get(g, {}).get('score', 0)}）"
                    for g in L.get("grill", []) if scores.get(g, {}).get("score", 0) < GRILL_PASS]
        if L.get("below") and L["below"] not in passed_ids:
            missing.append(f"下一層 {L['below']} 未通過")
        unlocked = not missing
        has_code = any(p for p in d.rglob("*.py"))
        docs_ok = ((d / "math.md").exists() or (d / "design.md").exists()) and (d / "falsification.md").exists()
        passed = unlocked and has_code and docs_ok and _tests_pass(d)
        if passed:
            passed_ids.add(L["id"])
        out.append(dict(id=L["id"], title=L["title"], unlocked=unlocked, has_code=has_code,
                        passed=passed, missing=missing))
    return out


def main():
    rows = layer_status()
    bad = False
    for r in rows:
        if r["passed"]:
            s = "通過"
        elif r["unlocked"]:
            s = "已解鎖，進行中" if r["has_code"] else "已解鎖，可以開始"
        elif r["has_code"]:
            s = "違規：未解鎖卻有程式碼"
            bad = True
        else:
            s = "鎖定"
        print(f"{r['id']:<24} {s}")
        for m in r["missing"][:6]:
            print(f"    - {m}")
        if len(r["missing"]) > 6:
            print(f"    - …另有 {len(r['missing']) - 6} 項")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
