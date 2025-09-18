# Model Parameters Documentation

This document provides detailed information about the required parameters for each of the three risk prediction models.

## 1. CVD Risk Prediction Model

### Model Configuration
- **Input Size**: 24 features
- **Architecture**: 4-layer neural network
- **Hidden Sizes**: [31, 73, 56, 75]
- **Dropout Rate**: 0.064
- **Risk Threshold**: 0.120

### Required Parameters (24 features)

| # | Parameter Name | Test Name Mapping | Average Value | Standard Deviation |
|---|----------------|-------------------|---------------|-------------------|
| 1 | Alanine aminotransferase | alanine aminotransferase (alt/sgpt) | 22.46 | 8.89 |
| 2 | Albumin | serum albumin | 4.53 | 0.25 |
| 3 | Alkaline phosphatase | alkaline phosphatase (alp) | 81.27 | 20.57 |
| 4 | C-reactive protein | hs-crp (high sensitivity c-reactive protein) | 1.72 | 1.34 |
| 5 | Calcium | serum calcium | 9.51 | 0.35 |
| 6 | Creatinine | serum creatinine | 0.83 | 0.16 |
| 7 | Gamma glutamyltransferase | gamma glutamyl transferase (ggt) | 31.56 | 15.65 |
| 8 | Glycated haemoglobin (HbA1c) | hba1c (glycosylated hemoglobin) | 5.37 | 0.37 |
| 9 | HDL cholesterol | serum hdl cholesterol | 54.53 | 13.59 |
| 10 | Total bilirubin | serum bilirubin, (total) | 0.55 | 0.17 |
| 11 | Total protein | serum total protein | 7.25 | 0.39 |
| 12 | Urea | blood urea | 32.13 | 7.29 |
| 13 | Vitamin D | vitamin d (25 - oh vitamin d) | 19.40 | 8.22 |
| 14 | Basophill Percentage | basophils | 0.49 | 0.26 |
| 15 | Eosinophill percentage | eosinophils | 2.44 | 1.38 |
| 16 | Haemoglobin concentration | haemoglobin (hb) | 14.38 | 1.18 |
| 17 | Lymphocyte count | absolute lymphocyte count (alc) | 1.89 | 0.55 |
| 18 | Mean platelet (thrombocyte) volume | mpv | 9.32 | 1.02 |
| 19 | Monocyte count | monocytes | 0.47 | 0.15 |
| 20 | Neutrophill count | neutrophils | 4.15 | 1.23 |
| 21 | Platelet count | platelet count | 247.08 | 53.20 |
| 22 | Aspartate aminotransferase | aspartate aminotransferase (ast/sgot) | 92.43 | 22.86 |
| 23 | Total Leucocyte Count (TLC) | total leucocyte count (tlc) | 43.35 | 13.86 |
| 24 | Sex Parameter | gender field | 0.5 | 0.5 |

---

## 2. Liver Disease Risk Model

### Model Configuration
- **Input Size**: 14 features
- **Architecture**: 2-layer neural network
- **Hidden Sizes**: [92, 68]
- **Dropout Rate**: 0.089
- **Risk Threshold**: 0.16

### Required Parameters (14 features)

| # | Parameter Name | Test Name Mapping | Average Value | Standard Deviation |
|---|----------------|-------------------|---------------|-------------------|
| 1 | Gamma glutamyltransferase | gamma glutamyl transferase (ggt) | 37.52 | 40.29 |
| 2 | Aspartate aminotransferase | aspartate aminotransferase (ast/sgot) | 26.41 | 9.89 |
| 3 | Alanine aminotransferase | alanine aminotransferase (alt/sgpt) | 23.91 | 14.10 |
| 4 | Alkaline phosphatase | alkaline phosphatase (alp) | 82.24 | 24.98 |
| 5 | C-reactive protein | hs-crp (high sensitivity c-reactive protein) | 2.44 | 4.17 |
| 6 | Direct bilirubin | serum bilirubin, (direct) | 0.11 | 0.05 |
| 7 | Platelet count | platelet count(plt) | 248.15 | 58.10 |
| 8 | LDL direct | serum ldl cholesterol | 133.31 | 29.95 |
| 9 | Total protein | serum total protein | 7.25 | 0.40 |
| 10 | Monocyte count | monocytes | 0.48 | 0.21 |
| 11 | HDL cholesterol | serum hdl cholesterol | 54.87 | 14.11 |
| 12 | Mean platelet (thrombocyte) volume | mpv | 9.34 | 1.09 |
| 13 | Triglycerides | serum triglycerides | 147.09 | 82.35 |
| 14 | Sex Parameter | gender field | 0.5 | 0.5 |

---

## 3. Kidney Disease Risk Model

### Model Configuration
- **Input Size**: 17 features
- **Architecture**: 3-layer neural network
- **Hidden Sizes**: [85, 26, 113]
- **Dropout Rate**: 0.084
- **Risk Threshold**: 0.14

### Required Parameters (17 features)

| # | Parameter Name | Test Name Mapping | Average Value | Standard Deviation |
|---|----------------|-------------------|---------------|-------------------| 
| 1 | Creatinine | serum creatinine | 0.84 | 0.20 |
| 2 | Urea | blood urea | 32.37 | 8.25 |
| 3 | Glycated haemoglobin (HbA1c) | hba1c (glycosylated hemoglobin) | 5.43 | 0.61 |
| 4 | C-reactive protein | hs-crp (high sensitivity c-reactive protein) | 2.44 | 4.17 |
| 5 | HDL cholesterol | serum hdl cholesterol | 54.87 | 14.11 |
| 6 | LDL direct | serum ldl cholesterol | 133.31 | 29.95 |
| 7 | Triglycerides | serum triglycerides | 147.09 | 82.35 |
| 8 | Gamma glutamyltransferase | gamma glutamyl transferase (ggt) | 37.52 | 40.29 |
| 9 | Monocyte count | monocytes | 0.48 | 0.21 |
| 10 | Lymphocyte percentage | lymphocytes | 28.65 | 7.42 |
| 11 | Platelet count | platelet count(plt) | 248.15 | 58.10 |
| 12 | Aspartate aminotransferase | aspartate aminotransferase (ast/sgot) | 26.41 | 9.89 |
| 13 | Haemoglobin concentration | haemoglobin (hb) | 14.37 | 1.21 |
| 14 | Direct bilirubin | serum bilirubin, (direct) | 0.11 | 0.05 |
| 15 | Eosinophill percentage | eosinophils | 2.59 | 1.86 |
| 16 | Mean platelet (thrombocyte) volume | mpv | 9.34 | 1.09 |
| 17 | Sex Parameter | gender field | 0.5 | 0.5 |

---
