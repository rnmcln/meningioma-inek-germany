#!/usr/bin/env python3
"""
reconcile.py — cross-source consistency assessment (Protocol v2.0, Section 7.7).

Reads the pre-registered InEK-vs-Destatis comparison pairs from the Phase-2
manifest and a tidy per-year counts file, then reports the count ratio, absolute
difference and percentage divergence per overlapping year. This is a CONSISTENCY
assessment, not a validation: the two sources share administrative reporting, so
agreement is coherence, not confirmation against clinical truth.

Inputs
------
--manifest  : phase2_extraction/destatis_manifest.yaml  (defines compare pairs,
              overlapping years and the definitional differences to map)
--counts    : phase_counts_long.csv (tidy long counts; see schema below).
              Falls back to phase_counts_long.example.csv if the real file is absent.

Counts schema (one row per system x series x year):
  system   : inek | destatis
  key      : InEK anchor id (A1, A4, ...) OR Destatis source id (KH_DE_3d_basic, ...)
  icd      : the code the count refers to (D32, D32.0, ...)
  position : principal | principal_or_secondary
  year     : integer
  N        : integer count (blank/'' if suppressed/unavailable)
  suppressed : yes/no
  source_ref : provenance (GENESIS table + query datetime, or InEK query id)

Outputs
-------
  reconciliation_report.csv   per comparison x year
  reconciliation_summary.md   readable summary with definitional caveats
"""
import argparse, csv, os, sys

def load_yaml(path):
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML required: pip install pyyaml --break-system-packages")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_counts(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

def to_int(v):
    v = (v or "").strip().replace(".", "").replace(",", "")
    return int(v) if v.isdigit() else None

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest",
                    default=os.path.join(root, "phase2_extraction", "destatis_manifest.yaml"))
    ap.add_argument("--counts", default=os.path.join(here, "phase_counts_long.csv"))
    args = ap.parse_args()

    counts_path = args.counts
    if not os.path.exists(counts_path):
        alt = os.path.join(here, "phase_counts_long.example.csv")
        if os.path.exists(alt):
            print(f"[info] {os.path.basename(counts_path)} not found; using example data ({os.path.basename(alt)}).")
            counts_path = alt
        else:
            sys.exit(f"No counts file at {counts_path} and no example available.")

    m = load_yaml(args.manifest)
    cs = m["cross_source_consistency"]
    years = cs["overlapping_years"]
    pairs = cs["compare"]
    caveats = cs["definitional_differences_to_map"]
    rows = load_counts(counts_path)

    # index counts: (system, key, icd, position, year) -> (N, suppressed, ref)
    idx = {}
    for r in rows:
        k = (r["system"].strip(), r["key"].strip(), r["icd"].strip(),
             r["position"].strip(), str(r["year"]).strip())
        idx[k] = (to_int(r.get("N")), (r.get("suppressed", "").strip().lower() == "yes"),
                  r.get("source_ref", ""))

    out = []
    for i, p in enumerate(pairs, 1):
        d = p["destatis"]; k = p["inek"]
        cmp_id = f"CMP{i}"
        label = f"InEK[{k['anchor']} {k.get('cohort','')}/{k['position']}] vs Destatis[{d['source']} {d['code']}/{d['position']}]"
        for y in years:
            ik = idx.get(("inek", k["anchor"], _inek_icd(k), k["position"], str(y)))
            dk = idx.get(("destatis", d["source"], d["code"], d["position"], str(y)))
            n_inek = ik[0] if ik else None
            n_dest = dk[0] if dk else None
            ratio = round(n_inek / n_dest, 4) if (n_inek and n_dest) else ""
            absdiff = (n_inek - n_dest) if (n_inek is not None and n_dest is not None) else ""
            pct = round((n_inek - n_dest) / n_dest * 100, 2) if (n_inek and n_dest) else ""
            out.append({
                "comparison": cmp_id, "label": label, "year": y,
                "N_inek": n_inek if n_inek is not None else "",
                "N_destatis": n_dest if n_dest is not None else "",
                "ratio_inek_over_destatis": ratio,
                "abs_diff": absdiff, "pct_diff": pct,
                "status": _status(n_inek, n_dest, ik, dk),
            })

    rep = os.path.join(here, "reconciliation_report.csv")
    cols = ["comparison","label","year","N_inek","N_destatis",
            "ratio_inek_over_destatis","abs_diff","pct_diff","status"]
    with open(rep, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)

    # markdown summary
    md = []
    md.append("# Cross-source consistency assessment\n")
    md.append(f"Source counts: `{os.path.basename(counts_path)}`  |  overlapping years: {years[0]}-{years[-1]}\n")
    md.append("> Consistency assessment, not validation. InEK and Destatis draw on overlapping "
              "hospital administrative reporting; agreement reflects shared source data and shared "
              "coding limitations. Interpret ratios as coherence.\n")
    for i, p in enumerate(pairs, 1):
        cmp_id = f"CMP{i}"
        sub = [r for r in out if r["comparison"] == cmp_id]
        md.append(f"\n## {cmp_id}: {sub[0]['label']}\n")
        md.append("| Year | N InEK | N Destatis | Ratio | Δ | % diff | Status |")
        md.append("|---|---|---|---|---|---|---|")
        for r in sub:
            md.append(f"| {r['year']} | {r['N_inek']} | {r['N_destatis']} | "
                      f"{r['ratio_inek_over_destatis']} | {r['abs_diff']} | {r['pct_diff']} | {r['status']} |")
        vals = [r["ratio_inek_over_destatis"] for r in sub if isinstance(r["ratio_inek_over_destatis"], float)]
        if vals:
            md.append(f"\nMean ratio {round(sum(vals)/len(vals),4)} (min {min(vals)}, max {max(vals)}), n={len(vals)} years.")
        else:
            md.append("\nNo complete year pairs yet — populate the counts file.")
    md.append("\n## Definitional differences to map before interpreting divergence\n")
    for c in caveats:
        md.append(f"- {c}")
    md.append("")
    with open(os.path.join(here, "reconciliation_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    complete = sum(1 for r in out if r["ratio_inek_over_destatis"] != "")
    print(f"Comparisons: {len(pairs)} x {len(years)} years = {len(out)} cells; "
          f"{complete} with a computable ratio.")
    print(f"Wrote: reconciliation_report.csv, reconciliation_summary.md")

def _inek_icd(k):
    # informational icd label for the InEK side, by anchor
    return {"A1": "D32.0", "A4": "D32"}.get(k["anchor"], "")

def _status(ni, nd, ik, dk):
    if ni is None and nd is None: return "both missing"
    if ni is None: return "InEK missing"
    if nd is None: return "Destatis missing"
    if (ik and ik[1]) or (dk and dk[1]): return "suppressed cell present"
    pct = abs(ni - nd) / nd * 100 if nd else 0
    return "concordant (<10%)" if pct < 10 else ("moderate (10-25%)" if pct < 25 else "divergent (>25%)")

if __name__ == "__main__":
    main()
