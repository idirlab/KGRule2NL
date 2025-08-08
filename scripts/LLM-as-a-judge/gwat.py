import numpy as np
import pandas as pd

def gwets_ac2(data, num_categories=5, weighting='quadratic'):
    """
    Computes Gwet's AC2 coefficient for inter-rater reliability.

    Args:
        data (np.ndarray): A 2D NumPy array where rows represent items and
                           columns represent annotators' ratings.
        num_categories (int): The total number of possible categories/scores.
                              For a 1-5 scale, this is 5.
        weighting (str): The weighting scheme to use.
                         'unweighted': All disagreements are treated equally.
                         'quadratic': Disagreements are weighted quadratically,
                                      suitable for ordinal scales.

    Returns:
        float: The calculated Gwet's AC2 coefficient.
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)

    if data.ndim != 2:
        raise ValueError("Input data must be a 2D array (items x annotators).")

    # Check for NaN values and remove rows with any NaN
    if np.isnan(data).any():
        print("Warning: Found NaN values in data. Removing rows with NaN values.")
        data = data[~np.isnan(data).any(axis=1)]
        if len(data) == 0:
            raise ValueError("No valid data remaining after removing NaN values.")

    num_items, num_annotators = data.shape

    if num_annotators < 2:
        raise ValueError("Gwet's AC2 requires at least 2 annotators.")

    # For float values, we'll discretize them for the weight matrix calculation
    # but use actual values for agreement computation
    min_val, max_val = 1.0, 5.0
    
    # Validate scores are within the defined range
    if np.min(data) < min_val or np.max(data) > max_val:
        print(f"Warning: Some scores are outside the expected range [{min_val}, {max_val}]")

    # --- 1. Define Weight Matrix (w_kl) for discretized categories ---
    weights_matrix = np.zeros((num_categories, num_categories))
    if weighting == 'unweighted':
        # Unweighted: w_kl = 1 if k=l, 0 otherwise
        np.fill_diagonal(weights_matrix, 1)
    elif weighting == 'quadratic':
        # Quadratic weighting: w_kl = 1 - ((k-l)^2 / (C-1)^2)
        for k in range(num_categories):
            for l in range(num_categories):
                if num_categories > 1:
                    weights_matrix[k, l] = 1 - ((k - l)**2 / (num_categories - 1)**2)
                else:
                    weights_matrix[k, l] = 1
    else:
        raise ValueError("Invalid weighting scheme. Choose 'unweighted' or 'quadratic'.")

    # --- 2. Calculate Observed Agreement (Pa) ---
    Pa_sum = 0.0
    
    for i in range(num_items):
        item_ratings = data[i, :]
        
        # Calculate observed agreement for this item using continuous values
        Pa_i = 0.0
        num_pairs = 0
        
        # For each pair of annotators
        for j1 in range(num_annotators):
            for j2 in range(j1 + 1, num_annotators):
                rating1 = item_ratings[j1]
                rating2 = item_ratings[j2]
                
                # Convert continuous ratings to discrete categories for weight lookup
                cat1 = min(int(np.round(rating1)) - 1, num_categories - 1)
                cat2 = min(int(np.round(rating2)) - 1, num_categories - 1)
                cat1 = max(0, cat1)  # Ensure non-negative
                cat2 = max(0, cat2)  # Ensure non-negative
                
                Pa_i += weights_matrix[cat1, cat2]
                num_pairs += 1
        
        # Average over all pairs for this item
        if num_pairs > 0:
            Pa_i /= num_pairs
        else:
            Pa_i = 1.0  # Perfect agreement if only one annotator
            
        Pa_sum += Pa_i
    
    Pa = Pa_sum / num_items

    # --- 3. Calculate Expected Agreement (Pe) ---
    # Calculate the overall proportion of ratings for each category
    all_ratings_flat = data.flatten()
    
    # Convert continuous ratings to discrete categories for proportion calculation
    discrete_ratings = []
    for rating in all_ratings_flat:
        cat = min(int(np.round(rating)) - 1, num_categories - 1)
        cat = max(0, cat)  # Ensure non-negative
        discrete_ratings.append(cat)
    
    # Calculate proportions for each category
    pi_k_proportions = np.zeros(num_categories)
    for cat in discrete_ratings:
        pi_k_proportions[cat] += 1
    pi_k_proportions /= len(discrete_ratings)

    # Calculate expected agreement
    Pe = 0.0
    for k in range(num_categories):
        for l in range(num_categories):
            Pe += weights_matrix[k, l] * pi_k_proportions[k] * pi_k_proportions[l]

    # --- 4. Calculate Gwet's AC2 ---
    if abs(1 - Pe) < 1e-10:  # Use small epsilon for floating point comparison
        ac2 = 1.0
    else:
        ac2 = (Pa - Pe) / (1 - Pe)

    return ac2

# --- Main Analysis for Your Data ---
if __name__ == "__main__":
    excel_file_path = 'judge_gemini_3tries.xlsx'

    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path)
        
        print(f"--- Gwet's AC2 Analysis for Inter-Annotator Agreement ---")
        print(f"File: {excel_file_path}")
        print(f"Total instances loaded: {len(df)}")
        
        # Check if required columns exist
        required_columns = ['Annotator_correctness', 'Avg_judge']
        if not all(col in df.columns for col in required_columns):
            available_cols = list(df.columns)
            raise ValueError(f"Required columns {required_columns} not found. "
                           f"Available columns: {available_cols}")

        # Extract the two annotator columns
        annotator_data = df[required_columns].values
        
        print(f"\nData Overview:")
        print(f"Shape: {annotator_data.shape} (instances x annotators)")
        print(f"Columns analyzed: {required_columns}")
        
        # Show basic statistics for each annotator
        print(f"\nAnnotator Statistics:")
        for i, col_name in enumerate(required_columns):
            col_data = annotator_data[:, i]
            print(f"{col_name}:")
            print(f"  Min: {np.min(col_data):.3f}")
            print(f"  Max: {np.max(col_data):.3f}")
            print(f"  Mean: {np.mean(col_data):.3f}")
            print(f"  Std: {np.std(col_data):.3f}")
        
        # Check for missing values
        if np.isnan(annotator_data).any():
            nan_count = np.isnan(annotator_data).sum()
            print(f"\nWarning: Found {nan_count} NaN values in the data")
        
        # Show first few rows
        print(f"\nFirst 5 instances:")
        print("Annotator_correctness | Avg_judge")
        print("-" * 35)
        for i in range(min(5, len(annotator_data))):
            print(f"{annotator_data[i, 0]:>18.3f} | {annotator_data[i, 1]:>8.3f}")

        # Calculate Gwet's AC2 with quadratic weighting (recommended for ordinal data)
        print(f"\n--- Gwet's AC2 Results ---")
        ac2_quadratic = gwets_ac2(annotator_data, num_categories=5, weighting='quadratic')
        print(f"Gwet's AC2 (Quadratic Weighting): {ac2_quadratic:.4f}")

        # Calculate Gwet's AC2 with unweighted agreement
        ac2_unweighted = gwets_ac2(annotator_data, num_categories=5, weighting='unweighted')
        print(f"Gwet's AC2 (Unweighted): {ac2_unweighted:.4f}")

        # Calculate simple correlation for comparison
        correlation = np.corrcoef(annotator_data[:, 0], annotator_data[:, 1])[0, 1]
        print(f"Pearson Correlation (for comparison): {correlation:.4f}")

        # Interpretation
        print(f"\n--- Interpretation ---")
        print(f"Gwet's AC2 values range from -1 to 1:")
        print(f"  < 0.00: Poor agreement (worse than chance)")
        print(f"  0.01-0.20: Slight agreement")
        print(f"  0.21-0.40: Fair agreement") 
        print(f"  0.41-0.60: Moderate agreement")
        print(f"  0.61-0.80: Substantial agreement")
        print(f"  0.81-1.00: Almost perfect agreement")
        
        # Provide specific interpretation for your results
        if ac2_quadratic < 0:
            interpretation = "Poor agreement (worse than chance)"
        elif ac2_quadratic <= 0.20:
            interpretation = "Slight agreement"
        elif ac2_quadratic <= 0.40:
            interpretation = "Fair agreement"
        elif ac2_quadratic <= 0.60:
            interpretation = "Moderate agreement"
        elif ac2_quadratic <= 0.80:
            interpretation = "Substantial agreement"
        else:
            interpretation = "Almost perfect agreement"
            
        print(f"\nYour Result: {interpretation}")
        
        # Additional insights
        print(f"\n--- Additional Insights ---")
        mean_diff = np.mean(np.abs(annotator_data[:, 0] - annotator_data[:, 1]))
        print(f"Mean Absolute Difference: {mean_diff:.3f}")
        
        # Count instances where annotators agree within different thresholds
        for threshold in [0.1, 0.25, 0.5, 1.0]:
            agreement_count = np.sum(np.abs(annotator_data[:, 0] - annotator_data[:, 1]) <= threshold)
            percentage = (agreement_count / len(annotator_data)) * 100
            print(f"Agreement within ±{threshold}: {agreement_count}/100 ({percentage:.1f}%)")

    except FileNotFoundError:
        print(f"Error: The file '{excel_file_path}' was not found.")
        print("Please ensure the Excel file exists in the same directory.")
    except ValueError as e:
        print(f"Error processing Excel data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()