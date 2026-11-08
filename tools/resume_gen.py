"""履歷生產表：依證據自動產生履歷敘述。

用法：
    python tools/resume_gen.py            # 只讀現有 metrics.json
    python tools/resume_gen.py --refresh  # 先重跑專案 A、B 的 metrics.py

輸出（resume/generated/）：
    resume_table.md / resume_table.csv   每條敘述的狀態、缺什麼、面試會被問什麼
    bullets_zh.md / bullets_en.md        只含已解鎖的敘述，可直接貼進履歷
"""
import csv
import json
import operator
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resume" / "generated"
sys.path.insert(0, str(ROOT / "tools"))
from gate import shipped, grill_scores, layer_status, GRILL_PASS  # noqa: E402

PROJECTS = {"A": ROOT / "projects" / "A-flood-service", "B": ROOT / "projects" / "B-rain-etl-spatial"}
OPS = {"==": operator.eq, "!=": operator.ne, ">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt}


def load_metrics(refresh):
    m = {}
    for k, d in PROJECTS.items():
        if refresh and (d / "metrics.py").exists():
            subprocess.run([sys.executable, str(d / "metrics.py")], cwd=ROOT, capture_output=True)
        f = d / "metrics.json"
        m[k] = json.loads(f.read_text(encoding="utf-8"))["metrics"] if f.exists() else {}
    return m


def falsification_mine():
    f = ROOT / "docs" / "ai-falsification-log.md"
    rows = [r for r in f.read_text(encoding="utf-8").splitlines() if r.startswith("|")][2:]
    return sum(1 for r in rows if r.split("|")[2].strip() == "我")


def parse_value(s):
    s = s.strip()
    if s in ("true", "false"):
        return s == "true"
    try:
        return float(s)
    except ValueError:
        return s


def check_metric(expr, metrics):
    m = re.fullmatch(r"\s*([AB])\.(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)", expr)
    if not m:
        raise ValueError(f"看不懂的條件：{expr}")
    p, key, op, val = m.groups()
    if key not in metrics.get(p, {}):
        return False, f"{p}/metrics.json 沒有 {key}（先跑 metrics.py）"
    have = metrics[p][key]
    ok = OPS[op](have, parse_value(val))
    return ok, None if ok else f"{expr}（目前 {have}）"


def fill(text, metrics, nmine):
    def rep(m):
        p, key, fmt = m.group(1), m.group(2), m.group(3)
        v = metrics.get(p, {}).get(key, "?")
        return format(v, fmt) if fmt and v != "?" else str(v)
    text = re.sub(r"\{([AB])\.(\w+)(?::([^}]+))?\}", rep, text)
    return text.replace("{falsification_mine}", str(nmine))


def evaluate(claim, metrics, scores, layers, nmine):
    req, missing = claim.get("requires", {}), []
    missing += [f"grill {g} 分數 {scores.get(g, {}).get('score', 0)} < {GRILL_PASS}"
                for g in req.get("grill", []) if scores.get(g, {}).get("score", 0) < GRILL_PASS]
    missing += [f"課程 {x} 未出貨" for x in req.get("lessons", []) if not shipped(x)]
    missing += [f"專案 C {x} 未通過" for x in req.get("layers", []) if not layers.get(x)]
    for e in req.get("metrics", []):
        ok, why = check_metric(e, metrics)
        if not ok:
            missing.append(why)
    need = req.get("falsification_mine")
    if need and nmine < need:
        missing.append(f"自己的否證紀錄 {nmine} 筆 < {need}")
    return missing


def main():
    claims = tomllib.loads((ROOT / "resume" / "claims.toml").read_text(encoding="utf-8"))["claim"]
    metrics = load_metrics("--refresh" in sys.argv)
    scores = grill_scores()
    layers = {r["id"]: r["passed"] for r in layer_status()}
    nmine = falsification_mine()
    OUT.mkdir(parents=True, exist_ok=True)

    rows = []
    for c in claims:
        missing = evaluate(c, metrics, scores, layers, nmine)
        rows.append(dict(id=c["id"], capability=c["capability"], unlocked=not missing,
                         missing="；".join(missing), zh=fill(c["zh"], metrics, nmine),
                         en=fill(c["en"], metrics, nmine), interview=c.get("interview", "")))

    n_ok = sum(r["unlocked"] for r in rows)
    with open(OUT / "resume_table.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    md = [f"# 履歷生產表（自動產生，勿手改）\n\n已解鎖 {n_ok}／{len(rows)} 條。重新產生：`python tools/resume_gen.py --refresh`\n",
          "| 敘述 | 能力 | 狀態 | 還缺什麼 | 面試會被問 |", "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['capability']} | {'已解鎖' if r['unlocked'] else '鎖定'} | "
                  f"{r['missing'] or '—'} | {r['interview']} |")
    md.append("\n## 敘述預覽（含未解鎖；數字取自目前的 metrics.json）\n")
    for r in rows:
        md.append(f"- **{r['id']}**{'' if r['unlocked'] else '（鎖定）'}：{r['zh']}")
    (OUT / "resume_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    for lang, title in (("zh", "履歷敘述（已解鎖）"), ("en", "Resume bullets (unlocked)")):
        lines = [f"# {title}\n"]
        for cap in dict.fromkeys(r["capability"] for r in rows if r["unlocked"]):
            lines.append(f"\n## {cap}\n")
            lines += [f"- {r[lang]}" for r in rows if r["unlocked"] and r["capability"] == cap]
        if n_ok == 0:
            lines.append("\n尚未解鎖任何敘述。先用 grill-me 拆解專案 A、B，或完成課程。\n" if lang == "zh"
                         else "\nNothing unlocked yet.\n")
        (OUT / f"bullets_{lang}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"已解鎖 {n_ok}/{len(rows)}；輸出在 {OUT.relative_to(ROOT)}/")
    for r in rows:
        print(f"  {'✓' if r['unlocked'] else '·'} {r['id']:<22} {r['missing'][:70]}")


if __name__ == "__main__":
    main()
