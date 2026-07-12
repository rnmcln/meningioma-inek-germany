#!/usr/bin/env python3
"""
Figure S1 — Cross-source consistency of national counts (InEK vs Destatis).
Ratio of InEK to Destatis principal-diagnosis counts, 2019-2024, for the broad
three-digit (D32) and cranial four-digit (D32.0) phenotypes.
Message: the two independent administrative sources agree to within ~5%, a stable
offset consistent with grouper-vintage and case-definition differences, not a
validation against a gold standard.
"""
import os, csv
import figstyle as fs
from figstyle import C, OI
import matplotlib.pyplot as plt

D = os.path.join(os.path.dirname(__file__), "..", "data")
def rd(n):
    with open(os.path.join(D, n), encoding="utf-8") as f: return list(csv.DictReader(f))

rec = rd("fig_reconciliation.csv")
def series(cmp):
    rs=[r for r in rec if r["cmp"]==cmp]
    rs=sorted(rs, key=lambda r:int(r["year"]))
    return [int(r["year"]) for r in rs], [float(r["ratio"]) for r in rs]
y1,r1 = series("CMP2")   # D32.0 cranial (primary)
y2,r2 = series("CMP1")   # D32 broad

fig, ax = fs.figure(90, 68)
plt.subplots_adjust(left=0.17, right=0.965, top=0.93, bottom=0.155)
fs.ygrid(ax)
# concordance reference (1.0) and lightly shaded +/-5% region
ax.axhspan(0.95, 1.05, color="#F2F2F2", zorder=0)
ax.axhline(1.0, color="#999999", lw=0.8, zorder=1)
ax.text(2024.03, 1.002, "exact agreement", color=C["annot"], fontsize=5.6, va="bottom", ha="right")
ax.text(2019.0, 1.0515, "within ±5%", color=C["annot"], fontsize=5.6, va="top", ha="left")

ax.plot(y1, r1, color=C["primary"], lw=1.3, zorder=3)
ax.plot(y1, r1, "o", color=C["primary"], ms=3.8, zorder=4)
ax.plot(y2, r2, color=OI["orange"], lw=1.3, zorder=3)
ax.plot(y2, r2, "s", color=OI["orange"], ms=3.4, zorder=4)
# direct labels placed mid-series where the two lines are well separated
ax.text(2021, r1[2]+0.006, "D32.0 (cranial)", color=C["primary"], fontsize=6.2, ha="center", va="bottom")
ax.text(2021, r2[2]-0.006, "D32 (broad)", color=OI["orange"], fontsize=6.2, ha="center", va="top")

ax.set_xlim(2018.85, 2024.15)
ax.set_ylim(0.985, 1.062)
ax.set_xticks(y1)
ax.set_yticks([1.00,1.02,1.04,1.06])
ax.set_xlabel("year")
ax.set_ylabel("ratio of InEK to Destatis count")
fs.save(fig, "Figure_S1_supplement")
