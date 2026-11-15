"""卡 19 驗收（靜態檢查）：lab/mine/Dockerfile。真正的驗收是你自己 docker build 並跑起來。"""
import re
from pathlib import Path
import pytest

from conftest import MINE


@pytest.fixture
def text():
    p = MINE / "Dockerfile"
    assert p.exists(), "lab/mine/Dockerfile 不存在"
    return p.read_text()


def lines(text):
    return [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]


def test_base_image_is_pinned(text):
    froms = [l.split()[1] for l in lines(text) if l.upper().startswith("FROM ")]
    assert froms
    for img in froms:
        assert ":" in img and not img.endswith(":latest") or "@sha256:" in img, f"基底映像沒有固定版本：{img}"


def test_runs_as_non_root(text):
    users = [l.split()[1] for l in lines(text) if l.upper().startswith("USER ")]
    assert users and users[-1] not in ("root", "0"), "最後一個 USER 必須是非 root"


def test_has_healthcheck(text):
    assert any(l.upper().startswith("HEALTHCHECK") for l in lines(text))


def test_dockerignore_keeps_outputs_out():
    p = MINE / ".dockerignore"
    assert p.exists(), "缺 lab/mine/.dockerignore"
    t = p.read_text()
    assert re.search(r"^/?(\*\*/)?runs/?$", t, re.M) and re.search(r"^/?(\*\*/)?\.git/?$", t, re.M)


def test_apt_cache_cleaned(text):
    if "apt-get install" in text:
        assert "rm -rf /var/lib/apt/lists" in text
