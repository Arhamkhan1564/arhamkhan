# ASK-T2D: Open, Cost-Aware Diabetes Screening Methods Pilot

**Research status (2026-11-24):** This public repository contains a completed scikit-learn diabetes-progression methods pilot and an NHANES screening benchmark *implementation*. NHANES benchmark results are **not yet available**: CDC downloads failed from the execution environment. The regression pilot is NOT evidence of diabetes diagnosis/screening performance.

## Research question
Can simple measurement acquisition policies improve prediction of HbA1c-defined diabetes-range status among adults reporting no known diabetes, and does a policy selected on one survey cycle transport to a later, non-overlapping NHANES cycle?

## Dataset and protections
- Development: NHANES 2015–2016; temporal evaluation: NHANES 2017–March 2020 pre-pandemic.
- Retain adults age >=20, HbA1c result available, and DIQ010 == 2 (self-reported no diabetes).
- Label: HbA1c >= 6.5%; HbA1c never used as a predictor.
- Candidate predictors: age, sex, BMI, waist circumference; no diagnostic glucose variables.
- Report AUROC, average precision, Brier score, log loss; choose optional feature by validation Brier only.

## Run
```bash
pip install -r research/ASK-T2D/requirements.txt
python research/ASK-T2D/nhanes_pilot.py
```
The program downloads public CDC XPT data into ignored `data/`. It writes `results/nhanes_results.json` only after genuine execution.

## What has and has not been established
- **Executed earlier:** independent small-scale scikit-learn diabetes *progression* regression demonstration (n=442); 30 repeated random splits (correlated).
- **Not yet executed:** NHANES temporal screening benchmark. No NHANES AUROC, clinical validation, cost savings, adaptive individual test selection, or safety claims should be made.
- **Not clinically deployable:** no survey-weighted prevalence inference, diagnostic approval, patient follow-up, or clinical evaluation.

## Provenance
CDC NHANES public data, retrieved at runtime. Original analysis code prepared for the ASK-T2D exploratory proposal. Do not upload patient-identifiable information. This folder is temporarily hosted within an existing GitHub account repository because new repository creation is not available through the connected integration.
