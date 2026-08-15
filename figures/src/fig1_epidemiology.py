#!/usr/bin/env python3
"""
Figure 1 — National inpatient burden of cranial meningioma-coded admissions.
A: age-standardised episode rate (ESP2013) 2019-2024, with crude rate reference.
B: age-specific episode rate, 2024 (both sexes).
Explanatory text lives in the figure legend; the panels carry only data.
"""
import os, csv
import figstyle as fs
from figstyle import C
import matplotlib.pyplot as plt

D = os.path.join(os.path.dirname(__file__), "..", "data")
def rd(n):
    with open(os.path.join(D, n), encoding="utf-8") as f: return list(csv.DictReader(f))

asr = rd("fig_asr_trend.csv")
years = [int(r["year"]) for r in asr]
A = [float(r["asr"]) for r in asr]
lo = [float(r["ci_low"]) for r in asr]; hi = [float(r["ci_high"]) for r in asr]
crude = [float(r["crude"]) for r in asr]

ag = rd("fig_age_specific_2024.csv")
ag = [r for r in ag if ("-" in r["band"] or r["band"].endswith("+"))]
def band_start(b): return 85 if b=="85+" else int(b.split("-")[0])
ag = sorted(ag, key=lambda r: band_start(r["band"]))
bands = [r["band"] for r in ag]
ya = [float(r["rate_per100k"]) for r in ag]

fig, (axA, axB) = fs.figure_grid(180, 74, ncols=2)
plt.subplots_adjust(wspace=0.28, left=0.085, right=0.985, top=0.86, bottom=0.15)

# ---- Panel A: ASR trend (data only; crude vs age-standardized shown via legend) ----
fs.ygrid(axA)
axA.fill_between(years, lo, hi, color=C["primary"], alpha=0.15, linewidth=0, zorder=1)
lc, = axA.plot(years, crude, color="#AAAAAA", lw=1.0, zorder=2, label="crude")
la, = axA.plot(years, A, color=C["primary"], lw=1.5, marker="o", ms=3.8, zorder=3,
               label="age-standardized")
# census-basis change (2022), between 2021 and 2022 — explained in the legend
axA.axvline(2021.5, color=C["annot"], lw=0.7, ls=(0,(2,2)), zorder=1)
axA.set_xlim(2018.85, 2024.25)
axA.set_ylim(7.5, 10.2)
axA.set_xticks(years)
axA.set_xlabel("year")
axA.set_ylabel("episode rate (per 100,000)")
axA.legend(handles=[la, lc], loc="lower center", bbox_to_anchor=(0.5, 1.005),
           ncol=2, frameon=False, handlelength=1.6, columnspacing=1.4)
fs.panel_label(axA, "A", dx=-0.16)

# ---- Panel B: age-specific rate 2024 (categorical bars) ----
fs.ygrid(axB)
xpos = list(range(len(bands)))
axB.bar(xpos, ya, width=0.82, color=C["primary"], linewidth=0, zorder=3)
axB.set_xlim(-0.7, len(bands)-0.3)
axB.set_ylim(0, 26)
axB.set_xticks(xpos)
axB.set_xticklabels(bands, rotation=90, fontsize=5.0)
axB.set_xlabel("age band (years)")
axB.set_ylabel("episode rate (per 100,000)")
fs.panel_label(axB, "B", dx=-0.16)

fs.save(fig, "Figure_1_main")
