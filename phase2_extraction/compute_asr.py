#!/usr/bin/env python3
"""
compute_asr.py — crude and age-standardised (ESP2013) episode rate for the
primary cohort (principal D32.0), both sexes combined.

Inputs (auto-detected in the project root / data folder):
  - numerator : phase2_extraction/data/destatis_D32.0_agesex_2019-2024.csv
  - denominator: GENESIS 12411-0005 flat CSV (Deutschland, Stichtag, Altersjahre)

Notes / choices (stated for reproducibility):
  - Denominator uses the year-end Bevölkerungsstand (31.12.YYYY); a single-year
    rate approximation. 2024 population is on the 2022-Census basis, matching the
    2024 numerator (no rebasing mismatch).
  - 12411-0005 tops out at "85 Jahre und mehr", so the highest band is 85+ with
    the summed ESP2013 weight 2500 (=1500+800+200). Numerator 85-89/90-94/95+ are
    collapsed into 85+ to match. A finer top band needs a 90+/95+ population source.
  - ASR variance via the Poisson (Keyfitz) approximation; 95% CI = ASR +/- 1.96*SE.

Usage: python compute_asr.py [--year 2024] [--pop <flatcsv>]
"""
import argparse, csv, re, math, os, glob

ESP2013 = {"0-4":5000,"5-9":5500,"10-14":5500,"15-19":5500,"20-24":6000,"25-29":6000,
 "30-34":6500,"35-39":7000,"40-44":7000,"45-49":7000,"50-54":7000,"55-59":6500,
 "60-64":6000,"65-69":5500,"70-74":5000,"75-79":4000,"80-84":2500,"85+":2500}
BANDS = list(ESP2013.keys())

def band(a): return "85+" if a >= 85 else f"{(a//5)*5}-{(a//5)*5+4}"
def val(x):
    s = str(x).strip()
    if s in ("-","","...",".","x","/"): return 0
    s = s.replace(".","").replace(",","")
    return int(s) if s.lstrip("-").isdigit() else 0

def main():
    here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2024)
    ap.add_argument("--pop", default=None)
    ap.add_argument("--num", default=os.path.join(here,"data","destatis_D32.0_agesex_2019-2024.csv"))
    a = ap.parse_args()
    popfile = a.pop or next(iter(sorted(
        glob.glob(os.path.join(root,"*12411-0005*flat*.csv")) or glob.glob(os.path.join(root,"*12411*.csv")),
        key=os.path.getmtime, reverse=True)), None)
    if not popfile or not os.path.exists(popfile):
        raise SystemExit("12411-0005 flat CSV not found in project root.")

    # numerator
    numer = {b:0 for b in BANDS}
    for r in csv.DictReader(open(a.num, encoding="utf-8")):
        if r["year"] != str(a.year): continue
        l = r["age_band"].strip().lower()
        m = re.match(r"(\d+)", l)
        b = "0-4" if "unter 1" in l else (band(int(m.group(1))) if m else None)
        if b: numer[b] += val(r["N"])

    # denominator (year-end population by single year of age)
    pop = {b:0 for b in BANDS}; stag = f"{a.year}-12-31"; matched = 0
    for p in csv.reader(open(popfile, encoding="utf-8-sig"), delimiter=";"):
        if len(p) < 14 or p[4] != stag: continue
        lab = p[12].strip().lower()
        if "unter 1" in lab: age = 0
        elif "und mehr" in lab: age = 85
        else:
            m = re.search(r"(\d+)", lab); age = int(m.group(1)) if m else None
        if age is None: continue
        pop[band(age)] += val(p[13]); matched += 1
    if not matched: raise SystemExit(f"No population rows for {stag}.")

    cases = sum(numer.values()); P = sum(pop.values()); W = sum(ESP2013.values())
    crude = cases/P*1e5
    asr = sum((numer[b]/pop[b]*1e5)*ESP2013[b] for b in BANDS if pop[b])/W
    se = math.sqrt(sum((ESP2013[b]/W)**2*(numer[b]/pop[b]**2)*(1e5**2) for b in BANDS if pop[b]))
    lo, hi = asr-1.96*se, asr+1.96*se

    print(f"Primary cohort D32.0 — {a.year} (principal diagnosis, both sexes)")
    print(f"  population (31.12.{a.year}): {P:,}")
    print(f"  episodes:                 {cases}")
    print(f"  crude rate:               {crude:.2f} /100,000")
    print(f"  ASR (ESP2013):            {asr:.2f} /100,000  (95% CI {lo:.2f}-{hi:.2f})")
    out = os.path.join(here,"data",f"D32.0_ASR_{a.year}.csv")
    with open(out,"w",newline="",encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["band","cases","population","age_specific_per100k","esp2013_weight"])
        for b in BANDS: w.writerow([b,numer[b],pop[b],round(numer[b]/pop[b]*1e5,3) if pop[b] else 0,ESP2013[b]])
        w.writerow([]); w.writerow(["crude_per100k",round(crude,3)])
        w.writerow(["asr_esp2013_per100k",round(asr,3)]); w.writerow(["asr_95ci",f"{lo:.3f}-{hi:.3f}"])
    print(f"  wrote {out}")

if __name__ == "__main__":
    main()
