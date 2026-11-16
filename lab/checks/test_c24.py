"""卡 24 驗收：lab/mine/k8s/deployment.yaml（只檢查內容，不需要叢集）"""
import re
import pytest
import yaml
from conftest import MINE

DOCS = [d for d in yaml.safe_load_all((MINE / "k8s" / "deployment.yaml").read_text(encoding="utf-8")) if d]


def kind(k):
    return [d for d in DOCS if d.get("kind") == k]


@pytest.fixture
def containers():
    deps = kind("Deployment")
    assert deps, "找不到 Deployment"
    cs = deps[0]["spec"]["template"]["spec"]["containers"]
    assert cs, "Deployment 沒有容器"
    return deps[0], cs


def test_has_service():
    assert kind("Service"), "找不到 Service"


def test_image_tag_pinned(containers):
    _, cs = containers
    for c in cs:
        img = c["image"]
        name = img.rsplit("/", 1)[-1]
        assert "@sha256:" in img or (":" in name and not name.endswith(":latest")), f"映像標籤未固定：{img}"


def test_requests_and_limits(containers):
    _, cs = containers
    for c in cs:
        r = c.get("resources", {})
        for part in ("requests", "limits"):
            assert {"cpu", "memory"} <= set(r.get(part, {})), f"{c['name']} 缺 resources.{part} 的 cpu 或 memory"


def test_probes(containers):
    _, cs = containers
    for c in cs:
        assert "readinessProbe" in c and "livenessProbe" in c, f"{c['name']} 缺探針"


def test_run_as_non_root(containers):
    dep, cs = containers
    pod_sc = dep["spec"]["template"]["spec"].get("securityContext", {})
    for c in cs:
        sc = {**pod_sc, **c.get("securityContext", {})}
        assert sc.get("runAsNonRoot") is True, f"{c['name']} 沒有 runAsNonRoot: true"


def test_service_selects_deployment(containers):
    dep, _ = containers
    labels = dep["spec"]["template"]["metadata"]["labels"]
    sel = kind("Service")[0]["spec"]["selector"]
    assert sel.items() <= labels.items(), "Service 的 selector 對不到 Pod 的標籤"
