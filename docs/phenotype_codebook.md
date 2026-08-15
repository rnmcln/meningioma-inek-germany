# Phenotype codebook (ICD-10-GM and OPS)

Public classification codes used to define the cohort and procedures. No study
result values appear here.

## Diagnosis (ICD-10-GM)

| Code | Description | Role |
|---|---|---|
| D32.0 | Benign neoplasm of cerebral meninges | **Primary cohort** (cranial) |
| D32.1 | Benign neoplasm of spinal meninges | Broader comparison phenotype (D32) |
| D32.9 | Benign neoplasm of meninges, unspecified | Broader comparison phenotype (D32) |
| D42.0 | Neoplasm of uncertain behaviour, cerebral meninges | Outside benign scope (context only) |
| C70.0 | Malignant neoplasm of cerebral meninges | Outside benign scope (context only) |

The three-digit **D32** group = D32.0 + D32.1 + D32.9.

## Procedures (OPS)

| Code | Description | Role |
|---|---|---|
| 5-015.3 | Excision/destruction of diseased meningeal tissue, tumour, without infiltration of intracranial tissue | Attributable meningeal resection |
| 5-015.4 | Excision/destruction of diseased meningeal tissue, tumour, with preparation of infiltrated adjacent tissue | Attributable meningeal resection |
| 5-015.0 / 5-015.1 | Excision/destruction of intracerebral tumour (brain-derived / non-brain-derived) | Recorded, **not** counted as meningeal resection |
| 5-017.1 | Resection of cranial-nerve tumour | Recorded, **not** counted as meningeal resection |
| 5-984 | Microsurgical technique | Adjunctive technique (cohort prevalence) |
| 5-988.0–.4 | Use of a navigation system (radiological / electromagnetic / sonographic / optical / radar-reflector) | Adjunctive technique; reported as the **union** of subcodes |
| 8-925 | Intraoperative neurophysiological monitoring (duration bands) | Adjunctive technique |
| 5-983 | Reoperation | Presence of code during the episode; **not** linked to the index resection |
| 5-010.00 | Craniotomy of the calvaria (single access subcode) | Access (supplementary/exploratory) |
| 5-021.0 | Reconstruction of the meninges: duraplasty at the convexity | Dural repair (supplementary/exploratory) |
| 8-522.91 | Intensity-modulated radiotherapy with image guidance (inpatient) | Exploratory radiotherapy floor (single code) |

Notes:

- The 5-015.3 vs 5-015.4 distinction is a **procedural coding** distinction and
  must not be read as histological brain invasion or WHO grade.
- 5-015.3 and 5-015.4 are **not mutually exclusive** at the episode level.
- ICD behaviour categories (D32 vs D42 vs C70) are administrative recording
  categories and are **not** proxies for WHO grade.
- Where a single access or dural-repair subcode is queried, that exact subcode is
  reported; it is not the sum of all subcodes in its category.
- OPS and ICD-10-GM catalogues are revised annually; the definitions of 5-015.3
  and 5-015.4 were stable across 2019–2024.
