import pandas as pd
from scipy.stats import spearmanr, pearsonr

# Load CSV
df = pd.read_csv("correlation.csv")  # Replace with your file name

# Define metrics and judge models
metrics = ["correctness2", "clarity2", "correctness3", "clarity3"]
judges = ["gpt", "gem"]

# Compute and display correlations
for metric in metrics:
    human_col = f"{metric}"
    print(f"\n=== {metric.upper()} ===")
    for judge in judges:
        judge_col = f"{metric}-{judge}"
        
        # Drop rows with missing values (optional)
        data = df[[human_col, judge_col]].dropna()
        human_scores = data[human_col]
        judge_scores = data[judge_col]

        # Spearman correlation
        spearman_corr, _ = spearmanr(human_scores, judge_scores)
        # Pearson correlation
        pearson_corr, _ = pearsonr(human_scores, judge_scores)

        print(f"{judge.upper()} as judge:")
        print(f"  Spearman: {spearman_corr:.3f}")
        print(f"  Pearson : {pearson_corr:.3f}")
