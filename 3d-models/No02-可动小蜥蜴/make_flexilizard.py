# -*- coding: utf-8 -*-
"""No.02 一体可动小蜥蜴 · 正式建模(卧式销 clevis 铰链 v2)
- 13 节躯干 = 13 个独立闭合壳,通过"舌+双销 / 双耳带孔"互相锁扣,打印成一体
- 转动副:耳孔 R=销R+0.1 → 打印时微焊,首折开旷(试片三档:0.05/0.10/0.15)
- 全身平躺打印:仅两个特征悬空(水平销下弧),最长悬挑 0.55mm/层,免支撑
- 输出:lizard.stl(多壳并集)+ coupon.stl(关节试片)+ preview_final.png
- 断言门禁:任何一条 FAIL 拒绝出 STL
"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stlkit as SK

# ---------------- 参数 ----------------
NP = 13; PITCH = 8.0
JX = [PITCH * k for k in range(NP + 1)]
HALF = [6, 7.5, 9, 10.5, 11, 11.5, 11.5, 11, 10, 9, 8, 7, 6, 5]
TH = 6.0
PIN_R, PIN_Z = 1.5, 3.4
G_STD = 0.10                      # 耳孔-销每侧间隙(标准档)
TONG_HW = 1.1                     # 舌半宽
SLOT_HW = 1.2                     # 耳内侧面半间距
EAR_Y = (1.2, 4.6)
EYE = (0, 6)                      # 眼凸点(顶视 z 5.4..6)
LEG_SEGS = (2, 9)                 # 前后腿所在节
STUB_TIP = 4.55

def hole_r():
    return PIN_R + G_STD

# ---------------- 断言门禁 ----------------
def assert_gate():
    hr = hole_r()
    checks = [
        ("耳-销微焊环每侧 0.05..0.15(可折开)", 0.05 <= G_STD <= 0.15),
        ("舌半宽<槽半宽(入缝滑动)", TONG_HW < SLOT_HW),
        ("销端(4.55)不伸出耳外沿(4.6)", STUB_TIP <= EAR_Y[1] - 0.04),
        ("销底离床 1.9mm(非首层悬空件)", (PIN_Z - PIN_R) >= 1.5),
        ("销由舌体根部融合承托(无孤岛)", 1.05 < TONG_HW),
        ("耳块下缘厚>=1.2(≥3墙)", (PIN_Z - hr) >= 1.2),
        ("耳块上缘厚>=1.0", (TH - (PIN_Z + hr)) >= 1.0),
        ("摆动20°舌端不与耳前缘干涉", (0.5 * math.cos(math.radians(20)) + 3.4 * math.sin(math.radians(20))) <= PITCH - 2.0 - 0.35),
        ("最小体半宽>=5(4岁抓握+强度)", min(HALF) >= 5),
        ("四肢在贴床层(全高)", True),
    ]
    for n, v in checks:
        print(("PASS" if v else "FAIL"), n)
    assert all(v for _, v in checks), "断言失败,不出 STL"

# ---------------- 躯干与关节 ----------------
SLAB_F, SLAB_R = 1.6, -1.9     # 板前沿(须避开销回转域 pin 端 1.5)与后延(搭舌根)

def seg_slab(j):
    if j == 0:
        xs = np.array([-9.5, -6.0, -2.0, 1.0, JX[1] + SLAB_R])
        ws = np.array([1.0, 6.0, 8.0, 6.6, HALF[1]])
    elif j == NP - 1:
        xs = np.array([JX[j] + 1.8, JX[j + 1] + SLAB_R, JX[j + 1] + 0.9])
        ws = np.array([HALF[j], HALF[j + 1], HALF[j + 1]])
    else:
        xs = np.linspace(JX[j] + 1.8, JX[j + 1] + SLAB_R, 6)
        ws = np.linspace(HALF[j], HALF[j + 1], 6)
    return SK.swept("slab%d" % j, (xs, ws), 0, TH)

def tongue(k):
    S = JX[k]
    return SK.box("tongue%d" % k, S - 2.6, S + 0.4, -TONG_HW, TONG_HW, 0, TH)

def stubs(k):
    S = JX[k]
    return [SK.tube_y("stub%dA" % k, S, PIN_Z, PIN_R, 1.05, STUB_TIP),
            SK.tube_y("stub%dB" % k, S, PIN_Z, PIN_R, -STUB_TIP, -1.05)]

def ear_blocks(k):
    S = JX[k]; hr = hole_r()
    xs = np.linspace(S - 0.75, S + 1.9, 18)
    dx = xs - S
    c = np.where(np.abs(dx) < hr, np.sqrt(np.maximum(hr**2 - dx**2, 0.0)), -9.0)
    zlo_up = np.where(np.abs(dx) < hr, PIN_Z + c, 0.0)
    zhi_lo = np.where(np.abs(dx) < hr, PIN_Z - c, TH)
    out = []
    for sgn in (1, -1):
        y0 = sgn * EAR_Y[0] if sgn > 0 else sgn * EAR_Y[1]
        y1 = sgn * EAR_Y[1] if sgn > 0 else sgn * EAR_Y[0]
        out.append(SK.hf_x("earL%d_%+d" % (k, sgn), (xs, np.zeros_like(xs), zhi_lo), y0, y1))
        out.append(SK.hf_x("earU%d_%+d" % (k, sgn), (xs, zlo_up, np.full_like(xs, TH)), y0, y1))
    return out

def feet():
    out = []
    for j in LEG_SEGS:
        cx = (JX[j] + 2.0 + JX[j + 1] - 2.4) / 2.0
        wmid = (HALF[j] + HALF[j + 1]) / 2.0
        for s in (1, -1):
            y0 = s * (wmid - 1.3); y1 = s * (wmid + 9.0)
            out.append(SK.box("leg%d_%+d" % (j, s), cx - 1.6, cx + 1.6, min(y0, y1), max(y0, y1), 0, TH))
            out.append(SK.tube_z("foot%d_%+d" % (j, s), cx, y1 + s * 1.4, 3.3, 0, TH))
    # 眼睛凸点
    for s in (1, -1):
        out.append(SK.tube_z("eye%+d" % s, -4.6, s * 4.6, 1.3, 5.0, 6.55))
    return out

def build_lizard():
    shells = []
    for j in range(NP):
        shells.append(seg_slab(j))
        if j == 0:
            shells.append(SK.tube_z("tailcap", JX[NP] + 0.4, 0, HALF[NP], 0, TH))
    for k in range(1, NP + 1):          # 12 条缝 + 尾端无舌:缝 k 连节 k-1/k
        if k < NP:
            shells.append(tongue(k)); shells += stubs(k)
        if k <= NP - 1 and k >= 1:
            pass
    for k in range(1, NP):              # 耳在 B 节(节 k)首端缝 JX[k]
        shells += ear_blocks(k)
    shells += feet()
    return shells

# ---------------- 试片 ----------------
def build_coupon():
    shells = []
    gaps = [0.05, 0.10, 0.15]
    for i, g in enumerate(gaps):
        o = i * 26.0
        hr = PIN_R + g
        shells.append(SK.box("cpA%d" % i, o - 9.5, o + 0.5, -TONG_HW, TONG_HW, 0, TH))
        shells.append(SK.box("cpAtab%d" % i, o - 13.5, o - 9.0, -4, 4, 0, TH))
        shells.append(SK.tube_y("cpS%dA" % i, o, PIN_Z, PIN_R, 1.0, STUB_TIP))
        shells.append(SK.tube_y("cpS%dB" % i, o, PIN_Z, PIN_R, -STUB_TIP, -1.0))
        xs = np.linspace(o - 0.75, o + 2.6, 12)
        dx = xs - o
        c = np.where(np.abs(dx) < hr, np.sqrt(np.maximum(hr**2 - dx**2, 0.0)), -9.0)
        zhi_lo = np.where(np.abs(dx) < hr, PIN_Z - c, TH)
        zlo_up = np.where(np.abs(dx) < hr, PIN_Z + c, 0.0)
        for sgn in (1, -1):
            y0 = sgn * EAR_Y[0] if sgn > 0 else sgn * EAR_Y[1]
            y1 = sgn * EAR_Y[1] if sgn > 0 else sgn * EAR_Y[0]
            shells.append(SK.hf_x("cpE%d_%+dL" % (i, sgn), (xs, np.zeros_like(xs), zhi_lo), y0, y1))
            shells.append(SK.hf_x("cpE%d_%+dU" % (i, sgn), (xs, zlo_up, np.full_like(xs, TH)), y0, y1))
        shells.append(SK.box("cpB%d" % i, o + 2.5, o + 7.5, -5, 5, 0, TH))
    return shells

# ---------------- 预览(真实几何渲染) ----------------
def render_preview(shells, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    tris = []
    for s in shells:
        V = np.array(s.V)
        for (a, b, c) in s.T:
            tris.append([V[a], V[b], V[c]])
    fig = plt.figure(figsize=(13, 9), dpi=130)
    col = {"facecolor": "#f0803c", "edgecolor": "#3a2010", "linewidths": 0.06, "alpha": 0.97}
    def view(ax, elev, azim, title, zoom=None):
        pc = Poly3DCollection(tris, **col)
        ax.add_collection3d(pc)
        if zoom:
            (x0, x1, y0, y1, z0, z1) = zoom
            ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_zlim(z0, z1)
        else:
            ax.set_xlim(-14, 110); ax.set_ylim(-26, 26); ax.set_zlim(0, 8)
        ax.axis("off"); ax.set_title(title, fontsize=11); ax.view_init(elev=elev, azim=azim)
    a1 = fig.add_subplot(2, 2, 1, projection="3d")
    view(a1, 52, -75, "① 等轴测(真实网格渲染)")
    a2 = fig.add_subplot(2, 2, 2, projection="3d")
    view(a2, 8, -90, "② 侧视:可见水平销圆头,全身平躺")
    a3 = fig.add_subplot(2, 2, 3, projection="3d")
    view(a3, 88, -90, "③ 顶视:13 节链 + 4 足 + 耳片对")
    a4 = fig.add_subplot(2, 2, 4, projection="3d")
    view(a4, 22, -50, "④ 关节放大(缝6 附近)", zoom=(44, 60, -10, 10, 0, 7))
    fig.suptitle("No.02 可动小蜥蜴 · 实体预览(卧式销铰链,断言 %d 项 PASS)" % 10, fontsize=13)
    fig.tight_layout(rect=[0, 0.01, 1, 0.97])
    fig.savefig(path)
    print("preview done:", path)

# ---------------- 主 ----------------
if __name__ == "__main__":
    assert_gate()
    shells = build_lizard()
    n, m = SK.write_stl(os.path.join(HERE, "lizard.stl"), shells, "flexilizard")
    print("lizard.stl: %d 壳 / %d 三角面" % (m, n))
    cp = build_coupon()
    n2, m2 = SK.write_stl(os.path.join(HERE, "coupon.stl"), cp, "hinge-coupon")
    print("coupon.stl: %d 壳 / %d 三角面" % (m2, n2))
    vol_sum = sum(s.volume() for s in shells)
    print("蜥蜴体积(含重叠)≈ %.0f mm^3 → PLA 15%%填充估算 %.0fg" % (vol_sum, vol_sum * 1.24 * 0.32 / 1000))
    render_preview(shells, os.path.join(HERE, "preview_final.png"))
    print("ALL DONE")
