"""潰壩解析解：Ritter（下游乾床）與 Stoker（下游濕床）。平底、無摩擦、初始靜止。"""
import numpy as np
from scipy.optimize import brentq

G = 9.81


def ritter(x, t, h_left, x0):
    c0 = np.sqrt(G * h_left)
    xi = (np.asarray(x) - x0) / t
    h = np.where(xi <= -c0, h_left, np.where(xi >= 2 * c0, 0.0, (2 * c0 - xi) ** 2 / (9 * G)))
    u = np.where((xi > -c0) & (xi < 2 * c0), 2.0 / 3.0 * (c0 + xi), 0.0)
    return h, u


def stoker_middle_state(h_left, h_right):
    """解中間水深 h_m：稀疏波給 u_m = 2(c_l − c_m)，激波跳躍條件給 u_m = (h_m − h_r)√(g(h_m+h_r)/(2 h_m h_r))。"""
    cl = np.sqrt(G * h_left)

    def f(hm):
        rare = 2 * (cl - np.sqrt(G * hm))
        shock = (hm - h_right) * np.sqrt(0.5 * G * (hm + h_right) / (hm * h_right))
        return rare - shock

    hm = brentq(f, h_right * (1 + 1e-12), h_left)
    um = 2 * (cl - np.sqrt(G * hm))
    S = hm * um / (hm - h_right)          # 質量守恆跨激波
    return hm, um, S


def stoker(x, t, h_left, h_right, x0):
    if h_right <= 0:
        return ritter(x, t, h_left, x0)
    cl = np.sqrt(G * h_left)
    hm, um, S = stoker_middle_state(h_left, h_right)
    cm = np.sqrt(G * hm)
    xi = (np.asarray(x) - x0) / t
    h = np.select([xi <= -cl, xi <= um - cm, xi <= S], [h_left, (2 * cl - xi) ** 2 / (9 * G), hm], h_right)
    u = np.select([xi <= -cl, xi <= um - cm, xi <= S], [0.0, 2.0 / 3.0 * (cl + xi), um], 0.0)
    return h, u
