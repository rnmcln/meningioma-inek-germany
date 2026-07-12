# Project summary

A deep description of the study design, data, and analytical pipeline. This
document deliberately contains **no result values** and is **not** the
manuscript.

## 1. Objective and estimand

The study is a descriptive, repeated cross-sectional analysis of national German
inpatient administrative data for 2019–2024. The unit of analysis is the
**discharge episode** (not the individual patient; readmissions are counted
separately). The primary phenotype is a hospital discharge episode with a
**principal diagnosis of ICD-10-GM D32.0** (benign neoplasm of the cerebral
meninges), which in routine German coding predominantly represents benign
cranial meningioma but does not confirm histology and excludes tumours coded as
uncertain (D42.0) or malignant (C70.0) behaviour.

The study characterises:

1. **Volume and rates** — annual episode counts and crude/age-standardised
   episode rates, and the trajectory across the 2020 pandemic year.
2. **Composition** — the proportion of episodes carrying an attributable
   meningeal-resection code, decomposed into absolute resection-associated and
   non-resection counts, plus adjunctive-technique code prevalence.
3. **Mortality** — all-cause in-hospital mortality overall, by age band, and by
   resection status (descriptive only).
4. **Data quality** — numerical concordance of InEK and Destatis discharge
   counts, and the site-composition of the three-digit D32 group.

The design does not support inference about patient-level incidence, treatment
probability, surgical selection, operative risk, or outcomes beyond discharge.

## 2. Data sources and their distinct roles

- **InEK DatenBrowser (§21 KHEntgG).** Publishes aggregate query results from
  the case-level data all German hospitals submit under the Hospital
  Remuneration Act. Provides the cohort counts and all hospital-process measures
  (sex, length-of-stay categories, complexity level, in-hospital deaths via
  discharge reason 07, and the diagnosis/procedure distributions). Cells with
  fewer than five cases are suppressed at source.
- **Destatis GENESIS hospital diagnosis statistics (23131) and four-digit
  diagnosis reports.** Provide the **numerators for population-based rates**,
  because the age- and sex-specific national distributions required for
  standardisation are published here rather than in the DatenBrowser.
- **Destatis GENESIS resident population (12411-0005).** Rate **denominator**,
  taken at the 31 December reference date on the matching census basis.

Because the rate numerators are Destatis counts and the cohort/process measures
are InEK counts, the two are reported separately; a small, consistent difference
between them is expected and is examined as a reconciliation exercise, not as
external validation.

## 3. Phenotype and procedure definitions

See [`phenotype_codebook.md`](phenotype_codebook.md) for the full ICD-10-GM and
OPS code list. Key definitions:

- **Primary cohort:** principal diagnosis D32.0.
- **Broader comparison phenotype:** three-digit D32 (D32.0 + spinal D32.1 +
  unspecified D32.9).
- **Resection-associated episode:** a principal-D32.0 episode carrying OPS
  **5-015.3** (excision without infiltration of intracranial tissue) or
  **5-015.4** (excision with preparation of infiltrated adjacent tissue). This
  is a procedural coding distinction and is **not** evidence of histological
  brain invasion or WHO grade. The two codes are not mutually exclusive.
- **Not counted as meningeal resection:** intracerebral tumour codes
  (5-015.0/.1) and cranial-nerve tumour resection (5-017.1).
- **Adjunctive-technique and other codes** (microsurgery 5-984; neuronavigation
  5-988, taken as the union of subcodes; intraoperative monitoring 8-925;
  reoperation 5-983) are tabulated as prevalence across the whole cohort — they
  are cohort-level code prevalences, not proportions of resections.

## 4. Analytical methods

See [`METHODS.md`](METHODS.md) for the formulas. In brief:

- **Rates:** direct age standardisation to the 2013 European Standard
  Population; because the population source tops out at "85 and older", the
  highest band is 85+ with the summed standard weight 2,500. Confidence
  intervals use the Poisson (Keyfitz) variance. Episodes of unknown age are
  excluded from standardisation.
- **Proportions:** 95% Wilson intervals.
- **Mortality:** all-cause in-hospital death (discharge reason 07). For 2024,
  additionally examined by resection status; single-variable comparisons only,
  because the aggregate outputs return one marginal distribution per query and do
  not support joint stratification.
- **Cross-source concordance:** ratio of InEK to Destatis principal-diagnosis
  counts for matching codes and years.
- **No hypothesis testing** is performed; the data approximate a national census
  and results are reported as absolute and relative differences with their
  precision.

## 5. Software pipeline

```
extraction (documented queries)  ->  */data/*.csv (regenerated locally)
   |
   ├─ phase2_extraction/compute_asr.py         crude + ASR per year (ESP2013)
   ├─ phase2_extraction/parse_4digit_report.py  parse four-digit Destatis reports
   ├─ reconciliation/reconcile.py               InEK vs Destatis ratios
   ├─ tables/build_tables.py                     tidy tables + figure inputs + verification
   └─ figures/src/prepare_figure_data.py         remaining figure inputs
          |
          └─ figures/RUN_ALL.py                  publication figures (SVG/PDF/PNG)
```

Every derived value is recomputed from the input counts and cross-checked by the
verification block in `build_tables.py`.

## 6. Reporting

The analysis follows the RECORD extension of the STROBE statement for studies
using routinely collected health data.
