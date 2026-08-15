#!/usr/bin/env python3
"""
RUN_ALL.py — regenerate the complete figure system deterministically.
Order: data cleaning (prepare_figure_data) -> each figure script.
Outputs SVG + PDF + PNG (600 dpi) into figures/output/.
Run from anywhere:  python figures/RUN_ALL.py
"""
import runpy, os, sys
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, SRC)
for mod in ["prepare_figure_data",
            "fig1_epidemiology", "fig2_treatment", "fig3_mortality",
            "figS1_reconciliation", "figS2_structure"]:
    print(f"\n=== {mod} ===")
    runpy.run_path(os.path.join(SRC, mod + ".py"), run_name="__main__")
print("\nAll figures regenerated in figures/output/.")
