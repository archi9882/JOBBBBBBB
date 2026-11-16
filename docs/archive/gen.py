"""從 tools/curriculum.py 產生 lesson 骨架、CATALOG.md 與 learning-paths。已存在的 math.md／falsification.md／code／tests 不覆寫；README 與目錄每次重產。

用法：python tools/gen.py
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from curriculum import PHASES, CAP_NAMES, PATHS

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
TODO = "<!-- TODO -->"

def lesson_readme(pi, pslug, ptitle, li, l):
    slug, title, cap, prob, math, test, trap = l
    return f"""# {pi:02d}/{li:02d}　{title}

- Phase：{pslug}（{ptitle}）
- 能力：{cap} {CAP_NAMES[cap]}
- 狀態：由 `python tools/ship_check.py` 判定，不手寫

## 問題
{prob}

## 數學／原理（完整推導寫在 math.md）
{math}

## 測試：通過條件
{test}

## AI 否證目標
{trap}

## 出貨條件（四項都完成才算這堂課完成）
1. `math.md`：逐步推導，每步交代上一步留下什麼、這步補什麼。
2. `code/`：可在 WSL2 Ubuntu 直接執行的程式，附實跑輸出。
3. `tests/`：把「通過條件」寫成 pytest，且全部通過。
4. `falsification.md`：至少一筆 AI 否證紀錄（AI 說了什麼、怎麼驗證、結論）。
"""

lessons_all = []
for pi, (pslug, ptitle, lessons) in enumerate(PHASES):
    for li, l in enumerate(lessons, start=1):
        d = ROOT / "phases" / pslug / l[0]
        (d / "code").mkdir(parents=True, exist_ok=True)
        (d / "tests").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(lesson_readme(pi, pslug, ptitle, li, l), encoding="utf-8")
        for f, head in (("math.md", f"# {l[1]}：推導\n\n"), ("falsification.md", f"# {l[1]}：AI 否證紀錄\n\n")):
            if not (d / f).exists():
                (d / f).write_text(head + TODO + "\n", encoding="utf-8")
        for sub in ("code", "tests"):
            if not any((d / sub).iterdir()):
                (d / sub / ".gitkeep").write_text("")
        lessons_all.append((f"{pi:02d}/{li:02d}", pslug, l))

# learning paths
lp = ROOT / "learning-paths"; lp.mkdir(exist_ok=True)
ids = [x[0] for x in lessons_all]
for key, p in PATHS.items():
    sel = ids if p["lessons"] == "ALL" else p["lessons"]
    bad = [s for s in sel if s not in ids]
    assert not bad, f"{key} 有不存在的課：{bad}"
    out = {"id": key, "title": p["title"], "description": p["description"],
           "lessons": [{"id": s, "path": f"phases/{x[1]}/{x[2][0]}", "title": x[2][1]}
                       for s in sel for x in lessons_all if x[0] == s]}
    (lp / f"{key}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

# catalog
rows = []
for pi, (pslug, ptitle, lessons) in enumerate(PHASES):
    rows.append(f"\n### Phase {pi:02d}　{ptitle}（`{pslug}`）\n\n| 課 | 標題 | 能力 | 通過條件 |\n|---|---|---|---|")
    for li, l in enumerate(lessons, start=1):
        rows.append(f"| [{pi:02d}/{li:02d}](phases/{pslug}/{l[0]}) | {l[1]} | {l[2]} | {l[5]} |")
(ROOT / "CATALOG.md").write_text("# 課程目錄（由 gen 產生，勿手改）\n" + "\n".join(rows) + "\n", encoding="utf-8")
print(f"{len(PHASES)} phases, {len(lessons_all)} lessons")
