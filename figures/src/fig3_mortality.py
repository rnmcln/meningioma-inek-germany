#!/usr/bin/env python3
"""
Figure 3 — In-hospital mortality of the primary cohort (principal D32.0).
A: in-hospital mortality, 2019-2024 (95% Wilson CI).
B: age-specific in-hospital mortality, 2024 (95% Wilson CI).
Message: mortality is low (~1.5%) and concentrated in the oldest patients.
"""
import os, csv
import figstyle as fs
from figstyle import C
import matplotlib.pyplot as plt

D = os.path.join(os.path.dirname(__file__), "..", "data")
def rd(n):
    with open(os.path.join(D, n), encoding="utf-8") as f: return list(csv.DictReader(f))

mt = rd("fig_mortality_trend.csv")
yr=[int(r["year"]) for r in mt]
m=[float(r["mortality_pct"]) for r in mt]
lo=[float(r["ci_low"]) for r in mt]; hi=[float(r["ci_high"]) for r in mt]

ma = rd("fig_mortality_by_age_2024.csv")
bands=[r["age_band"] for r in ma]
mv=[float(r["mortality_pct"]) for r in ma]
alo=[float(r["ci_low"]) for r in ma]; ahi=[float(r["ci_high"]) for r in ma]

fig, (axA, axB) = fs.figure_grid(180, 72, ncols=2)
plt.subplots_adjust(wspace=0.30, left=0.085, right=0.985, top=0.90, bottom=0.16)

# ---- Panel A: mortality trend (dot-and-line with 95% CI error bars; annual cross-sections) ----
fs.ygrid(axA)
yerr=[[m[i]-lo[i] for i in range(len(yr))],[hi[i]-m[i] for i in range(len(yr))]]
axA.errorbar(yr, m, yerr=yerr, fmt="none", ecolor=C["mortality"], elinewidth=0.9,
             capsize=2.2, capthick=0.9, alpha=0.7, zorder=2)
axA.plot(yr, m, color=C["mortality"], lw=0.9, ls=(0,(4,2)), zorder=3)
axA.plot(yr, m, "o", color=C["mortality"], ms=3.8, zorder=4)
axA.set_xlim(2018.85, 2024.2)
axA.set_ylim(0.8, 2.2)
axA.set_xticks(yr)
axA.set_yticks([1.0,1.5,2.0])
axA.set_yticklabels(["1.0","1.5","2.0"])
axA.set_xlabel("year")
axA.set_ylabel("in-hospital mortality (%)")
fs.panel_label(axA, "A", dx=-0.16)

# ---- Panel B: age-specific mortality 2024 (horizontal dot + CI) ----
ypos=list(range(len(bands)))[::-1]  # 80+ at top
axB.xaxis.grid(True, color=C["grid"], linewidth=0.5); axB.set_axisbelow(True)
for i,yv in zip(range(len(bands)), ypos):
    axB.plot([alo[i],ahi[i]],[yv,yv], color=C["mortality"], lw=1.1, alpha=0.55, zorder=2)
    axB.plot(mv[i], yv, "o", color=C["mortality"], ms=4.4, zorder=3)
    axB.text(ahi[i]+0.15, yv, f"{mv[i]:.1f}%", va="center", ha="left", fontsize=6.0, color="#333333")
axB.set_yticks(list(range(len(bands)))[::-1])
axB.set_yticklabels(bands)
axB.set_ylim(-0.6, len(bands)-0.4)
axB.set_xlim(0, 6.2)
axB.set_xticks([0,2,4,6])
axB.set_xlabel("in-hospital mortality (%)")
axB.set_ylabel("age (years)")
axB.spines["left"].set_visible(False)
axB.tick_params(axis="y", length=0)
fs.panel_label(axB, "B", dx=-0.18)

fs.save(fig, "Figure_3_main")
