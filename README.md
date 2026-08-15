# National trends in inpatient care for cranial meningioma in Germany, 2019–2024

Reproducibility repository for a repeated cross-sectional analysis of national
German hospital administrative data on inpatient episodes coded as benign
neoplasm of the cerebral meninges (ICD-10-GM **D32.0**).

This repository contains the **analysis code, query manifests, methodological
documentation, and input-file schemas** needed to reproduce the study. It does
**not** contain the manuscript, and it does **not** redistribute the underlying
InEK or Destatis figures (see [Data availability and licensing](#data-availability-and-licensing)).
The `*/data/` folders hold **header-only templates**; you regenerate the data
locally by running the documented queries and dropping the results into those
files.

## What the study does

Using two national administrative reporting systems, the analysis describes,
for 2019–2024:

- annual inpatient episode volume for principal diagnosis D32.0, and its
  recovery after the 2020 reduction;
- the changing composition of activity: the proportion of episodes carrying an
  attributable meningeal-resection code (OPS 5-015.3 / 5-015.4), decomposed into
  resection-associated and non-resection episode counts;
- crude and age-standardised episode rates (direct standardisation to the 2013
  European Standard Population);
- all-cause in-hospital mortality overall and by age, and a descriptive
  comparison by resection status;
- numerical concordance between InEK and Destatis discharge counts as a
  data-quality check.

A fuller narrative is in [`docs/PROJECT_SUMMARY.md`](docs/PROJECT_SUMMARY.md).

## Data sources

| Source | Role | Access |
|---|---|---|
| InEK DatenBrowser (§21 KHEntgG) | episode counts, sex, length of stay, in-hospital deaths, procedure profile | https://datenbrowser.inek.org (free registration) |
| Destatis GENESIS hospital diagnosis statistics (23131) + four-digit diagnosis reports | numerators for population-based rates | https://www-genesis.destatis.de |
| Destatis GENESIS resident population (12411-0005) | rate denominator | https://www-genesis.destatis.de |
| 2013 European Standard Population | age standardisation weights | public (Eurostat) |

## Repository layout

```
.
├── docs/                     project summary, methods, codebook, query manifest, data dictionary
├── phase1_extraction/        InEK query-grid generator + data templates
├── phase2_extraction/        Destatis query-grid generator, ASR computation, 4-digit parser + templates
├── reconciliation/           InEK vs Destatis cross-source reconciliation + templates
├── tables/                   analysis hub (build_tables.py): tidy tables + figure inputs + verification
├── figures/                  figure-data preparation and publication figure scripts
├── requirements.txt
├── CITATION.cff
└── LICENSE                   MIT (code)
```

## How to reproduce

1. **Install** Python 3.10+ and dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Regenerate the inputs.** Follow [`docs/extraction_manifest.md`](docs/extraction_manifest.md)
   to run the exact InEK and Destatis queries, and
   [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) for the expected columns.
   Save each result into the matching header-only template under `*/data/`.
3. **Compute rates and reconcile:**
   ```bash
   python phase2_extraction/compute_asr.py --year 2024        # repeat per year
   python phase2_extraction/parse_4digit_report.py            # 4-digit Destatis reports
   python reconciliation/reconcile.py
   ```
4. **Build tables and figure inputs:**
   ```bash
   python tables/build_tables.py                              # tidy tables + verification
   python figures/src/prepare_figure_data.py                  # remaining figure inputs
   ```
5. **Render figures:**
   ```bash
   python figures/RUN_ALL.py
   ```

`tables/build_tables.py` writes `tables/verification_report.txt`, which re-checks
every derived quantity against internal identities (four-digit sums equal the
three-digit total; resection subcodes obey inclusion–exclusion; mortality strata
partition the cohort; standardised rates recompute to the stored values).

## Data availability and licensing

The **code** in this repository is released under the MIT License.

The **underlying figures are not redistributed here.** InEK DatenBrowser and
Destatis GENESIS outputs are governed by the providers' own terms of use, and
their redistribution rights are not established by the authors. Both systems are
publicly accessible, and the queries needed to regenerate every value are fully
documented in `docs/extraction_manifest.md`. Destatis content, where reused, is
subject to the Data Licence Germany – attribution (dl-de/by-2-0). Small cells
(<5 cases) are suppressed at source.

## Citation

If you use this repository, please cite it via [`CITATION.cff`](CITATION.cff).
