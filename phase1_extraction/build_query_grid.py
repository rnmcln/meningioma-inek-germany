#!/usr/bin/env python3
"""
build_query_grid.py — validate the extraction manifest against the local
ICD-10-GM and OPS catalogues, then emit the Phase-1 InEK query grid.

Outputs (written next to this script):
  - inek_query_grid.csv     concrete, provenance-ready query list
  - query_log_template.csv  empty log with the manifest's query_log_fields
  - validation_report.txt   code-validation and grid summary

Usage:
  python build_query_grid.py [--manifest extraction_manifest.yaml] [--root ..]

--root is the project folder holding the ICD/OPS catalogue subfolders
(defaults to the manifest's parent's parent, i.e. the project root).
"""
import argparse, csv, os, re, sys, itertools
from datetime import date

def load_yaml(path):
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML required: pip install pyyaml --break-system-packages")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_ops_codes(root, ref):
    """Return set of all OPS codes present in the catalogue (field 7)."""
    path = os.path.join(root, ref)
    codes = set()
    if not os.path.exists(path):
        return codes, path
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.rstrip("\n").split(";")
            if len(parts) >= 7 and parts[6]:
                codes.add(parts[6])
    return codes, path

def load_icd_codes(root, ref):
    """Return set of ICD codes present in the systematik ClaML (code=...)."""
    path = os.path.join(root, ref)
    codes = set()
    if not os.path.exists(path):
        return codes, path
    txt = open(path, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'<Class code="([^"]+)"', txt):
        codes.add(m.group(1))
    return codes, path

def ops_present(code, catalogue):
    """A manifest OPS code matches if it exists exactly, or any catalogue code
    starts with it (covers 3-digit stems like 5-032 and .0-subcode families)."""
    if code in catalogue:
        return True
    return any(c == code or c.startswith(code) for c in catalogue)

def icd_present(code, catalogue):
    if code in catalogue:
        return True
    # accept if the dotted 4-digit or its 3-digit stem is present
    stem = code.split(".")[0]
    return stem in catalogue

def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--manifest", default=os.path.join(here, "extraction_manifest.yaml"))
    ap.add_argument("--root", default=os.path.dirname(here))
    args = ap.parse_args()

    m = load_yaml(args.manifest)
    root = args.root
    report = []
    def log(s=""):
        report.append(s); print(s)

    log("="*70)
    log(f"Extraction manifest validation — study {m['study_id']} / protocol v{m['protocol_version']}")
    log(f"Manifest {m['manifest_version']}  generated {m['generated']}")
    log(f"Project root: {root}")
    log("="*70)

    # ---- validate ICD ----
    icd_cat, icd_path = load_icd_codes(root, m["icd_catalogue_ref"])
    log(f"\nICD catalogue: {os.path.basename(icd_path)}  ({len(icd_cat)} classes)"
        if icd_cat else f"\nICD catalogue NOT FOUND at {icd_path}")
    icd_codes = [p["code"] for p in m["icd_phenotypes"]] + \
                [x["code"] for x in m.get("icd_excluded_context", [])]
    icd_bad = [c for c in icd_codes if icd_cat and not icd_present(c, icd_cat)]
    for c in icd_codes:
        ok = "OK " if (icd_cat and icd_present(c, icd_cat)) else "??"
        log(f"  [{ok}] ICD {c}")

    # ---- validate OPS ----
    ops_cat, ops_path = load_ops_codes(root, m["ops_catalogue_ref"])
    log(f"\nOPS catalogue: {os.path.basename(ops_path)}  ({len(ops_cat)} codes)"
        if ops_cat else f"\nOPS catalogue NOT FOUND at {ops_path}")
    ops_codes = [o["code"] for o in m["ops_codes"]]
    ops_bad = [c for c in ops_codes if ops_cat and not ops_present(c, ops_cat)]
    for o in m["ops_codes"]:
        c = o["code"]
        ok = "OK " if (ops_cat and ops_present(c, ops_cat)) else "??"
        log(f"  [{ok}] OPS {c:9s} {o['attribution']:20s} {o['label_en'][:52]}")

    # ---- referential integrity of sets ----
    log("\nSet integrity:")
    known_icd = {p["code"] for p in m["icd_phenotypes"]}
    for name, codes in m["icd_cohorts"].items():
        miss = [c for c in codes if c not in known_icd]
        log(f"  icd_cohorts.{name}: {'OK' if not miss else 'MISSING '+str(miss)}")
    known_ops = {o["code"] for o in m["ops_codes"]}
    for name, codes in m["ops_sets"].items():
        miss = [c for c in codes if c not in known_ops]
        log(f"  ops_sets.{name}: {'OK' if not miss else 'MISSING '+str(miss)}")

    # ---- enumerate query grid ----
    inek = m["inek"]
    years = inek["years"]
    strat_priority = {s["id"]: s.get("priority", "core") for s in inek["stratifiers"]}
    rows = []
    qn = 0
    for a in inek["anchors"]:
        icd_list = m["icd_cohorts"][a["icd_cohort"]]
        ops_filter = ""
        if a.get("ops_filter_set"):
            ops_filter = "+".join(m["ops_sets"][a["ops_filter_set"]])
        dept = ""
        if a.get("department"):
            dept = inek["department_codes"][a["department"]]
        for strat in a["stratifiers"]:
            for yr in years:
                qn += 1
                rows.append({
                    "query_id": f"Q{qn:03d}",
                    "anchor_id": a["id"],
                    "cohort_label": a["label"],
                    "icd_codes": "+".join(icd_list),
                    "ops_filter": ops_filter,
                    "diagnosis_position": a["position"],
                    "department": dept,
                    "data_year": yr,
                    "stratifier": strat,
                    "priority": a.get("priority", "core"),
                    "strat_priority": strat_priority.get(strat, "core"),
                    "status": "pending",
                    "N_result": "",
                    "query_datetime": "",
                    "notes": "",
                })

    grid_path = os.path.join(here, "inek_query_grid.csv")
    cols = ["query_id","anchor_id","cohort_label","icd_codes","ops_filter",
            "diagnosis_position","department","data_year","stratifier",
            "priority","strat_priority","status","N_result","query_datetime","notes"]
    with open(grid_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

    # ---- empty query-log template ----
    log_path = os.path.join(here, "query_log_template.csv")
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(m["query_log_fields"])

    # ---- summary ----
    from collections import Counter
    by_anchor = Counter(r["anchor_id"] for r in rows)
    by_core = Counter(r["priority"] for r in rows)
    log("\n" + "="*70)
    log(f"Query grid: {len(rows)} queries across {len(inek['anchors'])} anchors x {len(years)} years")
    log("  by anchor:  " + ", ".join(f"{k}={v}" for k,v in sorted(by_anchor.items())))
    log("  by priority:" + ", ".join(f" {k}={v}" for k,v in by_core.items()))
    core_n = sum(1 for r in rows if r["priority"]=="core")
    log(f"  Phase-1 CORE queries to run first: {core_n}")
    log(f"\nWrote: {os.path.basename(grid_path)}")
    log(f"Wrote: {os.path.basename(log_path)}")

    status = "PASS" if not icd_bad and not ops_bad else "CHECK CODES"
    log(f"\nCode validation: {status}"
        + (f"  ICD unresolved={icd_bad}" if icd_bad else "")
        + (f"  OPS unresolved={ops_bad}" if ops_bad else ""))
    log("="*70)

    with open(os.path.join(here, "validation_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")

if __name__ == "__main__":
    main()
