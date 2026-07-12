#!/usr/bin/env python3
"""
build_destatis_grid.py — validate the Phase-2 Destatis/GBE manifest against the
local ICD-10-GM catalogue and emit the extraction grid.

Outputs (written next to this script):
  - destatis_extraction_grid.csv   concrete extraction-task list
  - coding_era_ledger_template.csv one row per year, to be filled
  - destatis_query_log_template.csv log with the manifest's query_log_fields
  - validation_report.txt          validation and grid summary

Usage:
  python build_destatis_grid.py [--manifest destatis_manifest.yaml] [--root ..]
"""
import argparse, csv, os, re, sys

def load_yaml(path):
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML required: pip install pyyaml --break-system-packages")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_icd_codes(root, ref):
    path = os.path.join(root, ref)
    codes = set()
    if not os.path.exists(path):
        return codes, path
    txt = open(path, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'<Class code="([^"]+)"', txt):
        codes.add(m.group(1))
    return codes, path

def icd_present(code, catalogue):
    if code in catalogue:
        return True
    return code.split(".")[0] in catalogue

def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--manifest", default=os.path.join(here, "destatis_manifest.yaml"))
    ap.add_argument("--root", default=os.path.dirname(here))
    args = ap.parse_args()

    m = load_yaml(args.manifest)
    root = args.root
    def clean(s):
        return re.sub(r"\s+", " ", str(s or "")).strip()
    report = []
    def log(s=""):
        report.append(s); print(s)

    log("="*70)
    log(f"Destatis Phase-2 manifest validation — study {m['study_id']} / protocol v{m['protocol_version']}")
    log(f"Manifest {m['manifest_version']}  generated {m['generated']}")
    log(f"Window (nominal): {m['window']['nominal_start']}-{m['window']['nominal_end']}")
    log("="*70)

    # ---- validate ICD codes (3- and 4-digit) ----
    icd_cat, icd_path = load_icd_codes(root, m["icd_catalogue_ref"])
    log(f"\nICD catalogue: {os.path.basename(icd_path)}  ({len(icd_cat)} classes)"
        if icd_cat else f"\nICD catalogue NOT FOUND at {icd_path}")
    three = [x["code"] for x in m["icd_three_digit"]]
    four  = [x["code"] for x in m["icd_four_digit"]]
    bad = []
    for c in three + four:
        ok = icd_cat and icd_present(c, icd_cat)
        if not ok: bad.append(c)
        log(f"  [{'OK ' if ok else '??'}] ICD {c}")

    # ---- enumerate extraction grid ----
    rows = []
    tn = 0
    yr_range = f"{m['window']['nominal_start']}-{m['window']['nominal_end']}"
    for s in m["destatis"]["sources"]:
        gran = s["granularity"]
        codes = three if gran == "icd_3digit" else (four if gran == "icd_4digit" else [""])
        table = s.get("genesis_table") or s.get("publication") or ""
        for code in codes:
            tn += 1
            rows.append({
                "task_id": f"T{tn:03d}",
                "source_id": s["id"],
                "genesis_table": table,
                "icd_code": code,
                "granularity": gran,
                "role": s["role"],
                "region_scope": ("bundesland" if "BL" in s["id"] or "residence" in s["role"] else "national"),
                "year_range": yr_range,
                "priority": s.get("priority", "core"),
                "verify": clean(s.get("verify_at_extraction", "")),
                "status": "pending",
                "N_or_status": "",
                "retrieved_datetime": "",
                "notes": clean(s.get("note", "")),
            })
    # population + standard populations + optional context (no ICD dimension)
    for group in ("population_sources", "standard_populations", "optional_context"):
        for s in m["destatis"].get(group, []):
            tn += 1
            rows.append({
                "task_id": f"T{tn:03d}",
                "source_id": s["id"],
                "genesis_table": s.get("genesis_table", s.get("source", "")),
                "icd_code": "",
                "granularity": s.get("granularity", group),
                "role": s["role"],
                "region_scope": ("bundesland" if "BL" in s["id"] else "national"),
                "year_range": yr_range,
                "priority": s.get("priority", "core"),
                "verify": clean(s.get("verify_at_extraction", "")),
                "status": "pending",
                "N_or_status": "",
                "retrieved_datetime": "",
                "notes": clean(s.get("note", "")),
            })

    cols = ["task_id","source_id","genesis_table","icd_code","granularity","role",
            "region_scope","year_range","priority","verify","status",
            "N_or_status","retrieved_datetime","notes"]
    grid_path = os.path.join(here, "destatis_extraction_grid.csv")
    with open(grid_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

    # ---- coding-era ledger template (one row per year) ----
    led_path = os.path.join(here, "coding_era_ledger_template.csv")
    with open(led_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(m["coding_era_ledger_fields"])
        for y in range(m["window"]["nominal_start"], m["window"]["nominal_end"] + 1):
            row = [y] + [""] * (len(m["coding_era_ledger_fields"]) - 1)
            w.writerow(row)

    # ---- query-log template ----
    log_path = os.path.join(here, "destatis_query_log_template.csv")
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(m["query_log_fields"])

    from collections import Counter
    by_prio = Counter(r["priority"] for r in rows)
    by_gran = Counter(r["granularity"] for r in rows)
    log("\n" + "="*70)
    log(f"Extraction grid: {len(rows)} tasks")
    log("  by priority:  " + ", ".join(f"{k}={v}" for k,v in by_prio.items()))
    log("  by granularity:" + ", ".join(f" {k}={v}" for k,v in by_gran.items()))
    core = sum(1 for r in rows if r["priority"] == "core")
    log(f"  CORE tasks to run first: {core}")
    log(f"\nWrote: {os.path.basename(grid_path)}")
    log(f"Wrote: {os.path.basename(led_path)}  ({m['window']['nominal_end']-m['window']['nominal_start']+1} year rows)")
    log(f"Wrote: {os.path.basename(log_path)}")
    log(f"\nCode validation: {'PASS' if not bad else 'CHECK '+str(bad)}")
    log("="*70)

    with open(os.path.join(here, "validation_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")

if __name__ == "__main__":
    main()
