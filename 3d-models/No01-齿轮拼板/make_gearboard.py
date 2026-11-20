# -*- coding: utf-8 -*-
"""No.01 齿轮拼板(儿童4岁向)参数化生成器
- 底板 180x60x6mm:上下长边各11个半圆卡槽(槽R2.75,间距12mm网格),圆角R8
- 齿轮 16T/24T:真实渐开线齿(m=3, PA20deg, 侧隙0.4mm),盘厚10mm,卡柄 D5x8mm
- 啮合对:同行 16+16=48 / 16+24=60 / 24+24=72(=网格整数倍);同列跨板=60(16+24)
- 直写二进制STL;自检:水密(每条无向边恰2次且方向相反)+ 体积对账(误差<2%)
用法: python -I make_gearboard.py   ;改需求改头部常量重跑。
"""
import math, os, struct
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))

M = 3.0          # 模数
PA = math.radians(20.0)
BACKLASH = 0.4   # 齿侧总间隙 mm
GT = 10.0        # 齿轮盘厚
STEM_D, STEM_H = 5.0, 8.0
PLATE_L, PLATE_W, PLATE_T = 180.0, 60.0, 6.0
NOTCH_R = STEM_D / 2 + 0.25          # 每侧0.25mm旋转间隙
XS = [30.0 + 12.0 * i for i in range(11)]   # 11槽/边:30..150
RC = 8.0

def inv(a): return math.tan(a) - a

# ---------------- 齿形轮廓 ----------------
def gear_profile(z, rot_deg=0.0):
    rp = M * z / 2.0; rb = rp * math.cos(PA); ra = rp + M; rf = rp - 1.25 * M
    bk = BACKLASH / (2.0 * rp)
    def psi(r):
        r = max(r, rb)
        return math.pi / (2 * z) + inv(PA) - inv(math.acos(rb / r)) - bk
    psi_b, psi_a = psi(rb), psi(ra)
    radial = rf < rb - 1e-9
    rs = max(rf, rb)
    pts = []
    nS, nT, nR = 6, 3, 3
    for k in range(z):
        th = k * 2 * math.pi / z
        if radial: pts.append((rf, th + psi_b))
        for r in np.linspace(rs, ra, nS): pts.append((r, th + psi(r)))
        for t in np.linspace(psi_a, -psi_a, nT): pts.append((ra, th + t))
        for r in np.linspace(ra, rs, nS): pts.append((r, th - psi(r)))
        if radial: pts.append((rf, th - psi_b))
        nxt = (k + 1) * 2 * math.pi / z
        a0 = th - (psi_b if radial else psi(rf))
        a1 = nxt + (psi_b if radial else psi(rf))
        for t in np.linspace(a0, a1, nR + 2)[1:-1]: pts.append((rf, t))
    off = math.radians(rot_deg)
    cart = [(r * math.cos(a + off), r * math.sin(a + off)) for r, a in pts]
    ded = []
    for p in cart:
        if not ded or abs(p[0] - ded[-1][0]) > 1e-9 or abs(p[1] - ded[-1][1]) > 1e-9:
            ded.append(p)
    while len(ded) > 1 and abs(ded[0][0] - ded[-1][0]) < 1e-9 and abs(ded[0][1] - ded[-1][1]) < 1e-9:
        ded.pop()
    return np.array(ded)

# ---------------- 底板轮廓 ----------------
def plate_contour():
    L, W, rc, rn = PLATE_L, PLATE_W, RC, NOTCH_R
    P = []
    def arc(cx, cy, r, t0, t1, n):
        for t in np.linspace(t0, t1, n):
            P.append((cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t))))
    P.append((rc, 0.0))
    for x in XS:                       # 下边 +x:半圆槽向板内咬(y>=0 的半圆)
        arc(x, 0.0, rn, 180, 0, 13)    # 弧自带端点 (x-rn,0)->(x+rn,0)
    P.append((L - rc, 0.0)); arc(L - rc, rc, rc, -90, 0, 5)
    P.append((L, W - rc)); arc(L - rc, W - rc, rc, 0, 90, 5)
    for x in reversed(XS):             # 上边 -x
        arc(x, W, rn, 0, 180, 13)      # 弧自带端点 (x+rn,W)->(x-rn,W)
    P.append((rc, W)); arc(rc, W - rc, rc, 90, 180, 5)
    P.append((0.0, rc)); arc(rc, rc, rc, 180, 270, 5)
    ded = []                            # 防御性去重连续重合点
    for p in P:
        if not ded or abs(p[0] - ded[-1][0]) > 1e-12 or abs(p[1] - ded[-1][1]) > 1e-12:
            ded.append(p)
    while len(ded) > 1 and abs(ded[0][0] - ded[-1][0]) < 1e-12 and abs(ded[0][1] - ded[-1][1]) < 1e-12:
        ded.pop()
    return np.array(ded)

def signed_area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)

def circle_ring(R, n, cx=0.0, cy=0.0):
    return np.array([(cx + R * math.cos(2 * math.pi * i / n),
                      cy + R * math.sin(2 * math.pi * i / n)) for i in range(n)])

# ---------------- 网格 ----------------
class Mesh:
    def __init__(self): self.V, self.T = [], []
    def v(self, x, y, z): self.V.append((x, y, z)); return len(self.V) - 1
    def tri(self, a, b, c): self.T.append((a, b, c))

def earcut(P):
    """简单多边形耳切, P CCW -> 三角形(顶点索引,保绕向)"""
    P = np.asarray(P, float)
    idx = list(range(len(P))); tris = []
    def cross3(p, q, r): return np.cross(q - p, r - q)
    def convex(i):
        n = len(idx)
        return cross3(P[idx[(i - 1) % n]], P[idx[i]], P[idx[(i + 1) % n]]) > 1e-9
    def strictly_inside(pt, a, b, c):
        d1 = np.cross(b - a, pt - a); d2 = np.cross(c - b, pt - b); d3 = np.cross(a - c, pt - c)
        return (d1 > 1e-9 and d2 > 1e-9 and d3 > 1e-9) or (d1 < -1e-9 and d2 < -1e-9 and d3 < -1e-9)
    while len(idx) > 3:
        n = len(idx); cut = False
        for o in range(n):
            i, j, k = o, (o + 1) % n, (o + 2) % n
            if not convex(j): continue        # 耳尖=中点 j(两腰为边界边),须凸
            a, b, c = P[idx[i]], P[idx[j]], P[idx[k]]
            if np.cross(b - a, c - a) < 1e-9: continue
            bad = False
            for q in idx:
                if q == idx[i] or q == idx[j] or q == idx[k]: continue
                if strictly_inside(P[q], a, b, c): bad = True; break
            if bad: continue
            tris.append((idx[i], idx[j], idx[k])); idx.pop(j); cut = True; break
        if not cut:
            raise RuntimeError("earcut 卡住(轮廓自交?)")
    tris.append((idx[0], idx[1], idx[2]))
    return tris

def check_and_write(mesh, path, expect_vol, label):
    T = mesh.T
    seen = set()
    for (a, b, c) in T:
        for u, w in ((a, b), (b, c), (c, a)):
            if (u, w) in seen:
                raise RuntimeError("%s: 同向重复边 %s" % (label, (u, w)))
            seen.add((u, w))
    cnt = {}
    for (a, b, c) in T:
        for u, w in ((a, b), (b, c), (c, a)):
            k = (min(u, w), max(u, w)); cnt[k] = cnt.get(k, 0) + 1
    bad = [k for k, v in cnt.items() if v != 2]
    if bad: raise RuntimeError("%s: 破洞/悬挂边 %d 条" % (label, len(bad)))
    V = np.array(mesh.V, float); Ta = np.array(T)
    vol = np.sum(np.einsum('ij,ij->i', V[Ta[:, 0]], np.cross(V[Ta[:, 1]], V[Ta[:, 2]]))) / 6.0
    if vol < 0: raise RuntimeError("%s: 法向整体朝内" % label)
    err = abs(vol - expect_vol) / expect_vol
    if err > 0.02: raise RuntimeError("%s 体积对账失败 %.1f vs %.1f" % (label, vol, expect_vol))
    va, vb, vc = V[Ta[:, 0]], V[Ta[:, 1]], V[Ta[:, 2]]
    n = np.cross(vb - va, vc - va)
    ln = np.linalg.norm(n, axis=1, keepdims=True); ln[ln == 0] = 1
    n = (n / ln).astype(np.float32)
    buf = np.zeros((len(Ta), 12), dtype=np.float32)
    buf[:, 0:3] = n; buf[:, 3:6] = va; buf[:, 6:9] = vb.astype(np.float32); buf[:, 9:12] = vc
    with open(path, "wb") as f:
        f.write(struct.pack("<80sI", ("gearboard " + label).encode("gbk", "ignore")[:80], len(Ta)))
        rec = np.hstack([np.frombuffer(buf.tobytes(), np.uint8).reshape(len(Ta), 48),
                         np.zeros((len(Ta), 2), np.uint8)])  # 每面补 2 字节属性计数 = 50 字节
        f.write(rec.tobytes())
    print("%s: %d 面, 水密OK 体积 %.1f mm^3 (目标 %.1f, 差 %.2f%%)" % (label, len(Ta), vol, expect_vol, err * 100))
    return len(Ta)

def prism(m, poly, z0, z1):
    n = len(poly)
    assert signed_area(poly) > 0, "轮廓需CCW"
    rb0 = [m.v(x, y, z0) for x, y in poly]
    rb1 = [m.v(x, y, z1) for x, y in poly]
    for (a, b, c) in earcut(poly):
        m.tri(rb0[a], rb0[c], rb0[b]); m.tri(rb1[a], rb1[b], rb1[c])
    for i in range(n):
        a, b = i, (i + 1) % n
        m.tri(rb0[a], rb0[b], rb1[b]); m.tri(rb0[a], rb1[b], rb1[a])

def build_gear(z, fname):
    prof = gear_profile(z); N = len(prof); rs = STEM_D / 2
    m = Mesh(); z0, z1, z2 = 0.0, GT, GT + STEM_H
    cb = m.v(0, 0, z0)
    r0 = [m.v(x, y, z0) for x, y in prof]
    r1 = [m.v(x, y, z1) for x, y in prof]
    for i in range(N):
        m.tri(cb, r0[(i + 1) % N], r0[i])                  # 底 -z
    for i in range(N):
        a, b = i, (i + 1) % N
        m.tri(r0[a], r0[b], r1[b]); m.tri(r0[a], r1[b], r1[a])   # 盘壁
    inA = circle_ring(rs, N)
    ri = [m.v(x, y, z1) for x, y in inA]
    for i in range(N):
        a, b = i, (i + 1) % N
        m.tri(r1[a], r1[b], ri[b]); m.tri(r1[a], ri[b], ri[a])   # 顶环
    top = circle_ring(rs, N)
    rt = [m.v(x, y, z2) for x, y in top]
    for i in range(N):
        a, b = i, (i + 1) % N
        m.tri(ri[a], ri[b], rt[b]); m.tri(ri[a], rt[b], rt[a])   # 柄壁
    ct = m.v(0, 0, z2)
    for i in range(N):
        m.tri(ct, rt[i], rt[(i + 1) % N])                  # 柄盖 +z
    expect = float(abs(signed_area(prof))) * GT + math.pi * rs * rs * STEM_H
    return check_and_write(m, os.path.join(OUT, fname), expect, "齿轮%dT" % z)

def build_plate(fname):
    poly = plate_contour()
    m = Mesh(); prism(m, poly, 0.0, PLATE_T)
    expect = float(abs(signed_area(poly))) * PLATE_T
    return check_and_write(m, os.path.join(OUT, fname), expect, "底板")

# ---------------- 预览 ----------------
def render_preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as Poly2D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    fig = plt.figure(figsize=(13, 9), dpi=140)

    ax = fig.add_subplot(2, 2, 1)
    ax.add_patch(Poly2D(plate_contour(), closed=True, facecolor="#d9e2ec", edgecolor="#37653c", lw=1.6))
    cols = {16: "#e8590c", 24: "#1971c2"}
    # 下排 16-24-16(间距60,全啮合);上排 24-16-24(间距60);同列 x=30/150 处 16+24 隔板啮合
    gears = [(30, 0, 16), (90, 0, 24), (150, 0, 16), (30, 60, 24), (90, 60, 16), (150, 60, 24)]
    PHASE = {16: 0.0, 24: 7.5}   # 24T 转半齿距,使 60mm 啮合位呈"齿尖进齿槽"正确相位
    for cx, cy, z in gears:
        g = gear_profile(z, PHASE[z]) + np.array([cx, cy])
        ax.add_patch(Poly2D(g, closed=True, facecolor=cols[z], alpha=0.85, ec="k", lw=0.5))
        ax.add_patch(Poly2D(circle_ring(STEM_D / 2 + 0.4, 24, cx, cy), closed=True, facecolor="white", ec="k"))
    for x in XS:
        for y in (0.0, 60.0):
            ax.plot(x, y, "k.", ms=3)
    ax.set_xlim(-10, 190); ax.set_ylim(-42, 102); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("组装顶视图:每对相邻齿轮均满足啮合中心距(16+24=60)", fontsize=10)

    def gear_faces(z):
        prof = gear_profile(z); N = len(prof); rs = STEM_D / 2
        z1, z2 = GT, GT + STEM_H
        top = circle_ring(rs, N); f = []
        for i in range(N):
            a, b = i, (i + 1) % N
            pa, pb = prof[a], prof[b]; ta, tb = top[a], top[b]
            f.append([(0, 0, 0), (pb[0], pb[1], 0), (pa[0], pa[1], 0)])
            f.append([(pa[0], pa[1], 0), (pb[0], pb[1], 0), (pb[0], pb[1], z1)])
            f.append([(pa[0], pa[1], 0), (pb[0], pb[1], z1), (pa[0], pa[1], z1)])
            f.append([(pa[0], pa[1], z1), (pb[0], pb[1], z1), (tb[0], tb[1], z1)])
            f.append([(pa[0], pa[1], z1), (tb[0], tb[1], z1), (ta[0], ta[1], z1)])
            f.append([(ta[0], ta[1], z1), (tb[0], tb[1], z1), (tb[0], tb[1], z2)])
            f.append([(ta[0], ta[1], z1), (tb[0], tb[1], z2), (ta[0], ta[1], z2)])
            f.append([(0, 0, z2), (ta[0], ta[1], z2), (tb[0], tb[1], z2)])
        return f
    for pos, z, ttl, col in ((2, 16, "16T 齿轮 x4", "#f7b267"), (3, 24, "24T 齿轮 x3", "#74c0fc")):
        a = fig.add_subplot(2, 2, pos, projection="3d")
        a.add_collection3d(Poly3DCollection(gear_faces(z), facecolor=col, edgecolor="k", lw=0.08, alpha=0.96))
        a.set_xlim(-42, 42); a.set_ylim(-42, 42); a.set_zlim(0, 18)
        a.axis("off"); a.set_title(ttl + "(渐开线齿 m=3)"); a.view_init(elev=30, azim=-60)

    poly = plate_contour(); N = len(poly); f = []
    t2 = earcut(poly)
    for (a, b, c) in t2:
        f.append([tuple(poly[a]) + (PLATE_T,), tuple(poly[b]) + (PLATE_T,), tuple(poly[c]) + (PLATE_T,)])
        f.append([tuple(poly[a]) + (0.0,), tuple(poly[c]) + (0.0,), tuple(poly[b]) + (0.0,)])
    for i in range(N):
        j = (i + 1) % N
        f.append([tuple(poly[i]) + (0.0,), tuple(poly[j]) + (0.0,), tuple(poly[j]) + (PLATE_T,)])
        f.append([tuple(poly[i]) + (0.0,), tuple(poly[j]) + (PLATE_T,), tuple(poly[i]) + (PLATE_T,)])
    ax3 = fig.add_subplot(2, 2, 4, projection="3d")
    ax3.add_collection3d(Poly3DCollection(f, facecolor="#b2f2bb", edgecolor="k", lw=0.08, alpha=0.96))
    ax3.set_xlim(-5, 185); ax3.set_ylim(-5, 65); ax3.set_zlim(0, 10)
    ax3.axis("off"); ax3.set_title("底板 180x60x6(22 槽,网格12mm)"); ax3.view_init(elev=40, azim=-65)

    fig.suptitle("No.01 齿轮拼板 · 预览(4岁款)", fontsize=13)
    try:
        fig.tight_layout(rect=[0, 0, 1, 0.97])
    except TypeError:
        fig.set_layout_engine  # mpl3.0 无 rect 参数时直接画
    fig.savefig(os.path.join(OUT, "preview.png"))
    print("preview.png done")

if __name__ == "__main__":
    build_gear(16, "gear16T.stl")
    build_gear(24, "gear24T.stl")
    build_plate("baseplate.stl")
    render_preview()
    print("ALL DONE ->", OUT)
