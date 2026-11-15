"""卡片進度。

    python lab/tools/card.py              # 顯示下一張卡與進度
    python lab/tools/card.py done 01 "一句收穫"   # 完成一張卡（寫入 lab/progress.json 與 lab/log.md）
"""
import datetime as dt
import json
import sys
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
CARDS = tomllib.loads((LAB / "cards.toml").read_text(encoding="utf-8"))["card"]
PROG = LAB / "progress.json"


def load():
    return json.loads(PROG.read_text(encoding="utf-8")) if PROG.exists() else {"done": {}}


def streak(done):
    days = sorted({v["date"] for v in done.values()}, reverse=True)
    if not days:
        return 0
    n, d = 0, dt.date.fromisoformat(days[0])
    if (dt.date.today() - d).days > 1:
        return 0
    for s in days:
        if dt.date.fromisoformat(s) == d:
            n += 1
            d -= dt.timedelta(days=1)
        else:
            break
    return n


def bar(k, n, w=13):
    f = round(w * k / n) if n else 0
    return "■" * f + "□" * (w - f)


def status(p):
    done = p["done"]
    nxt = next((c for c in CARDS if c["id"] not in done), None)
    print(f"進度 {bar(len(done), len(CARDS))} {len(done)}/{len(CARDS)} 張　｜　連續 {streak(done)} 晚")
    upcoming = next((c for c in CARDS if c["id"] not in done and c.get("milestone")), None)
    if upcoming:
        k = [c["id"] for c in CARDS].index(upcoming["id"]) + 1 - len(done)
        print(f"下一個里程碑：{upcoming['milestone']}（再 {k} 張）")
    if nxt is None:
        print("佇列做完了。請 Claude 依你最近的收穫補下一批卡。")
        return
    print(f"\n下一張　卡 {nxt['id']}［{nxt['kind']}］{nxt['title']}")
    print(f"背景：{nxt['context']}")
    print(f"先預測：{nxt['predict']}")
    if nxt.get("run"):
        print("然後執行：\n  " + "\n  ".join(nxt["run"]))
    print(f"成果：{nxt['win']}")


def done(cid, note):
    p = load()
    card = next((c for c in CARDS if c["id"] == cid), None)
    if card is None:
        sys.exit(f"沒有卡 {cid}")
    today = dt.date.today().isoformat()
    p["done"][cid] = {"date": today, "note": note}
    PROG.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")
    log = LAB / "log.md"
    if not log.exists():
        log.write_text("# 實驗日誌（一張卡一行）\n\n| 日期 | 卡 | 題目 | 收穫 |\n|---|---|---|---|\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"| {today} | {cid} | {card['title']} | {note} |\n")
    print(f"✓ 卡 {cid} {card['title']}")
    if card.get("milestone"):
        print(f"★ 解鎖：{card['milestone']}")
    status(p)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "done":
        done(sys.argv[2], " ".join(sys.argv[3:]) or "—")
    else:
        status(load())
