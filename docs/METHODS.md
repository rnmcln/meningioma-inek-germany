# Methods (formulas and parameters)

No result values appear here; this document defines the computations only.

## Age standardisation (direct method, ESP2013)

Numerator age bands (Destatis, both sexes) are mapped one-to-one to five-year
standard bands; ages under one year are assigned to the 0–4 band; episodes of
unknown age are excluded. Because the resident-population source (GENESIS
12411-0005) tops out at "85 and older", the highest standard band is **85+**
with the summed 2013 European Standard Population weight **2,500**
(= 1,500 + 800 + 200).

Age-standardised rate (per 100,000), with band index *i*, standard weight *w_i*,
age-specific episode count *d_i*, age-specific population *n_i*, and
*W* = Σ *w_i*:

```
ASR = ( Σ_i  w_i * (d_i / n_i) * 1e5 ) / W
```

Poisson (Keyfitz) variance and 95% interval:

```
Var(ASR) = Σ_i ( w_i / W )^2 * ( d_i / n_i^2 ) * (1e5)^2
95% CI   = ASR ± 1.96 * sqrt(Var(ASR))
```

Because the data are national counts rather than a probability sample, these
intervals describe the stochastic uncertainty of the counts under a Poisson
model, not sampling uncertainty. No hypothesis testing is performed.

The ESP2013 weights used are the standard published values (0–4 = 5,000;
5-year bands rising to a plateau of 7,000 in the 40–54 range; declining
thereafter; 80–84 = 2,500; 85+ = 2,500 as the collapsed top band).

## Proportions

95% Wilson score interval for *k* of *n*:

```
centre = (p + z^2/2n) / (1 + z^2/n),  p = k/n,  z = 1.96
half   = z * sqrt( p(1-p)/n + z^2/4n^2 ) / (1 + z^2/n)
CI     = (centre ± half)
```

## In-hospital mortality

All-cause in-hospital death identified by **discharge reason 07** (death). The
overall and age-band mortality use the full principal-D32.0 cohort. The 2024
resection-status comparison uses:

- resection-associated = principal D32.0 + (5-015.3 or 5-015.4);
- the complement (no meningeal-resection code), derived by subtraction.

These are crude, unadjusted single-variable comparisons.

## Resection subcode inclusion–exclusion

For the two non-mutually-exclusive codes, with |A∪B| queried directly as the
union:

```
|A ∩ B| (both codes) = |A| + |B| − |A ∪ B|
```

## Cross-source concordance

For matching codes and years, ratio = InEK count / Destatis count. A pragmatic
5% reference band is used only as a visual aid in the reconciliation figure; it
is not a formal agreement criterion. Expected sources of the small, consistent
InEK excess: diagnosis-position handling, the aG-DRG grouper vintage ("grouped
by year Y+1" in the InEK delivery), and small-cell suppression.

## Denominator conventions

The rate denominator is the year-end (31 December) resident population on the
matching census basis. Population estimates from 2022 onward reflect the 2022
census; this is relevant when interpreting small changes across 2021–2022. A
sensitivity check replacing the year-end population with the mean of consecutive
year-end populations changes rates negligibly.
