# -*- coding: utf-8 -*-
"""stlkit — 脚本建模共享库(No.01 齿轮验证过的自检基建抽取版)
- Mesh:顶点+三角形收集;loft:沿站点的闭合截面扫掠(体侧壁+两端盖)
- 原语:box / tube_y / tube_z / swept(半宽函数)/ hf_x(变高块)
- check:逐壳体水密(每条无向边恰2次)+ 体积符号;多壳装配写一个 STL(切片器自动并)
所有原语都是独立闭合壳;相互重叠 0.1mm 实现"打印后为一整块"的并集效果。
"""
import struct
import numpy as np


class Shell:
    def __init__(self, name=""):
        self.name = name
        self.V = []   # list of (x,y,z)
        self.T = []   # list of (i,j,k)

    def v(self, x, y, z):
        self.V.append((x, y, z))
        return len(self.V) - 1

    def tri(self, a, b, c):
        self.T.append((a, b, c))

    def volume(self):
        V = np.array(self.V, float); T = np.array(self.T, int)
        return float(np.sum(np.einsum('ij,ij->i', V[T[:, 0]], np.cross(V[T[:, 1]], V[T[:, 2]]))) / 6.0)

    def watertight(self):
        cnt = {}
        for (a, b, c) in self.T:
            for u, w in ((a, b), (b, c), (c, a)):
                cnt[(min(u, w), max(u, w))] = cnt.get((min(u, w), max(u, w)), 0) + 1
        return all(v == 2 for v in cnt.values())

    def seal(self):
        """闭合检查 + 法向统一朝外(体积为负则翻转)"""
        if not self.watertight():
            raise RuntimeError("shell %s 不水密" % self.name)
        vol = self.volume()
        if vol < 0:
            self.T = [(a, c, b) for (a, b, c) in self.T]
            vol = -vol
        if vol < 1e-6:
            raise RuntimeError("shell %s 体积为零" % self.name)
        return vol


def loft(name, loops):
    """loops: [(N,3) 站点...];相邻站点等点数截面扫掠成闭合壳。截面须凸(端盖用扇形)"""
    s = Shell(name)
    idx = []
    for lp in loops:
        row = [s.v(*p) for p in lp]
        idx.append(row)
    n = len(idx[0])
    for i in range(len(idx) - 1):
        for k in range(n):
            a, b = idx[i][k], idx[i][(k + 1) % n]
            c, d = idx[i + 1][(k + 1) % n], idx[i + 1][k]
            s.tri(a, b, c); s.tri(a, c, d)
    for k in range(1, n - 1):
        s.tri(idx[0][0], idx[0][k + 1], idx[0][k])
        s.tri(idx[-1][0], idx[-1][k], idx[-1][k + 1])
    s.seal()
    return s


def box(name, x0, x1, y0, y1, z0, z1):
    def ring(x):
        return np.column_stack([np.full(4, x),
                                np.array([y0, y1, y1, y0], float),
                                np.array([z0, z0, z1, z1], float)])
    return loft(name, [ring(x0), ring(x1)])


def tube_y(name, cx, cz, r, y0, y1, nseg=24):
    th = np.arange(nseg) * 2 * np.pi / nseg
    xs, zs = cx + r * np.cos(th), cz + r * np.sin(th)
    return loft(name, [np.column_stack([xs, np.full(nseg, y0), zs]),
                       np.column_stack([xs, np.full(nseg, y1), zs])])


def tube_z(name, cx, cy, r, z0, z1, nseg=24):
    th = np.arange(nseg) * 2 * np.pi / nseg
    xs, ys = cx + r * np.cos(th), cy + r * np.sin(th)
    return loft(name, [np.column_stack([xs, ys, np.full(nseg, z0)]),
                       np.column_stack([xs, ys, np.full(nseg, z1)])])


def swept(name, x_of_w, z0, z1, n=24):
    """沿 X 扫掠半宽 w(x) 的矩形截面; x_of_w: 返回 (xs 递增) 后由调用方给 w 数组"""
    xs, ws = x_of_w
    loops = []
    for x, w in zip(xs, ws):
        loops.append(np.column_stack([np.full(4, x),
                                      np.array([-w, w, w, -w]),
                                      np.array([z0, z0, z1, z1])]))
    return loft(name, loops)


def hf_x(name, x_of_z, y0, y1, n=24):
    """沿 X 的变高块:截面 y∈[y0,y1], z∈[zlo(x), zhi(x)]"""
    xs, zlo, zhi = x_of_z
    loops = []
    for x, zl, zh in zip(xs, zlo, zhi):
        assert zh - zl > 1e-4, "薄壁 %s @x=%.2f" % (name, x)
        loops.append(np.column_stack([np.full(4, x),
                                      np.array([y0, y1, y1, y0]),
                                      np.array([zl, zl, zh, zh])]))
    return loft(name, loops)


def write_stl(path, shells, header="stlkit"):
    """多壳并集写 binary STL(每壳独立闭合,重叠合并交给切片器)"""
    Voff, T, N = 0, [], 0
    verts = []
    for s in shells:
        vol = s.seal() if not getattr(s, "_sealed", False) else None
        s._sealed = True
        for (a, b, c) in s.T:
            T.append((a + Voff, b + Voff, c + Voff))
        verts.extend(s.V)
        Voff += len(s.V)
        N += len(s.T)
    V = np.array(verts, dtype=np.float32)
    Ta = np.array(T)
    va, vb, vc = V[Ta[:, 0]], V[Ta[:, 1]], V[Ta[:, 2]]
    nrm = np.cross(vb - va, vc - va)
    ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
    nrm = nrm / ln
    buf = np.zeros((N, 12), dtype=np.float32)
    buf[:, 0:3] = nrm; buf[:, 3:6] = va; buf[:, 6:9] = vb; buf[:, 9:12] = vc
    with open(path, "wb") as f:
        f.write(struct.pack("<80sH", header.encode("ascii", "ignore")[:80], N))
        f.write(buf.tobytes())
    return N, len(shells)
