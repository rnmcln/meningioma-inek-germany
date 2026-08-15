#!/usr/bin/env python3
"""
Case structure and phenotype specificity.
A: age and sex distribution of principal-D32.0 discharges, 2024 (Destatis).
B: cranial fraction (D32.0 as a percentage of three-digit D32), 2019-2024, with
   the unspecified-site fraction (D32.9) on a secondary axis.
NOTE: in the manuscript this is Supplementary Figure S1 (cited first, for the
age distribution); output name set accordingly.
Explanatory text lives in the figure legend; the panels carry only data.
"""
import os, csv
import figstyle as fs
from figstyle import C
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

D = os.path.join(os.path.dirname(__file__), "..", "data")
def rd(n):
    with open(os.path.join(D, n), encoding="utf-8") as f: return list(csv.DictReader(f))

ax_ = rd("fig_agesex_2024.csv")
def enlabel(b):
    return {"unter 1":"<1", "95 und älter":"95+"}.get(b, b)
male=[int(float(r["male"])) for r in ax_]
female=[int(float(r["female"])) for r in ax_]
labels=[enlabel(r["age_group"]) for r in ax_]

cf = rd("fig_subsite_fraction.csv")
cy=[int(r["year"]) for r in cf]
cpct=[float(r["cranial_pct"]) for r in cf]
upct=[float(r["unspec_pct"]) for r in cf]

fig, (axA, axB) = fs.figure_grid(180, 84, ncols=2, gridspec_kw={"width_ratios":[1.15,1]})
plt.subplots_adjust(wspace=0.34, left=0.075, right=0.985, top=0.84, bottom=0.14)

# ---- Panel A: age-sex pyramid (counts); sex shown via legend ----
ypos=list(range(len(labels)))
bh=0.82
axA.barh(ypos, [-v for v in female], height=bh, color=C["female"], linewidth=0, zorder=3)
axA.barh(ypos, male, height=bh, color=C["male"], linewidth=0, zorder=3)
axA.axvline(0, color="#333333", lw=0.6)
xmax=800
axA.set_xlim(-xmax, xmax)
axA.set_xticks([-800,-400,0,400,800])
axA.set_xticklabels(["800","400","0","400","800"])
show=set(range(0,len(labels),2))
axA.set_yticks([i for i in ypos if i in show])
axA.set_yticklabels([labels[i] for i in ypos if i in show])
axA.tick_params(axis="y", length=0)
axA.spines["left"].set_visible(False)
axA.set_ylim(-0.7, len(labels)-0.3)
axA.set_xlabel("discharge episodes (n)")
axA.set_ylabel("age (years)")
axA.legend(handles=[Patch(color=C["female"], label="female"),
                    Patch(color=C["male"], label="male")],
           loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=2, frameon=False,
           handlelength=1.2, columnspacing=1.4)
fs.panel_label(axA, "A", dx=-0.15)

# ---- Panel B: cranial fraction (left) and unspecified-site fraction (right) ----
fs.ygrid(axB)
axB.plot(cy, cpct, color=C["primary"], lw=1.4, marker="o", ms=3.6, zorder=3)
axB.set_xlim(2018.8, 2024.2)
axB.set_ylim(74, 90)
axB.set_xticks(cy); axB.set_yticks([75,80,85,90])
axB.set_xlabel("year")
axB.set_ylabel("cranial fraction, D32.0 / D32 (%)", color=C["primary"])
axB.tick_params(axis="y", colors=C["primary"])
# unspecified-site fraction on secondary axis (declining -> drives the cranial rise)
ax2=axB.twinx()
ax2.plot(cy, upct, color="#D55E00", lw=1.2, ls=(0,(3,2)), marker="s", ms=3.0, zorder=3)
ax2.set_ylim(0, 12); ax2.set_yticks([0,4,8,12])
ax2.set_ylabel("unspecified-site fraction, D32.9 / D32 (%)", color="#D55E00")
ax2.tick_params(axis="y", colors="#D55E00")
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color("#D55E00")
ax2.spines["top"].set_visible(False)
axB.legend(handles=[Line2D([0],[0], color=C["primary"], marker="o", ms=3.6, lw=1.4,
                           label="cranial (D32.0), left axis"),
                    Line2D([0],[0], color="#D55E00", marker="s", ms=3.0, lw=1.2,
                           ls=(0,(3,2)), label="unspecified (D32.9), right axis")],
           loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=1, frameon=False,
           handlelength=1.8, borderaxespad=0.2)
fs.panel_label(axB, "B", dx=-0.17)

fs.save(fig, "Figure_S1_supplement")
