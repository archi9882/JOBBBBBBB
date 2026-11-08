"""04/02 多邊形面積與有效性：手寫鞋帶公式與自相交檢查，用來否證函式庫輸出。

執行：python code/polygon.py
"""
import numpy as np


def signed_area(pts, shift=True):
    """鞋帶公式。逆時針為正。shift=True 時先減去第一個頂點，避免大座標相減的捨入誤差。"""
    p = np.asarray(pts, dtype=float)
    if shift:
        p = p - p[0]
    x, y = p[:, 0], p[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _segments_cross(p1, p2, p3, p4):
    """兩線段是否嚴格相交（不含共用端點）。"""
    d1, d2 = _cross(p3, p4, p1), _cross(p3, p4, p2)
    d3, d4 = _cross(p1, p2, p3), _cross(p1, p2, p4)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def self_intersections(pts):
    """O(n²) 檢查：回傳互相交叉的非相鄰邊對。"""
    p = [tuple(map(float, q)) for q in pts]
    n, hits = len(p), []
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue                      # 相鄰邊共用頂點，不算
            if _segments_cross(p[i], p[(i + 1) % n], p[j], p[(j + 1) % n]):
                hits.append((i, j))
    return hits


SQUARE = [(0, 0), (2, 0), (2, 2), (0, 2)]
L_SHAPE = [(0, 0), (3, 0), (3, 1), (1, 1), (1, 3), (0, 3)]
BOWTIE = [(0, 0), (1, 1), (1, 0), (0, 1)]
# TWD97 量級的座標（m）：一個 100 m × 100 m 的正方形，平移到台灣附近
FAR = [(250000.1 + x * 50, 2650000.3 + y * 50) for x, y in SQUARE]


def irregular_polygon(seed=0, n=12):
    """約 1–3 m² 的不規則星形多邊形（以原點為中心），用來測大座標下的捨入誤差。"""
    rng = np.random.default_rng(seed)
    th = np.sort(rng.uniform(0, 2 * np.pi, n))
    r = rng.uniform(0.5, 1.0, n)
    return np.c_[r * np.cos(th), r * np.sin(th)]

TWD97_OFFSET = (250000.123, 2650000.456)

if __name__ == "__main__":
    for name, poly in [("正方形", SQUARE), ("L 形", L_SHAPE), ("蝴蝶結", BOWTIE), ("TWD97 量級", FAR)]:
        print(f"{name:8s} 面積 {signed_area(poly):12.6f}  自相交 {self_intersections(poly)}")
    print("順時針正方形面積", signed_area(SQUARE[::-1]))
    loc = irregular_polygon(); A = signed_area(loc); far = loc + TWD97_OFFSET
    print(f"不規則多邊形 {A:.12f} m²；平移到 TWD97 量級後誤差：未減原點 {signed_area(far, shift=False)-A:.2e}，減原點 {signed_area(far)-A:.2e}")
    try:
        from shapely.geometry import Polygon
        b = Polygon(BOWTIE)
        print(f"shapely 蝴蝶結：area={b.area}  is_valid={b.is_valid}")
    except ImportError:
        print("（未安裝 shapely，略過對照）")
