#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_quotes.py — 校验笔记中的引号是否逐字出自提取全文(中英文均支持)。
用法: python -I verify_quotes.py <fulltext.txt> <notes_dir>
规则: 抽取笔记中所有 "..." / “...” 内的片段(≥25 个字母数字或汉字),
按省略号/分号/破折号切分后,与全文做"仅字母数字+汉字小写"的包含匹配
(可穿越行折叠与编码噪声)。
MISS = 引文与原文有出入,必须回原文核对修正。
"""
import re, io, glob, sys

def norm(s):
    return re.sub(r'[^0-9a-z一-鿿]', '', s.lower())

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    full_path, notes_dir = sys.argv[1], sys.argv[2]
    full = io.open(full_path, encoding='utf-8', errors='replace').read()
    FL = norm(full)
    fails = 0
    for fn in glob.glob(notes_dir + '/**/*.md', recursive=True):
        if fn.replace('\\', '/').endswith('00-overview.md'):
            continue
        for i, ln in enumerate(io.open(fn, encoding='utf-8', errors='replace'), 1):
            spans = []
            parts = ln.split('"')          # ASCII 引号:奇偶交替配对,引号对之间的行文不算引文
            spans += [parts[j] for j in range(1, len(parts) - 1, 2)] if len(parts) % 2 == 1 else []
            if len(parts) % 2 == 0:        # 引号数为偶数才能完整配对;不配对则跳过该行 ASCII 部分
                pass
            spans += re.findall(r'“([^”\n]{20,})”', ln)  # 中文弯引号自带开合方向
            for s in spans:
                if len(s) < 20:
                    continue
                for f in re.split(r'…{1,2}|\.\.\.|; | — ', s):
                    lf = norm(f.strip(' ,.;:()（）[]"“”「」'))
                    if len(lf) >= 25 and lf not in FL:
                        fails += 1
                        sys.stdout.buffer.write(('MISS %s:%d  %s\n' % (fn.split('\\')[-1], i, f[:80])).encode('utf-8'))
    print('total fails =', fails)
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
