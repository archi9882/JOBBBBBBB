"""卡片進度。

    python lab/tools/card.py              # 顯示下一張卡與進度
    python lab/tools/card.py done 01 "一句收穫"   # 完成一張卡（寫入 lab/progress.json 與 lab/log.md）
    python lab/tools/card.py check [卡號]         # 跑實作卡的驗收測試（預設是下一張卡）
    python lab/tools/card.py hint 1|2|3 [卡號]    # 實作卡卡住時，依序看三層提示
實作卡的驗收測試沒過，done 不會記錄。MINE_DIR=lab/mine_ai 可改測別的程式目錄（卡 21）。
"""
import datetime as dt
import json
import subprocess
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
    if nxt.get("spec"):
        print(f"要寫的：{nxt['spec']}")
        print(f"驗收：python lab/tools/card.py check　｜　卡住：python lab/tools/card.py hint 1（最多到 3）")
    if nxt.get("run"):
        print("然後執行：\n  " + "\n  ".join(nxt["run"]))
    print(f"成果：{nxt['win']}")


def find(cid):
    p = load()
    if cid is None:
        c = next((c for c in CARDS if c["id"] not in p["done"]), None)
    else:
        c = next((c for c in CARDS if c["id"] == cid), None)
    if c is None:
        sys.exit("沒有這張卡（或佇列已做完）")
    return c


def run_check(card):
    """跑驗收測試；沒有 check 欄位的卡視為通過。回傳是否通過。"""
    if not card.get("check"):
        return True
    root = LAB.parent
    r = subprocess.run([sys.executable, "-m", "pytest", "-o", "addopts=", "-q", "-x", "--tb=short", card["check"]], cwd=root)
    return r.returncode == 0


def hint(level, cid):
    card = find(cid)
    hs = card.get("hints") or []
    if not hs:
        sys.exit(f"卡 {card['id']} 沒有提示")
    if not 1 <= level <= len(hs):
        sys.exit(f"提示層級 1–{len(hs)}")
    print(f"卡 {card['id']} 提示 {level}/{len(hs)}：{hs[level - 1]}")


def done(cid, note):
    p = load()
    card = next((c for c in CARDS if c["id"] == cid), None)
    if card is None:
        sys.exit(f"沒有卡 {cid}")
    if not run_check(card):
        sys.exit(f"✗ 卡 {cid} 的驗收測試沒過，不記錄完成。修好再 done。")
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
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "done":
        done(a[1], " ".join(a[2:]) or "—")
    elif a and a[0] == "check":
        c = find(a[1] if len(a) > 1 else None)
        if not c.get("check"):
            sys.exit(f"卡 {c['id']} 沒有驗收測試")
        sys.exit(0 if run_check(c) else 1)
    elif a and a[0] == "hint" and len(a) >= 2:
        hint(int(a[1]), a[2] if len(a) > 2 else None)
    else:
        status(load())
