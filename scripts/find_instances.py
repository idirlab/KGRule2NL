import pandas as pd
import re
import numpy as np

# usr_input = input("Which dataset would you like to use? (1,2,3): ")
entities_added = 0
# rules_df = pd.read_csv(f"data/phase{usr_input}/unique_rule_types.csv")
rules_df = pd.read_csv(f"data/instance/unique_rule_types.csv")
# instances_file_path = input("Enter the path to the instances file: ")
instances_df = pd.read_csv("data/instance/triples_ids.csv", header=None, names=["subjectid", "relationid", "objectid"])

instances_column = {"Instances": []}

def check_tuple_exists(tuple):
    return instances_df[(instances_df["subjectid"] == tuple[0]) &
                        (instances_df["relationid"] == tuple[1]) &
                        (instances_df["objectid"] == tuple[2])].shape[0] > 0


def check_df_sizes(df_arr):
    """Check if the instances exist in the instances_df."""
    for df in df_arr:
        if df.shape[0] == 0:
            return False
    return True


def find_dfs_with_common_cols(df_arr, col_name):
    df_list = []
    for i in range(len(df_arr)):
        if col_name in df_arr[i].columns:
            df_list.append(i)
    return df_list


def update_dfs(df_arr, dfs_to_update, col):
    common_vals = set(df_arr[dfs_to_update[0]][col])
    for df_index in dfs_to_update:
        common_vals &= set(df_arr[df_index][col])

    for i in dfs_to_update:
        df_arr[i] = df_arr[i][df_arr[i][col].isin(common_vals)]

    return df_arr


def filter_dfs(df_arr, dfs_to_update, col, val):
    for i in dfs_to_update:
        df_arr[i] = df_arr[i][df_arr[i][col] == val]

    return df_arr


for index, row in rules_df.iterrows():
    instances_arr = []
    triple_vars = []  # don't set equal to instances_arr, it will add it to the array
    variables_dict = {}
    filtered_df = instances_df.copy()

    # get parsed rule
    print(f"\rprogress: {((index+1)/len(rules_df))*100:6.2f}% ", end="| ")
    parsed_rule = re.split(r"\s+", row["rule"])  # get rid of spaces
    parsed_rule = [x for x in parsed_rule if x != "=>"]  # get rid of arrow

    # filter df based on constants
    for i in range(len(parsed_rule) + 1):
        if i % 3 == 0 and i != 0:
            filtered_df.columns = triple_vars
            instances_arr.append(filtered_df.reset_index(drop=True))
            filtered_df = instances_df.copy()
            triple_vars = []

        if i < len(parsed_rule) and parsed_rule[i].isdigit():
            filtered_df = filtered_df[filtered_df.iloc[:, i % 3] == int(
                parsed_rule[i])]
            triple_vars.append("c")
        elif i < len(parsed_rule):
            triple_vars.append(parsed_rule[i])

    # Find common variables in instances_arr
    processed_cols = set()
    for df in instances_arr:
        for col in df.columns:
            if col != "c" and not col in processed_cols:
                instances_arr = update_dfs(instances_arr, find_dfs_with_common_cols(instances_arr, col), col)
                processed_cols.add(col)

    # make final string for export to csv
    final_instances = []
    vars = set()
    for i, rule in enumerate(parsed_rule):
        if check_df_sizes(instances_arr):

            if rule.isdigit():
                final_instances.append(int(rule))
            else:
                val = int(instances_arr[i // 3][rule].iloc[0])
                final_instances.append(val if len(
                    instances_arr[i // 3]) > 0 else pd.NA)
                if rule not in vars:
                    instances_arr = filter_dfs(
                        instances_arr, find_dfs_with_common_cols(instances_arr, rule), rule, val)
                    vars.add(rule)

            if i % 3 == 0 and i != 0 and not check_tuple_exists(final_instances[i-3:i]):
                final_instances[i-3:i] = [pd.NA, pd.NA, pd.NA]
        else:
            final_instances = [pd.NA]

    if final_instances != [pd.NA]:
        entities_added += 1

    # Convert the array into a string and add '=>' at the appropriate index
    if len(final_instances) > 6:
        final_instances.insert(6, '=>')
    elif len(final_instances) == 6:
        final_instances.insert(3, '=>')
    final_instances_str = " ".join(map(str, final_instances))

    instances_column["Instances"].append(
        final_instances_str if final_instances else pd.NA)

rules_df["Instances"] = pd.Series(instances_column["Instances"])


rules_df.to_csv(f"data/rules_w_instances.csv", index=False)

print(f"\nEntities added: {entities_added}/{len(rules_df)}")
