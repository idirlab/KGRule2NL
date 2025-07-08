# ====================
# DOES NOT WORK FOR PHASE 1
# ====================



import pandas as pd
import re
import numpy as np
import time

entities_added = 0

usr_input = input("Which dataset would you like to use? (2,3): ")
rules_df = pd.read_csv(f"data/phase{usr_input}/unique_rule_types.csv")
instances_file_path = input("Enter the path to the instances file: ")
instances_df = pd.read_csv("data/instance/triples_ids.csv", header=None, names=["subjectid", "relationid", "objectid"])

# Pre-create indices for faster lookups
instances_df_indexed = instances_df.set_index(['subjectid', 'relationid', 'objectid'])
subject_index = instances_df.groupby('subjectid').indices
relation_index = instances_df.groupby('relationid').indices  
object_index = instances_df.groupby('objectid').indices

def check_df_sizes(df_arr):
    """Check if the instances exist in the instances_df."""
    return all(df.shape[0] > 0 for df in df_arr)

def find_dfs_with_common_cols(df_arr, col_name):
    """Find dataframes that contain the specified column."""
    return [i for i, df in enumerate(df_arr) if col_name in df.columns]

def update_dfs_vectorized(df_arr, dfs_to_update, col):
    """Vectorized version of update_dfs for better performance."""
    if not dfs_to_update:
        return df_arr
    
    # Find intersection of all values for the column across specified dataframes
    common_vals = set(df_arr[dfs_to_update[0]][col])
    for df_index in dfs_to_update[1:]:
        common_vals &= set(df_arr[df_index][col])
    
    # Filter all specified dataframes
    for i in dfs_to_update:
        df_arr[i] = df_arr[i][df_arr[i][col].isin(common_vals)]
    
    return df_arr

def filter_dfs_vectorized(df_arr, dfs_to_update, col, val):
    """Vectorized version of filter_dfs."""
    for i in dfs_to_update:
        df_arr[i] = df_arr[i][df_arr[i][col] == val]
    return df_arr

def get_filtered_instances(instances_df, column_idx, value):
    """Fast filtering using pre-built indices."""
    if column_idx == 0:  # subject
        return instances_df.iloc[subject_index.get(value, [])]
    elif column_idx == 1:  # relation  
        return instances_df.iloc[relation_index.get(value, [])]
    elif column_idx == 2:  # object
        return instances_df.iloc[object_index.get(value, [])]
    else:
        return instances_df

# Pre-process rules to avoid repeated string operations
processed_rules = []
for _, row in rules_df.iterrows():
    parsed_rule = row["rule"].split()  # More efficient than re.split
    parsed_rule = [x for x in parsed_rule if x != "=>"]
    processed_rules.append(parsed_rule)

instances_column = {"Instances": []}

# Track timing for progress estimation
start_time = time.time()
total_rules = len(processed_rules)

for index, parsed_rule in enumerate(processed_rules):
    instances_arr = []
    triple_vars = []
    filtered_df = instances_df.copy()

    # Progress with estimated time remaining (update every 100 iterations)
    if index % 100 == 0:
        elapsed_time = time.time() - start_time
        if index > 0:  # Avoid division by zero
            avg_time_per_rule = elapsed_time / index
            remaining_rules = total_rules - index
            estimated_remaining_time = avg_time_per_rule * remaining_rules
            
            hours = int(estimated_remaining_time // 3600)
            minutes = int((estimated_remaining_time % 3600) // 60)
            seconds = int(estimated_remaining_time % 60)
            
            progress_pct = (index / total_rules) * 100
            print(f"\rprogress: {progress_pct:6.2f}% | ETA: {hours:02d}:{minutes:02d}:{seconds:02d} ", end="")
        else:
            print(f"\rprogress: {0.00:6.2f}% | ETA: calculating... ", end="")

    # filter based on constants
    for i in range(len(parsed_rule) + 1):
        if i % 3 == 0 and i != 0:
            filtered_df.columns = triple_vars
            instances_arr.append(filtered_df.reset_index(drop=True))
            filtered_df = instances_df.copy()
            triple_vars = []

        if i < len(parsed_rule):
            rule_part = parsed_rule[i]
            if rule_part.isdigit():
                filtered_df = filtered_df[filtered_df["relationid"] == int(rule_part)]
                triple_vars.append("c")
            else:
                triple_vars.append(rule_part)

    # Find common variables in instances_arr 
    processed_cols = set()
    for df in instances_arr:
        for col in df.columns:
            if col != "c" and col not in processed_cols:
                common_df_indices = find_dfs_with_common_cols(instances_arr, col)
                instances_arr = update_dfs_vectorized(instances_arr, common_df_indices, col)
                processed_cols.add(col)

    # Generate final instances
    final_instances = []
    vars_processed = set()
    
    if check_df_sizes(instances_arr):
        for i, rule_part in enumerate(parsed_rule):
            if rule_part.isdigit():
                final_instances.append(int(rule_part))
            else:
                try:
                    val = int(instances_arr[i // 3][rule_part].iloc[0])
                    final_instances.append(val)
                    if rule_part not in vars_processed:
                        instances_arr = [df[df[rule_part] == val] if rule_part in df.columns else df for df in instances_arr]
                        vars_processed.add(rule_part)
                except (IndexError, KeyError):
                    final_instances = [pd.NA]
                    break
    else:
        final_instances = [pd.NA]

    if final_instances != [pd.NA]:
        entities_added += 1

    # Convert the array into a string and add '=>' at the appropriate index
    if len(final_instances) > 6:
        final_instances.insert(6, '=>')
    elif len(final_instances) == 6:
        final_instances.insert(3, '=>')
    
    # More efficient string joining
    final_instances_str = " ".join(str(x) for x in final_instances) if final_instances else ""
    instances_column["Instances"].append(final_instances_str if final_instances_str else pd.NA)

# Use direct assignment instead of pd.Series for better performance
rules_df["Instances"] = instances_column["Instances"]
rules_df.to_csv(f"data/rules_w_instances.csv", index=False)

print(f"\nEntities added: {entities_added}/{len(rules_df)}")
