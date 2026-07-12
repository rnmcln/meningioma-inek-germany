#!/usr/bin/env python3
"""
prepare_figure_data.py -- data cleaning only (kept separate from figure code).

Reads the extracted aggregate inputs and writes tidy per-figure CSVs into
figures/data/. No data values are hardcoded here: every figure input is derived
from the files under phase1_extraction/data/, phase2_extraction/data/ and
reconciliation/. The age-specific mortality panel reads its cohort/deaths age
distribution from inek_D32.0_age_distribution_2024.csv (see DATA_DICTIONARY.md).
"""
import csv, os, math
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

def rd(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
def wr(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print("wrote", name, f"({len(rows)} rows)")
def wilson(k, n):
    if not n: return (0.0, 0.0)
    z = 1.96; p = k/n; d = 1+z*z/n
    c = (p+z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return ((c-h)*100, (c+h)*100)

# 1) ASR trend
asr = rd("phase2_extraction/data/D32.0_ASR_trend.csv")
wr("fig_asr_trend.csv", ["year","episodes","population","crude","asr","ci_low","ci_high","basis"],
   [[r["year"],r["episodes"],r["population"],r["crude_per100k"],r["asr_esp2013_per100k"],
     r["asr_ci_low"],r["asr_ci_high"],r["population_basis"]] for r in asr])

# 2) Age-specific rate 2024
age = [r for r in rd("phase2_extraction/data/D32.0_ASR_2024.csv") if r.get("band")]
wr("fig_age_specific_2024.csv", ["band","cases","population","rate_per100k"],
   [[r["band"],r["cases"],r["population"],r["age_specific_per100k"]] for r in age])

# 3) Resection-share trend
res = rd("phase1_extraction/data/inek_D32.0_resection_trend_2019-2024.csv")
wr("fig_resection_trend.csv", ["year","cohort","operative","share_pct"],
   [[r["year"],r["cohort_principal_D32.0"],r["operative_resection_5-015.3or.4"],r["resection_share_pct"]] for r in res])

# 4) In-hospital mortality trend
mort = rd("phase1_extraction/data/inek_D32.0_mortality_2019-2024.csv")
rows = []
for r in mort:
    lo, hi = r["mortality_95ci"].split("-")
    rows.append([r["year"], r["cohort_N"], r["in_hospital_deaths"], r["mortality_pct"], lo, hi])
wr("fig_mortality_trend.csv", ["year","cohort","deaths","mortality_pct","ci_low","ci_high"], rows)

# 5) Age-specific in-hospital mortality 2024 (age distribution read from input, not hardcoded)
princ = {int(r["year"]): r for r in rd("phase1_extraction/data/inek_D32.0_principal_2019-2024.csv")}
mo = {int(r["year"]): r for r in mort}
agedist = rd("phase1_extraction/data/inek_D32.0_age_distribution_2024.csv")
if agedist and 2024 in princ:
    Ncoh = int(princ[2024]["fallzahl"]); Ndea = int(mo[2024]["in_hospital_deaths"])
    rows = []
    for r in agedist:
        ck = round(float(r["cohort_pct"])/100*Ncoh); dk = round(float(r["deaths_pct"])/100*Ndea)
        m = dk/ck*100 if ck else 0; lo, hi = wilson(dk, ck)
        rows.append([r["band"], ck, dk, round(m,2), round(lo,2), round(hi,2)])
    wr("fig_mortality_by_age_2024.csv", ["age_band","admissions","deaths","mortality_pct","ci_low","ci_high"], rows)

# 6) Cross-source reconciliation
rec = rd("reconciliation/reconciliation_report.csv")
rows = []
for r in rec:
    if not r.get("ratio_inek_over_destatis"): continue
    ph = "D32 (broad, 3-digit)" if r["comparison"] == "CMP1" else "D32.0 (cranial, 4-digit)"
    rows.append([r["comparison"], ph, r["year"], r["N_inek"], r["N_destatis"], r["ratio_inek_over_destatis"]])
wr("fig_reconciliation.csv", ["cmp","phenotype","year","n_inek","n_destatis","ratio"], rows)

# 7) Sex x age case structure 2024 (Destatis D32.0, principal)
ax = rd("phase2_extraction/data/destatis_4digit_meningeal_2024.csv")
band_order = ["unter 1","1-5","5-10","10-15","15-18","18-20","20-25","25-30","30-35","35-40",
              "40-45","45-50","50-55","55-60","60-65","65-70","70-75","75-80","80-85","85-90","90-95","95 und älter"]
def lab(b): return {"unter 1":"0","95 und älter":"95+"}.get(b, b.split("-")[0])
rows = []
for b in band_order:
    mv = next((r["N"] for r in ax if r["icd_code"]=="D32.0" and r["sex"]=="m" and r["age_group"]==b), "")
    wv = next((r["N"] for r in ax if r["icd_code"]=="D32.0" and r["sex"]=="w" and r["age_group"]==b), "")
    rows.append([b, lab(b), mv or 0, wv or 0])
wr("fig_agesex_2024.csv", ["age_group","age_start","male","female"], rows)

# 8) Cranial fraction D32.0 / D32 (three-digit total derived from GENESIS 23131 input)
tot = rd("phase2_extraction/data/destatis_4digit_meningeal_2019-2024_totals.csv")
threed = rd("phase2_extraction/data/destatis_23131-0001_meningeal_3digit.csv")
d32_3 = {}
for r in threed:
    try: y = int(r.get("year",""))
    except ValueError: continue
    if r.get("icd_code","").strip() == "D32" and "princip" in r.get("position","").lower():
        d32_3[y] = d32_3.get(y, 0) + (int(r["N"]) if str(r.get("N","")).strip().isdigit() else 0)
tot_by = defaultdict(lambda: defaultdict(int))
for r in tot:
    tot_by[int(r["year"])][r["icd_code"]] += int(r["N_total_all_ages"]) if r["N_total_all_ages"] else 0
rows = []
for y in sorted(tot_by):
    if y in d32_3 and d32_3[y]:
        d0 = tot_by[y]["D32.0"]; rows.append([y, d0, d32_3[y], round(d0/d32_3[y]*100, 1)])
wr("fig_cranial_fraction.csv", ["year","d32_0","d32_3digit","cranial_pct"], rows)

print("\nFigure-data CSVs prepared in figures/data/ (empty until inputs are populated).")
