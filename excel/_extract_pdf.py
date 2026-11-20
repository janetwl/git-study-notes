# -*- coding: utf-8 -*-
import fitz, os, glob
base = "E:/git-workspace/excel"
# find the target dir (the one named with Chinese chars) by listing dirs
subs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
target = None
for d in subs:
    pdfs = glob.glob(os.path.join(base, d, "*.pdf"))
    if pdfs:
        target = os.path.join(base, d)
        break
print("target dir:", target.encode("unicode_escape").decode())
for p in sorted(glob.glob(os.path.join(target, "*.pdf"))):
    doc = fitz.open(p)
    print("pages:", len(doc))
    out = p[:-4] + ".txt"
    with open(out, "w", encoding="utf-8") as f:
        for i, page in enumerate(doc):
            f.write("\n===== p%d =====\n" % (i+1))
            f.write(page.get_text("text"))
    doc.close()
    print("wrote:", out.encode("unicode_escape").decode()[:80])
