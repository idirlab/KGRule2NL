import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error
import krippendorff

# === Config ===
file_path = "judge_gemini_3tries.xlsx"  # Replace if needed
annotator_col = "Annotator_correctness"
avg_judge_col = "Avg_judge"

# === Load Data ===
df = pd.read_excel(file_path)

# === Check Columns ===
if annotator_col not in df.columns or avg_judge_col not in df.columns:
    raise ValueError(f"Columns '{annotator_col}' or '{avg_judge_col}' not found in the file.")

# Convert columns to float (no rounding)
annotator_scores = df[annotator_col].astype(float).values
avg_judge_scores = df[avg_judge_col].astype(float).values

# === Metrics ===

# 1. Krippendorff's Alpha (interval level)
alpha_data = np.array([annotator_scores, avg_judge_scores])
kripp_alpha_interval = krippendorff.alpha(reliability_data=alpha_data, level_of_measurement='interval')

# 2. Spearman correlation
spearman_corr, spearman_p = spearmanr(annotator_scores, avg_judge_scores)

# 3. Pearson correlation
pearson_corr, pearson_p = pearsonr(annotator_scores, avg_judge_scores)

# 4. Mean Absolute Difference
mad = mean_absolute_error(annotator_scores, avg_judge_scores)

# === Output ===
print("=== Agreement Between Annotator and avg_judge ===")
print(f"Krippendorff's Alpha (interval): {kripp_alpha_interval:.4f}")
print(f"Spearman Correlation: {spearman_corr:.4f} (p = {spearman_p:.4f})")
print(f"Pearson Correlation: {pearson_corr:.4f} (p = {pearson_p:.4f})")
print(f"Mean Absolute Difference (MAD): {mad:.4f}")
