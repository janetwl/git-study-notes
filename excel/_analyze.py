# -*- coding: utf-8 -*-
"""一次性扫描 7月订单.xlsx,输出 UTF-8 分析报告。只读,不改源文件。"""
import openpyxl
from collections import Counter, defaultdict
from datetime import datetime, date

SRC = r'E:/git-workspace/excel/7月订单.xlsx'
OUT = r'E:/git-workspace/excel/7月订单-分析报告.md'

def to_f(v):
    if v is None or v == '':
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def to_dt(v):
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day)
    if isinstance(v, str) and v.strip():
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d'):
            try:
                return datetime.strptime(v.strip(), fmt)
            except ValueError:
                pass
    return None

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
ws = wb['Sheet1']
it = ws.iter_rows(values_only=True)
raw_header = next(it)
header = [(h if h is not None else 'col%d' % i) for i, h in enumerate(raw_header)]
idx = {}
for i, h in enumerate(header):
    idx.setdefault(str(h).strip(), i)

n = 0
miss = Counter()
orders = set()
status = Counter()
sales_co = Counter()
recv_co = Counter()
otype = Counter()
area = Counter()
buyer_orders = defaultdict(set)
prov = Counter()
city = Counter()
unit = Counter()
brand = Counter()
cat1 = Counter()
cat2 = Counter()
prod_amt = defaultdict(float)
prod_qty = defaultdict(float)
prod_name = Counter()
month_ct = Counter()
day_amt = defaultdict(float)
day_qty = defaultdict(float)
day_orders = defaultdict(set)
dt_min = dt_max = None
amt_total = 0.0
qty_total = 0.0
price_n = 0
price_min = None
price_max = None
order_amt = defaultdict(float)

cOrder = idx.get('OMS销售订单号')
cSaleCo = idx.get('销方企业')
cStatus = idx.get('销售订单状态')
cRecvCo = idx.get('购方企业')
cTime = idx.get('下单时间')
cProdName = idx.get('商品名称')
cUnit = idx.get('计量单位')
cPrice = idx.get('销售价')
cAmt = idx.get('合计金额')
cQty = idx.get('实发数量')
cProv = idx.get('收货省')
cCity = idx.get('收货市')
cOrdType = idx.get('订单类型名称')
cRegion = idx.get('区域')
cCat1 = idx.get('一级目录')
cCat2 = idx.get('二级目录')

for row in it:
    n += 1
    if n % 10000 == 0:
        pass
    for j, v in enumerate(row):
        if v is None or v == '':
            miss[header[j]] += 1
    oid = row[cOrder] if cOrder is not None else None
    if oid:
        orders.add(oid)
    for j, c in ((status, cStatus), (sales_co, cSaleCo), (recv_co, cRecvCo),
                 (prov, cProv), (city, cCity), (unit, cUnit),
                 (cat1, cCat1), (cat2, cCat2), (prod_name, cProdName),
                 (otype, cOrdType), (area, cRegion)):
        if c is not None:
            v = row[c]
            if v not in (None, ''):
                j[str(v)] += 1
    if cRecvCo is not None and oid:
        buyer = row[cRecvCo]
        if buyer not in (None, ''):
            buyer_orders[str(buyer)].add(oid)
    dt = to_dt(row[cTime]) if cTime is not None else None
    if dt:
        if dt_min is None or dt < dt_min:
            dt_min = dt
        if dt_max is None or dt > dt_max:
            dt_max = dt
        month_ct[dt.strftime('%Y-%m')] += 1
        dk = dt.strftime('%Y-%m-%d')
        day_orders[dk].add(oid)
    a = to_f(row[cAmt]) if cAmt is not None else None
    q = to_f(row[cQty]) if cQty is not None else None
    p = to_f(row[cPrice]) if cPrice is not None else None
    if p is not None:
        price_n += 1
        price_min = p if price_min is None or p < price_min else price_min
        price_max = p if price_max is None or p > price_max else price_max
    if a is not None:
        amt_total += a
        if dt:
            day_amt[dt.strftime('%Y-%m-%d')] += a
        if oid:
            order_amt[oid] += a
        if cProdName is not None and row[cProdName]:
            prod_amt[str(row[cProdName])] += a
    if q is not None:
        qty_total += q
        if dt:
            day_qty[dt.strftime('%Y-%m-%d')] += q
        if cProdName is not None and row[cProdName]:
            prod_qty[str(row[cProdName])] += q
wb.close()

L = []
w = L.append
w('# 7月订单.xlsx 分析报告')
w('')
w('> 生成方式:openpyxl 只读流式扫描,未修改源文件。')
w('')
w('## 1. 表结构')
w('')
w('- 明细行数(不含表头):**%d**' % n)
w('- 列数:%d' % len(header))
w('- 去重后 OMS销售订单号 数(即订单数):**%d**' % len(orders))
w('- 平均每单行数:%.2f' % (n / len(orders) if orders else 0))
w('')
w('列清单:')
w('')
for i, h in enumerate(header):
    m = miss.get(h, 0)
    w('- 第%d列 %s (空值 %d, %.1f%%)' % (i, h, m, 100.0 * m / n))
w('')
w('## 2. 时间与状态')
w('')
w('- 下单时间范围:%s ~ %s' % (dt_min, dt_max))
w('- 按月份行数:' + ', '.join('%s: %d' % (k, v) for k, v in sorted(month_ct.items())))
w('- 销售订单状态分布:' + ', '.join('%s %d (%.1f%%)' % (k, v, 100.0 * v / n) for k, v in status.most_common()))
w('- 订单类型分布(前8):' + ', '.join('%s %d (%.1f%%)' % (k, v, 100.0 * v / n) for k, v in otype.most_common(8)))
w('- 销方企业:' + '; '.join('%s %d行' % (k, v) for k, v in sales_co.most_common()))
w('- 区域分布(前10):' + ', '.join('%s %d' % (k, v) for k, v in area.most_common(10)))
w('')
w('## 3. 金额与数量')
w('')
w('- 合计金额 总和:**%.2f 元**(约 %.2f 万元)' % (amt_total, amt_total / 10000))
w('- 实发数量 总和:%.2f(所有单位混加,仅供参考)' % qty_total)
w('- 销售价 范围:%.2f ~ %.2f(有效值 %d 个)' % (price_min or 0, price_max or 0, price_n))
oamts = sorted(order_amt.values())
if oamts:
    mid = oamts[len(oamts) // 2]
    w('- 按订单聚合金额:均值 %.2f,中位数 %.2f,最大 %.2f,最小 %.2f' %
      (amt_total / len(oamts), mid, oamts[-1], oamts[0]))
w('- 计量单位分布(前8):' + ', '.join('%s %d' % (k, v) for k, v in unit.most_common(8)))
w('')
w('## 4. 每日节奏(前5 + 后5)')
w('')
w('| 日期 | 订单数 | 金额 |')
w('|---|---|---|')
days = sorted(day_amt)
for d in days[:5] + days[-5:]:
    w('| %s | %d | %.2f |' % (d, len(day_orders[d]), day_amt[d]))
w('')
w('## 5. 客户与地区')
w('')
w('购方企业 TOP10(按行数;括号内为去重订单数):')
w('')
w('| 购方企业 | 明细行数 | 订单数 |')
w('|---|---|---|')
for k, v in recv_co.most_common(10):
    w('| %s | %d | %d |' % (k, v, len(buyer_orders.get(k, ()))))
w('')
w('收货省 TOP10(行数占比):')
for k, v in prov.most_common(10):
    w('- %s: %d (%.1f%%)' % (k, v, 100.0 * v / n))
w('')
w('收货市 TOP10:')
for k, v in city.most_common(10):
    w('- %s: %d' % (k, v))
w('')
w('## 6. 产品')
w('')
w('一级目录分布:')
for k, v in cat1.most_common(10):
    w('- %s: %d (%.1f%%)' % (k, v, 100.0 * v / n))
w('')
w('二级目录 TOP10:')
for k, v in cat2.most_common(10):
    w('- %s: %d' % (k, v))
w('')
w('金额 TOP15 产品(产品名称,合计金额,行数):')
w('')
w('| 产品 | 金额 | 行数 |')
w('|---|---|---|')
for k, v in sorted(prod_amt.items(), key=lambda x: -x[1])[:15]:
    w('| %s | %.2f | %d |' % (k, v, prod_name.get(k, 0)))
w('')
w('数量 TOP10 产品:')
for k, v in sorted(prod_qty.items(), key=lambda x: -x[1])[:10]:
    w('- %s: %.1f' % (k, v))
w('')

open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('report written:', OUT)
