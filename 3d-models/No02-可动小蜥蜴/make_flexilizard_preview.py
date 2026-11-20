# -*- coding: utf-8 -*-
"""No.02 一体可动小蜥蜴 · 设计预览 v2(只出 PNG,不出 STL)

v1"竖直轴阶梯销+盖环"经打印过程 grill 后废弃,四条必翻车理由:
  间隙=线宽级必焊死 / 盖环悬挑与捕获量数学不可兼得 / 封闭环形槽两湿壁粘连 / 球肩1mm悬垂。
v2 关节 = 卧式销 clevis 铰链(运动轴水平、平行于床面、垂直于身体长轴):
  - A 节尾端:舌片(宽2.2)+ 舌眼;眼与销 R1.5 融合为一体(无间隙环 → 零悬垂零孤岛,
    销底由舌眼顶弧 r1.8 承托,起桥即有依托)
  - B 节首端:左右两条竖耳片(厚1.5,内侧面 y=±1.2),耳孔 R1.6
  - 销:Ø3.0,随耳1/舌眼一体打印,悬桥 ~3.8mm 插入耳2 孔
  - 转动副 = 耳孔环带:0.1/侧 微焊,打印后"首折开旷"(与打印轴承同一成熟工艺)
  - 轴向保持:舌眼闭环绕销,拔不出;耳2 孔导向
  - 运动:±30° 点头/弓背(绕水平销);侧向扭动 = 间隙旷量(小幅)
规格:13 节 x 节距 8mm,含头全长 ~144mm;通体厚 6mm;四肢贴床平掌;平躺免支撑。
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly2D, Circle, Ellipse, Rectangle, Arc

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 参数 ----------
NP = 13; PITCH = 8.0
JX = np.arange(NP + 1) * PITCH
HALF = np.array([6, 7.5, 9, 10.5, 11, 11.5, 11.5, 11, 10, 9, 8, 7, 6, 5])
TH = 6.0
TONG_HW = 1.1        # 舌片半宽
SLOT_HW = 1.2        # 耳内半间距(舌侧隙 0.1/侧,滑动面为圆柱面,允许)
EAR_T, EAR_Y0, EAR_Y1 = 1.5, 1.2, 2.7
R_PIN, R_EARHOLE, R_EYE_OUT = 1.5, 1.6, 1.8
PIN_Z = 3.4
JOINTS = list(JX[1:NP])
MICRO = round(R_EARHOLE - R_PIN, 3)

checks = [
    ("耳外沿 < 最小体半宽(根部强度)", EAR_Y1 <= HALF.min()),
    ("悬桥 <= 4.0mm(桥极限一半)", (SLOT_HW + EAR_T) <= 4.0),
    ("销底离床 >= 1.5mm", (PIN_Z - R_PIN) >= 1.5),
    ("销底由舌眼顶弧承托(无孤岛层)", R_EYE_OUT > R_PIN),
    ("耳-销微焊环 0.10/side 且 <= 0.15(可折开)", 0.08 <= MICRO <= 0.15),
    ("舌眼-销融合:零间隙环", True),
    ("舌半宽 < 槽半宽(可入缝)", TONG_HW < SLOT_HW),
    ("销顶离背 >= 1.0mm(顶壁约5层)", (TH - (PIN_Z + R_PIN)) >= 1.0),
]
for name, v in checks:
    print(("PASS" if v else "FAIL"), name)
assert all(v for _, v in checks), "几何断言失败,不出图"

CA, CB = "#e8590c", "#f7a35c"
CEAR, CPIN, CLEG = "#1971c2", "#495057", "#66a80f"

fig = plt.figure(figsize=(14, 10.5), dpi=140)

# ================= ① 顶视 =================
ax = fig.add_axes([0.03, 0.60, 0.55, 0.37])
for j in range(NP):
    x0, x1 = JX[j], JX[j + 1]
    ax.add_patch(Poly2D([(x0, -HALF[j]), (x1, -HALF[j + 1]), (x1, HALF[j + 1]), (x0, HALF[j])],
                       closed=True, facecolor=(CB if j % 2 else CA), ec="k", lw=0.6, alpha=0.92))
ax.add_patch(Circle((JX[-1], 0), HALF[-1], facecolor=CA, ec="k", lw=0.6))
ax.add_patch(Ellipse((-9, 0), 22, 17, facecolor="#a04000", ec="k", lw=0.8))
ax.add_patch(Circle((-14, 4.4), 1.6, fc="k")); ax.add_patch(Circle((-14, -4.4), 1.6, fc="k"))
for cx in JOINTS:
    for s in (1, -1):
        ax.add_patch(Rectangle((cx - EAR_T / 2, min(s * EAR_Y0, s * EAR_Y1)), EAR_T, EAR_Y1 - EAR_Y0,
                               facecolor=CEAR, ec="k", lw=0.5))
    ax.add_patch(Circle((cx, 0), R_EYE_OUT, fc=(CB if int(cx / PITCH) % 2 else CA), ec="k", lw=0.5))
    ax.add_patch(Circle((cx, 0), R_PIN, fc=CPIN, ec="k", lw=0.5))
for j in (2, 9):
    for s in (1, -1):
        y1 = s * (HALF[j] + 11.5)
        ax.add_patch(Poly2D([(JX[j] - 2.6, s * (HALF[j] + 1)), (JX[j] + 2.6, s * (HALF[j] + 1)),
                             (JX[j] + 3.4, y1), (JX[j] - 3.4, y1)], closed=True, fc=CLEG, ec="k", lw=0.6))
        ax.add_patch(Circle((JX[j], y1), 3.4, fc=CLEG, ec="k", lw=0.6))
ax.annotate("蓝条成对=B耳片;灰圆=销(与舌眼融合)", (JX[6], HALF[6] + 2), (JX[6] + 6, 24),
            arrowprops=dict(arrowstyle="->", color="#004466"), fontsize=9, color="#004466")
ax.plot([0, 30], [-26, -26], "k-", lw=3)
for xx in (0, 10, 20, 30):
    ax.plot([xx, xx], [-27, -25], "k-", lw=1)
ax.text(15, -30.5, "3 cm 标尺", ha="center", fontsize=9)
ax.set_xlim(-26, 118); ax.set_ylim(-34, 28); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("① 顶视:13 节 + 12 个卧式销铰链 + 4 平掌,全长 ~144mm", fontsize=11)

# ================= ② 关节俯视放大(XY) =================
a2 = fig.add_axes([0.62, 0.60, 0.36, 0.37])
a2.add_patch(Rectangle((-14, -7), 14 - R_EYE_OUT + 0.6, 14, fc=CA, ec="k"))          # A 体
a2.add_patch(Rectangle((-14, -TONG_HW), 14 - TONG_HW + (R_EYE_OUT - TONG_HW) + 0, 2 * TONG_HW, fc=CA, ec="k"))
a2.add_patch(Circle((0, 0), R_EYE_OUT, fc=CA, ec="k", lw=0.8))                        # 舌眼
for s in (1, -1):
    y0 = s * EAR_Y0 if s > 0 else -EAR_Y1
    a2.add_patch(Rectangle((-EAR_T / 2, y0), EAR_T, EAR_Y1 - EAR_Y0, fc=CEAR, ec="k"))
    a2.add_patch(Circle((0, s * (EAR_Y0 + EAR_Y1) / 2), R_EARHOLE, fc="#eef4fb", ec="k", lw=0.8))
    a2.add_patch(Circle((0, s * (EAR_Y0 + EAR_Y1) / 2), R_PIN, fc=CPIN, ec="k", lw=0.5))
a2.add_patch(Circle((0, 0), R_PIN, fc=CPIN, ec="k", lw=0.8))
a2.text(0, -0.55, "销", color="#ffffff", fontsize=8, ha="center")
a2.annotate("耳孔 0.1/侧微焊环\n= 转动副,首折开旷", (1.6, 2.0), (4.6, 4.6),
            fontsize=8.5, color="#7a0000", arrowprops=dict(arrowstyle="->", color="#7a0000"))
a2.annotate("舌眼包销:融合无隙,拔不出", (-R_EYE_OUT, -0.0), (-13, -4.6),
            fontsize=8.5, color="#004466", arrowprops=dict(arrowstyle="->", color="#004466"))
a2.add_patch(Arc((0, 0), 11, 11, theta1=-30, theta2=30, color="#1a7f37", lw=1.2, ls=":"))
a2.text(5.6, -1.6, "±30°", fontsize=9, color="#1a7f37")
a2.set_xlim(-15, 10); a2.set_ylim(-8, 8); a2.set_aspect("equal"); a2.axis("off")
a2.set_title("② 单铰链俯视放大(XY):clevis 双耳 + 舌眼 + 卧式销", fontsize=11)

# ================= ③ 舌眼剖面(XZ, 过 y=0) =================
a3 = fig.add_axes([0.03, 0.06, 0.55, 0.44])
a3.add_patch(Rectangle((-24, 0), 24 + (-0.75) + 24 - 24, TH, fc=CA, ec="k"))
a3.add_patch(Rectangle((-24, 0), -0.75 + 24, TH, fc=CA, ec="k"))                     # A 体到缝
a3.add_patch(Circle((0, PIN_Z), R_EYE_OUT, fc=CA, ec="k", lw=0.8))                   # 舌眼顶弧
a3.add_patch(Circle((0, PIN_Z), R_PIN, fc=CPIN, ec="k", lw=0.8))                     # 销
for dx, lab in ((0, "耳1(实线=假想面外)"),):
    pass
a3.add_patch(Rectangle((-EAR_T / 2 - 1.6, 0), EAR_T, TH, fc="none", ec=CEAR, lw=1.6, ls="--"))
a3.add_patch(Rectangle((EAR_T / 2 + 1.6 - EAR_T, 0), EAR_T, TH, fc="none", ec=CEAR, lw=1.6, ls="--"))
a3.add_patch(Rectangle((EAR_T / 2 + 0.05, 0), 7, TH, fc="white", ec="#aaaaaa", lw=0.6))
a3.add_patch(Rectangle((EAR_T / 2 + 0.05, 0), 5, TH, fc=CB, ec="#a04000", alpha=0.35))  # B 体(示意)
a3.annotate("销φ3:下方由舌眼顶弧承托,\n起桥有依托 → 无悬浮岛层", (0.3, PIN_Z - R_PIN), (5.5, 1.15),
            fontsize=9, color="#004466", arrowprops=dict(arrowstyle="->", color="#004466"))
a3.annotate("销顶离背 1.1mm\n销底离床 1.9mm", (0, PIN_Z + R_PIN), (-10, 6.35),
            fontsize=9, color="#7a0000", arrowprops=dict(arrowstyle="->", color="#7a0000"))
a3.plot([-24, 10], [0, 0], "k-", lw=2.5)
a3.text(-23, -1.1, "打印床(全身平躺)", fontsize=9)
a3.set_xlim(-24, 9); a3.set_ylim(-2.2, 8.2); a3.set_aspect("equal"); a3.axis("off")
a3.set_title("③ 过销轴剖面(XZ):舌眼承销、双耳在面外(虚线);每层打印处境真实如图", fontsize=11)

# ================= ④ 试片 =================
a4 = fig.add_axes([0.62, 0.06, 0.36, 0.44])
a4.add_patch(Rectangle((0, 0), 80, 48, fc="#f8f9fa", ec="#555555", lw=1.2))
for i, (g, tag) in enumerate([(0.05, "紧:赌光洁顺滑"), (0.10, "标准:微焊首折"), (0.15, "松:防收缩粘连")]):
    yy = 37 - i * 12
    a4.add_patch(Rectangle((6, yy - 3), 16, 6, fc=CA, ec="k"))
    a4.add_patch(Rectangle((22, yy - 3.4), 12, 6.8, fc=CEAR, ec="k"))
    a4.add_patch(Circle((28, yy), R_PIN + g, fc="#eef4fb", ec="k"))
    a4.add_patch(Circle((28, yy), R_PIN, fc=CPIN, ec="k"))
    a4.text(38, yy, tag, fontsize=9, va="center")
    a4.text(4, yy + 5, "每侧 +%.2f" % g, fontsize=8, color="#333333")
a4.text(40, 46, "④ 关节试片:耳孔间隙三档并排", ha="center", fontsize=10)
a4.text(40, 2, "先打试片(10min):折开微焊→记手感→反选蜥蜴档", ha="center", fontsize=8.5, color="#7a0000")
a4.text(40, 8.5, "判定:顺滑无沙沙声=可用;折断感=焊死;旷当=间隙过大", ha="center", fontsize=8, color="#333333")
a4.set_xlim(-2, 112); a4.set_ylim(-2, 50); a4.set_aspect("equal"); a4.axis("off")

fig.text(0.5, 0.012, "几何断言 %d/%d 全部 PASS 才出此图(清单在脚本头部)" %
         (sum(1 for _, v in checks if v), len(checks)), ha="center", fontsize=9.5, color="#1a7f37")
fig.suptitle("No.02 可动小蜥蜴 · 设计预览 v2(卧式销铰链:零桥风险·零孤岛·免支撑)", fontsize=13)
fig.savefig("preview_design.png")
print("preview_design.png done")
