"""判定每堂課是否「出貨」：math.md、code、tests、falsification.md 四項齊全，且（加 --run 時）測試通過。

用法：
    python tools/ship_check.py          # 只檢查檔案
    python tools/ship_check.py --run    # 另外對每堂已齊全的課跑 pytest
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODO = "<!-- TODO -->"

def done(p: Path) -> bool:
    return p.exists() and TODO not in p.read_text(encoding="utf-8") and len(p.read_text(encoding="utf-8").strip()) > 80

def status(d: Path, run: bool):
    m = done(d / "math.md")
    c = any(d.glob("code/*.py"))
    t = any(d.glob("tests/test_*.py"))
    f = done(d / "falsification.md")
    passed = None
    if run and t:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(d / "tests")],
                           cwd=ROOT, capture_output=True, text=True)
        passed = r.returncode == 0
    ok = m and c and t and f and (passed is not False)
    return m, c, t, f, passed, ok

def main():
    run = "--run" in sys.argv
    mark = lambda b: "✓" if b else "·"
    lessons = sorted(p for p in (ROOT / "phases").glob("*/*") if p.is_dir())
    shipped, failed = 0, False
    print(f"{'課':<46} 推導 程式 測試 否證 {'pytest' if run else ''}")
    for d in lessons:
        m, c, t, f, passed, ok = status(d, run)
        shipped += ok
        failed |= passed is False
        name = f"{d.parent.name[:2]}/{d.name[:2]} {d.name[3:]}"
        pt = "" if passed is None else ("通過" if passed else "失敗")
        print(f"{name:<46} {mark(m):^4} {mark(c):^4} {mark(t):^4} {mark(f):^4} {pt}{'  ← 已出貨' if ok else ''}")
    print(f"\n已出貨 {shipped}/{len(lessons)}")
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
