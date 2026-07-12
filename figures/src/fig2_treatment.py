#!/usr/bin/env python3
"""
Figure 2 — Composition of inpatient activity, principal-D32.0 episodes.
A: annual resection-associated and non-resection episodes (stacked counts) with the
   resection-associated share overlaid, 2019-2024.
B: procedure and technique code prevalence, 2024, as a percentage of ALL
   principal-D32.0 episodes (not of resections), grouped by code type.
Message: total volume dipped in 2020 and recovered; the resection-associated share
rose because resection-associated episodes increased while non-resection episodes fell.
"""
import os, csv, math
import figstyle as fs
from figstyle import C
import matplotlib.pyplot as plt

D = os.path.join(os.path.dirname(__file__), "..", "data")
def rd(n):
    with open(os.path.join(D, n), encoding="utf-8") as f: return list(csv.DictReader(f))

dec = rd("fig_resection_decomp.csv")
yr=[int(r["year"]) for r in dec]
resn=[int(r["resection"]) for r in dec]
nonr=[int(r["nonresection"]) for r in dec]
share=[float(r["resection_pct"]) for r in dec]

prof = rd("fig_procedure_profile_2024.csv")

fig, (axA, axB) = fs.figure_grid(180, 82, ncols=2, gridspec_kw={"width_ratios":[1,1.2]})
plt.subplots_adjust(wspace=0.62, left=0.085, right=0.985, top=0.88, bottom=0.16)

# ---- Panel A: decomposition (stacked counts); resection share shown as labels ----
fs.ygrid(axA)
w=0.64
axA.bar(yr, resn, width=w, color=C["resection"], linewidth=0, zorder=3, label="resection-associated")
axA.bar(yr, nonr, width=w, bottom=resn, color="#C9D8E8", linewidth=0, zorder=3, label="non-resection")
axA.set_ylim(0, 9700)
axA.set_yticks([0,2000,4000,6000,8000])
axA.set_yticklabels(["0","2 000","4 000","6 000","8 000"])
axA.set_xticks(yr); axA.set_xticklabels([str(y) for y in yr], rotation=0, fontsize=5.6)
axA.set_xlabel("year")
axA.set_ylabel("episodes (n)")
# resection-associated share as small labels above each bar
for x, tot, sh in zip(yr, [r+n for r,n in zip(resn,nonr)], share):
    axA.text(x, tot+180, f"{sh:.1f}%", ha="center", va="bottom", fontsize=5.6, color=C["resection"])
axA.text(0.5, 1.02, "resection-associated share (%) above bars", transform=axA.transAxes,
         ha="center", va="bottom", fontsize=5.4, color=C["annot"])
axA.legend(loc="lower center", bbox_to_anchor=(0.5,-0.36), ncol=2, frameon=False,
           fontsize=5.6, handlelength=1.0, columnspacing=1.0)
fs.panel_label(axA, "A", dx=-0.22)

# ---- Panel B: procedure profile 2024 (grouped horizontal lollipop) ----
gcol = {"resection":C["resection"], "technique":C["technique"], "other":C["annot"]}
gname = {"resection":"resection", "technique":"adjunctive technique", "other":"other"}
order = ["resection","technique","other"]
rows=[]
for g in order:
    for r in prof:
        if r["group"]==g: rows.append(r)
rows = rows[::-1]  # first group at top
for i,r in enumerate(rows):
    v=float(r["pct_of_cohort"]); g=r["group"]
    axB.hlines(i, 0, v, color="#D9D9D9", lw=1.0, zorder=1)
    axB.plot(v, i, "o", color=gcol[g], ms=4.2, zorder=3)
    axB.text(v+1.4, i, f"{v:.1f}", va="center", ha="left", fontsize=6.0, color="#333333")
labels=[r["procedure"] for r in rows]
axB.set_yticks(list(range(len(rows)))); axB.set_yticklabels(labels, fontsize=6.1)
axB.set_ylim(-0.9, len(rows)-0.3)
axB.set_xlim(0, 84)
axB.set_xticks([0,20,40,60,80])
axB.set_xlabel("% of all principal-D32.0 episodes (n = 8 361)")
axB.spines["left"].set_visible(False)
axB.tick_params(axis="y", length=0)
# group colour key in lower-right white space
kx = 58
for j,g in enumerate(order):
    ky = 2.0 - j*0.6
    axB.plot(kx, ky, "o", color=gcol[g], ms=4.0)
    axB.text(kx+2.4, ky, gname[g], va="center", fontsize=5.8, color="#333333")
fs.panel_label(axB, "B", dx=-0.34)

fig.text(0.5, 0.008,
         "Codes are not mutually exclusive; values are episode-level code prevalence, not proportions of resections.",
         ha="center", fontsize=6.2, color=C["annot"])
fs.save(fig, "Figure_2_main")
