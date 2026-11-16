"""履歷生產表：依證據自動產生履歷敘述。

用法：
    python tools/resume_gen.py            # 依卡片、課程、grill 分數與否證紀錄產生

輸出（resume/generated/）：
    resume_table.md / resume_table.csv   每條敘述的狀態、缺什麼、面試會被問什麼
    bullets_zh.md / bullets_en.md        只含已解鎖的敘述，可直接貼進履歷
"""
import csv
import json
import sys
import tomllib
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resume" / "generated"
sys.path.insert(0, str(ROOT / "tools"))
from ship_check import status as lesson_status  # noqa: E402

GRILL_PASS = 2


@lru_cache(maxsize=None)
def shipped(lesson_id):
    p, l = lesson_id.split("/")
    hits = [d for d in (ROOT / "reserve-numerics").glob(f"{p}-*/{l}-*") if d.is_dir()]
    return bool(hits) and lesson_status(hits[0], run=True)[-1]


def grill_scores():
    f = ROOT / "grill" / "scores.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def falsification_mine():
    f = ROOT / "docs" / "ai-falsification-log.md"
    rows = [r for r in f.read_text(encoding="utf-8").splitlines() if r.startswith("|")][2:]
    return sum(1 for r in rows if r.split("|")[2].strip() == "我")


def fill(text, nmine):
    return text.replace("{falsification_mine}", str(nmine))


def evaluate(claim, scores, nmine):
    req, missing = claim.get("requires", {}), []
    missing += [f"grill {g} 分數 {scores.get(g, {}).get('score', 0)} < {GRILL_PASS}"
                for g in req.get("grill", []) if scores.get(g, {}).get("score", 0) < GRILL_PASS]
    missing += [f"課程 {x} 未出貨" for x in req.get("lessons", []) if not shipped(x)]
    lab = ROOT / "lab" / "progress.json"
    done = json.loads(lab.read_text(encoding="utf-8"))["done"] if lab.exists() else {}
    missing += [f"實驗室卡 {x} 未完成" for x in req.get("cards", []) if x not in done]
    need = req.get("falsification_mine")
    if need and nmine < need:
        missing.append(f"自己的否證紀錄 {nmine} 筆 < {need}")
    return missing


def main():
    claims = tomllib.loads((ROOT / "resume" / "claims.toml").read_text(encoding="utf-8"))["claim"]
    scores = grill_scores()
    nmine = falsification_mine()
    OUT.mkdir(parents=True, exist_ok=True)

    rows = []
    for c in claims:
        missing = evaluate(c, scores, nmine)
        rows.append(dict(id=c["id"], capability=c["capability"], unlocked=not missing,
                         missing="；".join(missing), zh=fill(c["zh"], nmine),
                         en=fill(c["en"], nmine), interview=c.get("interview", "")))

    n_ok = sum(r["unlocked"] for r in rows)
    with open(OUT / "resume_table.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    md = [f"# 履歷生產表（自動產生，勿手改）\n\n已解鎖 {n_ok}／{len(rows)} 條。重新產生：`python tools/resume_gen.py`\n",
          "| 敘述 | 能力 | 狀態 | 還缺什麼 | 面試會被問 |", "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['capability']} | {'已解鎖' if r['unlocked'] else '鎖定'} | "
                  f"{r['missing'] or '—'} | {r['interview']} |")
    md.append("\n## 敘述預覽（含未解鎖）\n")
    for r in rows:
        md.append(f"- **{r['id']}**{'' if r['unlocked'] else '（鎖定）'}：{r['zh']}")
    (OUT / "resume_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    for lang, title in (("zh", "履歷敘述（已解鎖）"), ("en", "Resume bullets (unlocked)")):
        lines = [f"# {title}\n"]
        for cap in dict.fromkeys(r["capability"] for r in rows if r["unlocked"]):
            lines.append(f"\n## {cap}\n")
            lines += [f"- {r[lang]}" for r in rows if r["unlocked"] and r["capability"] == cap]
        if n_ok == 0:
            lines.append("\n尚未解鎖任何敘述。先完成實驗室卡片。\n" if lang == "zh"
                         else "\nNothing unlocked yet.\n")
        (OUT / f"bullets_{lang}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"已解鎖 {n_ok}/{len(rows)}；輸出在 {OUT.relative_to(ROOT)}/")
    for r in rows:
        print(f"  {'✓' if r['unlocked'] else '·'} {r['id']:<22} {r['missing'][:70]}")


if __name__ == "__main__":
    main()
