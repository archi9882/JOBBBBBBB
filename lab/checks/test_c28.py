"""卡 28 驗收：lab/mine/adr/0001-result-storage.md（只檢查結構；內容由你判斷）"""
import re
from conftest import MINE

TEXT = (MINE / "adr" / "0001-result-storage.md").read_text(encoding="utf-8")


def h2():
    return [l[3:].strip() for l in TEXT.splitlines() if l.startswith("## ")]


def test_required_sections_in_order():
    need = ["背景", "選項", "決策", "後果", "推翻條件"]
    got = [s for s in h2() if s in need]
    assert got == need, f"二級標題應依序為 {need}，目前是 {h2()}"


def test_at_least_two_options():
    sec = TEXT.split("## 選項", 1)[1].split("\n## ", 1)[0]
    assert len(re.findall(r"^### ", sec, re.M)) >= 2, "選項至少兩個（各用 ### 開頭）"


def test_has_verification_date():
    assert re.search(r"\b20\d\d-\d\d-\d\d\b", TEXT), "要寫查證日期（YYYY-MM-DD）"


def test_reversal_condition_not_empty():
    sec = TEXT.split("## 推翻條件", 1)[1].split("\n## ", 1)[0].strip()
    assert len(sec) >= 20, "推翻條件要寫具體"
