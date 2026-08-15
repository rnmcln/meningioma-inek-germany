#!/usr/bin/env python3
"""
build_tables.py -- analysis hub.

Reads the extracted aggregate inputs (which the user must regenerate from the
InEK DatenBrowser and Destatis GENESIS; see docs/extraction_manifest.md and
docs/DATA_DICTIONARY.md), recomputes every derived quantity, verifies internal
identities, and writes tidy table CSVs plus the figure-input CSVs.

No data values are hardcoded in this file: cohort sizes, three-digit totals and
all derived statistics are computed from the input files. The repository ships
only header-only templates for those inputs, so this script produces empty
outputs until the templates are populated with locally regenerated data.
"""
import os, csv, json, math, re
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(os.path.dirname(__file__), "data")
FIGDATA = os.path.join(ROOT, "figures", "data")
os.makedirs(DATA, exist_ok=True); os.makedirs(FIGDATA, exist_ok=True)
YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
REPORT = []
def check(name, ok, detail=""):
    REPORT.append(f"[{'PASS' if ok else 'FAIL'}] {name}{(' -- '+detail) if detail else ''}")
    return ok

def rd(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
def num(x):
    s = str(x).strip().replace(".", "").replace(",", "")
    return int(s) if s.lstrip("-").isdigit() else None
def wilson(k, n):
    if not n: return (0.0, 0.0)
    z = 1.96; p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h) * 100, (c + h) * 100

# ---------- load inputs ----------
princ = {int(r["year"]): r for r in rd("phase1_extraction/data/inek_D32.0_principal_2019-2024.csv")}
mort  = {int(r["year"]): r for r in rd("phase1_extraction/data/inek_D32.0_mortality_2019-2024.csv")}
resn  = {int(r["year"]): r for r in rd("phase1_extraction/data/inek_D32.0_resection_trend_2019-2024.csv")}
asrf  = {int(r["year"]): r for r in rd("phase2_extraction/data/D32.0_ASR_trend.csv")}
recon = rd("reconciliation/reconciliation_report.csv")
opsum = {r["measure"]: r for r in rd("phase1_extraction/data/inek_D32.0_operative_summary_2024.csv")}
tot4  = rd("phase2_extraction/data/destatis_4digit_meningeal_2019-2024_totals.csv")
counts = rd("reconciliation/phase_counts_long.csv")
mortop = {r["stratum"]: r for r in rd("phase1_extraction/data/inek_D32.0_mortality_by_operative_2024.csv")}
subc  = {r["category"]: r for r in rd("phase1_extraction/data/inek_D32.0_resection_subcodes_2024.csv")}
threed = rd("phase2_extraction/data/destatis_23131-0001_meningeal_3digit.csv")

if not princ:
    print("No input data found. Populate the templates under */data/ first "
          "(see docs/DATA_DICTIONARY.md and docs/extraction_manifest.md).")

# cohort size and three-digit totals are DERIVED, not hardcoded
Ncoh = int(princ[2024]["fallzahl"]) if 2024 in princ else 0
# three-digit D32 principal counts from the GENESIS 23131 series (independent of the 4-digit report)
D32_3digit = {}
for r in threed:
    try: y = int(r.get("year", ""))
    except ValueError: continue
    if r.get("icd_code", "").strip() == "D32" and "princip" in r.get("position", "").lower():
        D32_3digit[y] = D32_3digit.get(y, 0) + (num(r.get("N")) or 0)

def f1(x): return f"{x:.1f}"
def thin(n): return f"{n:,}".replace(",", " ")

# ---------- VERIFY: four-digit sum == three-digit total ----------
by = defaultdict(lambda: defaultdict(int))
for r in tot4:
    by[int(r["year"])][r["icd_code"]] += int(r["N_total_all_ages"]) if r["N_total_all_ages"] else 0
for y in YEARS:
    if y in D32_3digit:
        s = by[y]["D32.0"] + by[y]["D32.1"] + by[y]["D32.9"]
        check(f"4-digit sum == 3-digit D32 {y}", s == D32_3digit[y], f"{s} vs {D32_3digit[y]}")

# ---------- age standardization (direct, ESP2013) ----------
ESP = {"0-4":5000,"5-9":5500,"10-14":5500,"15-19":5500,"20-24":6000,"25-29":6000,
       "30-34":6500,"35-39":7000,"40-44":7000,"45-49":7000,"50-54":7000,"55-59":6500,
       "60-64":6000,"65-69":5500,"70-74":5000,"75-79":4000,"80-84":2500,"85+":2500}
BANDS = list(ESP); W = sum(ESP.values())
def band(a): return "85+" if a >= 85 else f"{(a//5)*5}-{(a//5)*5+4}"
# population by year x band (GENESIS 12411-0005 flat export at repo root)
POP = defaultdict(lambda: defaultdict(int))
popfile = os.path.join(ROOT, "12411-0005_de_flat_more-years.csv")
if os.path.exists(popfile):
    for p in csv.reader(open(popfile, encoding="utf-8-sig"), delimiter=";"):
        if len(p) < 14: continue
        m = re.match(r"(\d{4})-12-31", p[4] or "")
        if not m: continue
        y = int(m.group(1))
        if y not in YEARS: continue
        lab = p[12].strip().lower()
        if "unter 1" in lab: a = 0
        elif "und mehr" in lab: a = 85
        else:
            mm = re.search(r"(\d+)", lab); a = int(mm.group(1)) if mm else None
        if a is None: continue
        POP[y][band(a)] += num(p[13]) or 0
NUM = defaultdict(lambda: defaultdict(int)); UNKNOWN = defaultdict(int)
for r in rd("phase2_extraction/data/destatis_D32.0_agesex_2019-2024.csv"):
    y = int(r["year"]); l = r["age_band"].strip().lower()
    if "unbekannt" in l: UNKNOWN[y] += num(r["N"]) or 0; continue
    if "unter 1" in l: b = "0-4"
    else:
        mm = re.match(r"(\d+)", l); b = band(int(mm.group(1))) if mm else None
    if b: NUM[y][b] += num(r["N"]) or 0
ASR = {}
for y in YEARS:
    if not any(POP[y].values()): continue
    asr = sum((NUM[y][b]/POP[y][b]*1e5)*ESP[b] for b in BANDS if POP[y][b]) / W
    se = math.sqrt(sum((ESP[b]/W)**2*(NUM[y][b]/POP[y][b]**2)*1e10 for b in BANDS if POP[y][b]))
    ASR[y] = (asr, asr-1.96*se, asr+1.96*se, sum(POP[y].values()))
    if y in asrf:
        check(f"ASR recomputed matches stored {y}", abs(asr-float(asrf[y]["asr_esp2013_per100k"]))<0.05)

# ---------- verify resection share, mortality, ratios, partitions ----------
for y in YEARS:
    if y not in resn: continue
    coh = int(resn[y]["cohort_principal_D32.0"]); op = int(resn[y]["operative_resection_5-015.3or.4"])
    check(f"resection share {y}", abs(op/coh*100 - float(resn[y]["resection_share_pct"])) < 0.1)
for y in YEARS:
    if y not in mort: continue
    coh = int(mort[y]["cohort_N"]); d = int(mort[y]["in_hospital_deaths"])
    check(f"mortality {y}", abs(d/coh*100 - float(mort[y]["mortality_pct"])) < 0.02)
for r in recon:
    if r.get("ratio_inek_over_destatis"):
        check("cross-source ratio recompute " + r["comparison"] + " " + r["year"],
              abs(int(r["N_inek"])/int(r["N_destatis"]) - float(r["ratio_inek_over_destatis"])) < 0.001)

either = int(subc["either_resection"]["episodes_N"]) if subc else 0
w_inf  = int(subc["resection_5-015.4_any"]["episodes_N"]) if subc else 0
wo_inf = int(subc["resection_5-015.3_any"]["episodes_N"]) if subc else 0
both   = int(subc["both_resection"]["episodes_N"]) if subc else 0
if subc:
    check("subcode overlap = |A|+|B|-|A or B|", both == (w_inf + wo_inf - either))

if mortop:
    op_e = int(mortop["operative"]["episodes_N"]); op_d = int(mortop["operative"]["in_hospital_deaths"])
    no_e = int(mortop["non_operative"]["episodes_N"]); no_d = int(mortop["non_operative"]["in_hospital_deaths"])
    tt_e = int(mortop["total"]["episodes_N"]); tt_d = int(mortop["total"]["in_hospital_deaths"])
    check("operative + non-operative episodes == cohort", op_e + no_e == tt_e)
    check("operative + non-operative deaths == total", op_d + no_d == tt_d)

# ==================================================================
# TABLES (written as tidy CSVs)
# ==================================================================
def wr(name, cols, rows):
    with open(os.path.join(DATA, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(rows)

if princ:
    # Table 1: annual cohort characteristics
    t1 = []
    for y in YEARS:
        coh = int(resn[y]["cohort_principal_D32.0"]); op = int(resn[y]["operative_resection_5-015.3or.4"])
        rlo, rhi = wilson(op, coh)
        d = int(mort[y]["in_hospital_deaths"]); m = d/coh*100; mlo, mhi = wilson(d, coh)
        t1.append([str(y), thin(int(princ[y]["fallzahl"])), f1(float(princ[y]["female_pct"])),
                   f"{float(princ[y]['mean_los_days']):.1f} ({float(princ[y]['sd_los']):.1f})",
                   thin(op), f"{op/coh*100:.1f} ({rlo:.1f}-{rhi:.1f})", str(d),
                   f"{m:.2f} ({mlo:.2f}-{mhi:.2f})"])
    wr("table1.csv", ["Year","Discharge episodes (n)","Female (%)","Mean LOS, days (SD)",
                      "Resection-associated admissions (n)","Resection-associated (%, 95% CI)",
                      "In-hospital deaths (n)","In-hospital mortality (%, 95% CI)"], t1)

    # Table 2: resection + adjunctive-technique code prevalence, 2024
    def prow(label, key):
        n = int(opsum[key]["value"]); return [label, thin(n), f"{n/Ncoh*100:.1f}"]
    t2 = [["Any meningeal tumor resection (5-015.3 or 5-015.4)", thin(either), f"{either/Ncoh*100:.1f}"],
          ["   5-015.3", thin(wo_inf), f"{wo_inf/Ncoh*100:.1f}"],
          ["   5-015.4", thin(w_inf), f"{w_inf/Ncoh*100:.1f}"],
          ["   both codes", thin(both), f"{both/Ncoh*100:.1f}"],
          prow("Microsurgical technique (5-984)", "microsurgery_5-984"),
          prow("Neuronavigation (5-988)", "navigation_any_5-988"),
          prow("Intraoperative monitoring (8-925)", "ionm_any_8-925"),
          prow("Reoperation code (5-983)", "reoperation_5-983")]
    wr("table2.csv", ["Code (OPS)","Episodes (n)","% of all D32.0 episodes"], t2)

    # figure inputs derived here (others in prepare_figure_data.py)
    dec = []
    for y in YEARS:
        coh = int(resn[y]["cohort_principal_D32.0"]); op = int(resn[y]["operative_resection_5-015.3or.4"])
        dec.append([y, op, coh-op, coh, f"{op/coh*100:.1f}"])
    with open(os.path.join(FIGDATA, "fig_resection_decomp.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["year","resection","nonresection","cohort","resection_pct"]); w.writerows(dec)

    subsite = []
    for y in YEARS:
        d0 = by[y]["D32.0"]; d1 = by[y]["D32.1"]; d9 = by[y]["D32.9"]; tot = d0+d1+d9 or 1
        subsite.append([y, f"{d0/tot*100:.2f}", f"{d1/tot*100:.2f}", f"{d9/tot*100:.2f}"])
    with open(os.path.join(FIGDATA, "fig_subsite_fraction.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["year","cranial_pct","spinal_pct","unspec_pct"]); w.writerows(subsite)

    if mortop:
        opm = op_d/op_e*100; opl, oph = wilson(op_d, op_e)
        nom = no_d/no_e*100; nol, noh = wilson(no_d, no_e)
        with open(os.path.join(FIGDATA, "fig_mortality_by_operative_2024.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["stratum","episodes","deaths","mortality_pct","ci_low","ci_high"])
            w.writerow(["Resection-associated", op_e, op_d, f"{opm:.2f}", f"{opl:.2f}", f"{oph:.2f}"])
            w.writerow(["Without resection code", no_e, no_d, f"{nom:.2f}", f"{nol:.2f}", f"{noh:.2f}"])

    prof = [("Tumor resection, any (5-015.3/.4)","resection",either),
            ("   5-015.4 (with tissue preparation)","resection",w_inf),
            ("   5-015.3 (without)","resection",wo_inf),
            ("Microsurgical technique (5-984)","technique",int(opsum["microsurgery_5-984"]["value"])),
            ("Neuronavigation (5-988)","technique",int(opsum["navigation_any_5-988"]["value"])),
            ("Intraoperative monitoring (8-925)","technique",int(opsum["ionm_any_8-925"]["value"])),
            ("Reoperation code (5-983)","other",int(opsum["reoperation_5-983"]["value"]))]
    with open(os.path.join(FIGDATA, "fig_procedure_profile_2024.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["procedure","group","pct_of_cohort"])
        for lab, g, n in prof: w.writerow([lab, g, f"{n/Ncoh*100:.1f}"])

npass = sum(1 for l in REPORT if l.startswith("[PASS"))
REPORT.insert(0, f"Verification: {npass}/{len(REPORT)} checks passed\n" + "=" * 50)
with open(os.path.join(os.path.dirname(__file__), "verification_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(REPORT) + "\n")
print("\n".join(REPORT) if REPORT else "No checks run (empty inputs).")
print("Wrote table CSVs and figure-input CSVs.")
