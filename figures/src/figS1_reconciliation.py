#!/usr/bin/env python3
"""
Cross-source consistency of national counts (InEK vs Destatis).
Ratio of InEK to Destatis principal-diagnosis counts, 2019-2024, for the broad
three-digit (D32) and cranial four-digit (D32.0) phenotypes.
NOTE: in the manuscript this is Supplementary Figure S2 (the age-sex/cranial
structure figure is S1, cited first); output name set accordingly.
Explanatory text lives in the figure legend; the panel carries only data.
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

fig, ax = fs.figure(90, 72)
plt.subplots_adjust(left=0.17, right=0.965, top=0.86, bottom=0.145)
fs.ygrid(ax)
# concordance reference (1.0) and lightly shaded +/-5% region (explained in legend)
ax.axhspan(0.95, 1.05, color="#F2F2F2", zorder=0)
ax.axhline(1.0, color="#999999", lw=0.8, zorder=1)

ax.plot(y1, r1, color=C["primary"], lw=1.3, marker="o", ms=3.8, zorder=3,
        label="D32.0 (cranial)")
ax.plot(y2, r2, color=OI["orange"], lw=1.3, marker="s", ms=3.4, zorder=3,
        label="D32 (broad)")

ax.set_xlim(2018.85, 2024.15)
ax.set_ylim(0.985, 1.062)
ax.set_xticks(y1)
ax.set_yticks([1.00,1.02,1.04,1.06])
ax.set_xlabel("year")
ax.set_ylabel("ratio of InEK to Destatis count")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=2, frameon=False,
          handlelength=1.6, columnspacing=1.4)
fs.save(fig, "Figure_S2_supplement")
