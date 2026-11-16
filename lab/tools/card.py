"""卡片進度。

    python lab/tools/card.py              # 各軌的下一張卡與進度
    python lab/tools/card.py PINN         # 指定一軌，看它下一張卡的全文
    python lab/tools/card.py 35           # 指定卡號，看全文（跳著做用這個）
    python lab/tools/card.py done 01 "一句收穫"   # 完成一張卡（寫入 lab/progress.json 與 lab/log.md）
    python lab/tools/card.py check [卡號]         # 跑實作卡的驗收測試（預設是下一張卡）
    python lab/tools/card.py hint 1|2|3 [卡號]    # 實作卡卡住時，依序看三層提示
卡片分成幾條平行軌（cards.toml 的 track 欄）；done、check、hint 本來就吃卡號，
所以要跳著做不必動佇列，直接給卡號即可。
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


def track_of(c):
    return c.get("track", "海嘯")


def tracks():
    """依卡片在檔案裡出現的順序列出軌名。"""
    seen = []
    for c in CARDS:
        if track_of(c) not in seen:
            seen.append(track_of(c))
    return seen


def next_in(track, done):
    return next((c for c in CARDS if track_of(c) == track and c["id"] not in done), None)


def milestone_of(track, done):
    """回傳 (里程碑文字, 還要幾張)。張數算同一軌裡排在它之前還沒做的卡，所以跳著做也不會算錯。"""
    k = 0
    for c in CARDS:
        if track_of(c) != track or c["id"] in done:
            continue
        k += 1
        if c.get("milestone"):
            return c["milestone"], k
    return None, 0


def show(card):
    print(f"\n卡 {card['id']}［{card['kind']}］{card['title']}　（{track_of(card)}）")
    print(f"背景：{card['context']}")
    print(f"先預測：{card['predict']}")
    if card.get("spec"):
        print(f"要寫的：{card['spec']}")
        print(f"驗收：python lab/tools/card.py check {card['id']}"
              f"　｜　卡住：python lab/tools/card.py hint 1 {card['id']}（最多到 3）")
    if card.get("run"):
        print("然後執行：\n  " + "\n  ".join(card["run"]))
    print(f"成果：{card['win']}")


def status(p, track=None):
    done = p["done"]
    print(f"進度 {bar(len(done), len(CARDS))} {len(done)}/{len(CARDS)} 張　｜　連續 {streak(done)} 晚")
    ts = [track] if track else tracks()
    for t in ts:
        n = len([c for c in CARDS if track_of(c) == t])
        d = len([c for c in CARDS if track_of(c) == t and c["id"] in done])
        nxt = next_in(t, done)
        head = f"\n{t}　{d}/{n}"
        if nxt is None:
            print(head + "　這一軌做完了")
            continue
        ms, k = milestone_of(t, done)
        print(head + f"　下一張：卡 {nxt['id']}［{nxt['kind']}］{nxt['title']}")
        if ms:
            print(f"　　里程碑：{ms}（再 {k} 張）")
    if track:
        nxt = next_in(track, done)
        if nxt:
            show(nxt)
    elif len(ts) == 1 and next_in(ts[0], done):
        show(next_in(ts[0], done))
    else:
        live = [t for t in ts if next_in(t, done)]
        if live:
            print(f"\n看全文：python lab/tools/card.py {live[0]}　（或給卡號）")
        else:
            print("\n全部做完了。請 Claude 依你最近的收穫補下一批卡。")


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
    elif a and a[0] in tracks():
        status(load(), a[0])
    elif a and any(c["id"] == a[0] for c in CARDS):
        show(next(c for c in CARDS if c["id"] == a[0]))
    elif a:
        sys.exit(f"不認得「{a[0]}」。軌名：{'、'.join(tracks())}；或給卡號。")
    else:
        status(load())
