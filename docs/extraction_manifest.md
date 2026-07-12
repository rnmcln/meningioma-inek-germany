# Extraction manifest

Exactly which queries to run to regenerate the inputs. This documents the
**parameters** of each query, not their results. Access dates should be recorded
when you run them, because online administrative outputs can be revised.

## Phase 1 — InEK DatenBrowser (https://datenbrowser.inek.org)

Register (free), then for each **data year 2019–2024** open the corresponding
**"Datenlieferung DRG {year} gruppiert nach {year+1}"** dataset and use the
**Daten-Selektion** form. Record the grouper vintage shown in the dataset title.

| # | Selection (Daten-Selektion filters) | Read from result | Saved to |
|---|---|---|---|
| A1 | Hauptdiagnose = D32.0 | Fallzahl; Geschlecht; Verweildauer (mean/SD, Kurz/Normal/Lang); PCCL; Altersklassen | `inek_D32.0_principal_2019-2024.csv`, `inek_D32.0_los_pccl_2024.csv`, `inek_D32.0_age_distribution_2024.csv` |
| A2 | Hauptdiagnose = D32.0 + Entlassungsgrund = 07 (Tod) | Fallzahl (deaths); Altersklassen; PCCL; Prozeduren tab (deaths carrying 5-015.3 / 5-015.4) | `inek_D32.0_mortality_2019-2024.csv` |
| A3 | Hauptdiagnose = D32.0 → **Prozeduren** tab (all rows) | procedure prevalence for the 2024 cohort | `inek_D32.0_procedures_2024.csv`, `inek_D32.0_operative_summary_2024.csv` |
| A4 | Hauptdiagnose = D32.0 + Prozedur = {5-015.3, 5-015.4} (multi-select = union) | Fallzahl (= resection-associated cohort); sex; LOS; PCCL; Altersklassen | `inek_D32.0_resection_trend_2019-2024.csv`, `inek_D32.0_resection_subcodes_2024.csv`, `inek_D32.0_resection_cohort_2024.csv` |
| A5 | Hauptdiagnose = D32.0 + Prozedur = {5-015.3, 5-015.4} + Entlassungsgrund = 07 | Fallzahl (= operative deaths) | `inek_D32.0_mortality_by_operative_2024.csv` |
| A6 | Hauptdiagnose = D32.0 + Prozedur = {5-988.0 … 5-988.4} (union) | Fallzahl (= any-navigation) | `inek_D32.0_navigation_union_2024.csv` |
| A7 | Hauptdiagnose = {D32.0, D32.1, D32.9} (broad three-digit) | Fallzahl | `inek_A4_broad_D32_2019-2024.csv` |

Multi-selecting several codes within one Prozedur filter applies **OR** logic
(union); the separate "weitere Prozedur" field applies **AND** logic.

## Phase 2 — Destatis GENESIS (https://www-genesis.destatis.de)

| # | Table / report | Selection | Saved to |
|---|---|---|---|
| B1 | 23131-0001 (hospital diagnoses, three-digit) | ICD D32; Germany; principal diagnosis; years 2019–2024 | `destatis_23131-0001_meningeal_3digit.csv` |
| B2 | Four-digit diagnosis reports ("Tiefgegliederte / Statistischer Bericht Diagnosedaten") | D32.0/.1/.9 (and D42.0, C70.0 for context) by sex and age band; per year | `destatis_4digit_meningeal_2019-2024_totals.csv`, `destatis_4digit_meningeal_2024.csv`, `destatis_D32.0_agesex_2019-2024.csv` |
| B3 | 12411-0005 (population, single year of age) | Germany; 31 December reference date; years 2019–2024 | `12411-0005_de_flat_more-years.csv` (repository root) |

`phase2_extraction/parse_4digit_report.py` parses the downloaded four-digit
Excel reports into the tidy CSVs above (the four-digit split is not available
from the 23131 online cube).

## Notes

- The four-digit report format differs by year (a tidy "SB" sheet in later
  years; dotless codes in a `Geschlecht_Anzahl` sheet in earlier years); the
  parser handles both.
- GENESIS exports only the currently selected years; select all six.
- Record the retrieval date for each query.
