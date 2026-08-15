#!/usr/bin/env python3
"""
figstyle.py — shared visual system for all manuscript figures.

One font (Liberation Sans, metric-identical to Arial), one colour-blind-safe
palette (Okabe-Ito), consistent sizing, editable vector output. Imported by
every figure script so the figures form one coherent publication system.
"""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ---- font: Liberation Sans is metric-compatible with Arial ----
for p in ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
          "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
          "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]:
    if os.path.exists(p):
        try: fm.fontManager.addfont(p)
        except Exception: pass

BASE = 7            # base font size (pt) — legible after journal reduction
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "Nimbus Sans", "DejaVu Sans"],
    "font.size": BASE,
    "axes.titlesize": BASE,
    "axes.labelsize": BASE,
    "xtick.labelsize": BASE - 0.5,
    "ytick.labelsize": BASE - 0.5,
    "legend.fontsize": BASE - 0.5,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#333333",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "grid.color": "#E6E6E6",
    "grid.linewidth": 0.5,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "lines.linewidth": 1.3,
    "lines.markersize": 4,
    "figure.dpi": 120,
    "savefig.dpi": 600,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "svg.fonttype": "none",   # keep text editable in SVG
    "pdf.fonttype": 42,       # embed TrueType, editable in PDF
    "ps.fonttype": 42,
})

# ---- Okabe-Ito colour-blind-safe palette + semantic assignments ----
OI = {
    "black":  "#000000", "orange": "#E69F00", "skyblue": "#56B4E9",
    "green":  "#009E73", "yellow": "#F0E442", "blue": "#0072B2",
    "vermillion": "#D55E00", "purple": "#CC79A7",
}
C = {
    "primary":   OI["blue"],       # principal cohort / InEK / main finding
    "reference": "#6E6E6E",        # comparator (Destatis, crude), reference groups
    "ci":        "#BDBDBD",        # confidence bands / secondary
    "female":    OI["blue"],
    "male":      OI["orange"],
    "resection": OI["blue"],
    "access":    OI["skyblue"],
    "technique": OI["green"],
    "radiotherapy": OI["orange"],
    "mortality": OI["vermillion"],
    "grid":      "#E6E6E6",
    "annot":     "#555555",
}
MM = 1 / 25.4

def figure(width_mm, height_mm):
    return plt.subplots(figsize=(width_mm * MM, height_mm * MM))

def figure_grid(width_mm, height_mm, ncols, nrows=1, **kw):
    return plt.subplots(nrows, ncols, figsize=(width_mm * MM, height_mm * MM), **kw)

def panel_label(ax, letter, dx=-0.14, dy=1.04):
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="top", ha="left")

def ygrid(ax):
    ax.yaxis.grid(True, color=C["grid"], linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

def save(fig, name, outdir=None):
    outdir = outdir or os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(outdir, exist_ok=True)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(os.path.join(outdir, f"{name}.{ext}"), facecolor="white")
    plt.close(fig)
    print("saved", name, "(svg/pdf/png)")
