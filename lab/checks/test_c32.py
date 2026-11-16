"""卡 32 驗收：docs/falsification-casebook.md（只檢查結構）"""
import re
from conftest import ROOT

TEXT = (ROOT / "docs" / "falsification-casebook.md").read_text(encoding="utf-8")
LABELS = ["**AI 的說法**", "**可檢驗的預測**", "**驗證方法**", "**結果**"]


def cases():
    parts = re.split(r"^### ", TEXT, flags=re.M)[1:]
    return parts


def test_at_least_five_cases():
    assert len(cases()) >= 5, f"目前 {len(cases())} 個案例，至少要 5 個"


def test_each_case_has_four_labels():
    for c in cases():
        title = c.splitlines()[0]
        missing = [l for l in LABELS if l not in c]
        assert not missing, f"案例「{title}」缺 {missing}"
