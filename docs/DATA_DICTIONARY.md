# Data dictionary

Expected columns for each input file. The repository ships these as
**header-only templates** under `*/data/`; populate them with locally
regenerated query results (see `extraction_manifest.md`). No values are shipped.

## Phase 1 — InEK (`phase1_extraction/data/`)

| File | Columns |
|---|---|
| `inek_D32.0_principal_2019-2024.csv` | year, dataset, fallzahl, female_pct, male_pct, mean_los_days, sd_los, source |
| `inek_D32.0_mortality_2019-2024.csv` | year, cohort_N, in_hospital_deaths, mortality_pct, mortality_95ci, death_cohort_mean_los, death_cohort_pct_80plus |
| `inek_D32.0_resection_trend_2019-2024.csv` | year, cohort_principal_D32.0, operative_resection_5-015.3or.4, resection_share_pct |
| `inek_D32.0_operative_summary_2024.csv` | measure, numerator, denominator, value, pct, note |
| `inek_D32.0_procedures_2024.csv` | category, ops_code, label_en, faelle, pct_of_cohort |
| `inek_D32.0_resection_subcodes_2024.csv` | category, ops_codes, episodes_N, pct_of_cohort, note (categories: either_resection, both_resection, resection_5-015.3_any, resection_5-015.4_any, …) |
| `inek_D32.0_mortality_by_operative_2024.csv` | stratum, definition, episodes_N, in_hospital_deaths, source_note (strata: operative, non_operative, total) |
| `inek_D32.0_resection_cohort_2024.csv` | stratum, N, female_pct, male_pct, mean_los, sd_los, age_lt65_pct, age_65_74_pct, age_75_79_pct, age_80plus_pct, source_note (strata: resection_associated, full_cohort) |
| `inek_D32.0_los_pccl_2024.csv` | cohort, measure, value, unit, source_note |
| `inek_D32.0_navigation_union_2024.csv` | measure, ops_codes, episodes_N, pct_of_cohort, note |
| `inek_D32.0_age_distribution_2024.csv` | band, cohort_pct, deaths_pct (bands: <65, 65-74, 75-79, 80+) |
| `inek_A4_broad_D32_2019-2024.csv` | year, dataset, icd_codes, fallzahl, female_pct, mean_los, destatis_3digit_D32, ratio_inek_destatis |

## Phase 2 — Destatis (`phase2_extraction/data/`)

| File | Columns |
|---|---|
| `D32.0_ASR_trend.csv` | year, episodes, population, crude_per100k, asr_esp2013_per100k, asr_ci_low, asr_ci_high, population_basis |
| `D32.0_ASR_2024.csv` | band, cases, population, age_specific_per100k, esp2013_weight |
| `destatis_23131-0001_meningeal_3digit.csv` | genesis_table, icd_code, icd_label_en, measure, region, position, year, N, retrieved, source_url, notes |
| `destatis_4digit_meningeal_2019-2024_totals.csv` | year, icd_code, sex, N_total_all_ages, position |
| `destatis_4digit_meningeal_2024.csv` | source, icd_code, sex, age_group, year, N, position |
| `destatis_D32.0_agesex_2019-2024.csv` | year, icd_code, sex, age_band, N, position |

## Reconciliation (`reconciliation/`)

| File | Columns |
|---|---|
| `phase_counts_long.csv` | system, key, icd, position, year, N, suppressed, source_ref |
| `reconciliation_report.csv` | comparison, label, year, N_inek, N_destatis, ratio_inek_over_destatis, abs_diff, pct_diff, status |

## Population (repository root)

`12411-0005_de_flat_more-years.csv` — GENESIS 12411-0005 flat CSV export,
semicolon-delimited. The scripts read the reference-date column (matching
`YYYY-12-31`), the single-year-of-age label column, and the count column. Keep
the file as exported from GENESIS.
