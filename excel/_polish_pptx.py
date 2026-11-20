# -*- coding: utf-8 -*-
from pptx import Presentation
F = r"E:\git-workspace\excel\聚合物的屈服与断裂_银纹剪切带与强韧化_第24讲_修改稿.pptx"
p = Presentation(F)
n = 0
for si, s in enumerate(p.slides, 1):
    for sh in s.shapes:
        if not sh.has_text_frame: continue
        for para in sh.text_frame.paragraphs:
            for r in para.runs:
                t = r.text
                if not t: continue
                s2 = t
                s2 = s2.replace('(HIPS/ABS/PVC/PP)', '（HIPS/ABS/PVC/PP）').replace('(ESC)', '（ESC）')
                s2 = s2.replace('， ', '，')
                if '"' in s2:
                    out = []; open_ = False
                    for ch in s2:
                        if ch == '"':
                            out.append('“' if not open_ else '”'); open_ = not open_
                        else:
                            out.append(ch)
                    s2 = ''.join(out)
                if s2 != t:
                    r.text = s2; n += 1
                    print(si, sh.name, '->', s2[:70])
p.save(F)
print('fixed:', n)
