import pandas as pd
import re


def task1(df):
    count_df = pd.read_csv('unique_rule_types.csv')

    unique_rules = df['formatted_rule'].unique()
    count_df['left_count'] = 0
    count_df['right_count'] = 0
    count_df['total_count'] = 0
    left_rules_dict = {rule: 0 for rule in unique_rules}
    right_rules_dict = {rule: 0 for rule in unique_rules}
    total_rules_dict = {rule: 0 for rule in unique_rules}
    
    for _, row in df.iterrows():
        
        rule = row['formatted_rule']
        left_desc = row['left_desc']
        right_desc = row['right_desc']

        left_rules_dict[rule] += sum(desc.count('.') for desc in left_desc)

        if any('.' in desc for desc in right_desc):
            right_rules_dict[rule] += 1

        total_rules_dict[rule] += len(row['left_desc']) + len(row['right_desc'])


    # Update count_df with the final values from the dictionaries
    count_df['left_count'] = count_df['rule'].map(left_rules_dict)
    count_df['right_count'] = count_df['rule'].map(right_rules_dict)
    count_df['total_count'] = count_df['rule'].map(total_rules_dict)

    count_df['left_percentage'] = (count_df['left_count'] / count_df['total_count']) * 100
    count_df['right_percentage'] = (count_df['right_count'] / count_df['total_count']) * 100


    return count_df


def task1_forRawDf(df):
    count_df = pd.DataFrame()

    count_df['rule'] = df['Rule']
    unique_rules = df['Rule']
    count_df['left_count'] = 0
    count_df['right_count'] = 0
    left_rules_dict = {rule: 0 for rule in unique_rules}
    right_rules_dict = {rule: 0 for rule in unique_rules}
    
    for index, row in df.iterrows():
        rule = row['Rule']
        left_desc = row['left_desc']
        right_desc = row['right_desc']

        # Check for '.' in left_desc
        left_rules_dict[rule] += sum(desc.count('.') for desc in left_desc)

        # Check for '.' in right_desc
        if any('.' in desc for desc in right_desc):
            right_rules_dict[rule] += 1



    # Update count_df with the final values from the dictionaries
    count_df['left_count'] = count_df['rule'].map(left_rules_dict)
    count_df['right_count'] = count_df['rule'].map(right_rules_dict)

    return count_df


def task2(df):
    # Collect unique rules
    unique_rules = df['full_rule'].unique()
    rules_dict = {rule: idx for idx, rule in enumerate(unique_rules, start=1)}

    rules_df = pd.DataFrame.from_dict(rules_dict, orient='index', columns=['rule'])
    rules_df.reset_index(inplace=True)

    rules_df.rename(columns={'index': 'rule', 'rule': 'id'}, inplace=True)
    rules_df.to_csv('rules_with_desc.csv', index=False)

    return rules_dict



def format_df(df):
    my_df = pd.DataFrame()
    my_df['left'] = df['Rule'].apply(lambda rule: re.split(r'=>', rule)[0])
    my_df['right'] = df['Rule'].apply(lambda rule: re.split(r'=>', rule)[-1])

    my_df['left_desc'] = my_df['left'].apply(lambda part: extract_desc(part))
    my_df['right_desc'] = my_df['right'].apply(lambda part: extract_desc(part))

    my_df['left'] = my_df['left'].apply(lambda part: part.strip())
    my_df['right'] = my_df['right'].apply(lambda part: part.strip())

    my_df['left'] = my_df['left'].apply(lambda part: re.sub(r'\s+', ' ', part).strip())
    my_df['right'] = my_df['right'].apply(lambda part: re.sub(r'\s+', ' ', part).strip())

    my_df['full_rule'] = my_df['left'] + ' => ' + my_df['right']

    my_df = add_formatted_rule(my_df)

    my_df.to_csv('formatted_rules.csv', index_label='id')

    return my_df


def add_formatted_rule(df):
    def format_rule(row):
        left_vars = remove_descs(row['left'], row['left_desc'])
        right_vars = remove_descs(row['right'], row['right_desc'])
        left_vars_cleaned = ' '.join(left_vars.split())
        right_vars_cleaned = ' '.join(right_vars.split())
        return f"{left_vars_cleaned} => {right_vars_cleaned}"

    df['formatted_rule'] = df.apply(format_rule, axis=1)
    return df

def extract_vars(part):
    return re.findall(r'\?\w+', part)

def remove_underscore_words(part):
    # Remove words connected to underscores
    return re.sub(r'_\w+\b', '', part)

def extract_desc(part):
    # for rule desc to be included in the list
    all_descs = re.findall(r'/[a-zA-Z0-9_/.\-]+/+', part)
    all_descs = re.findall(r'/[a-zA-Z0-9_/.\-]+', part)
    filtered_descs = [desc for desc in all_descs if not re.search(r'/./', desc)]
    return filtered_descs

def replace_consts(part):
    pattern = r'/[a-zA-Z0-9]/[a-zA-Z0-9_]+'
    replacement = 'c'
    return re.sub(pattern, replacement, part)

def remove_descs(part, descs):
    for desc in descs:
        part = part.replace(" " + desc, '')
    return part

if __name__ == '__main__':
    df = pd.read_csv('updated_rules.csv')
    
    formatted_df = format_df(df)

    # Create a new csv file with unique rules
    unique_rules_df = formatted_df.rename(columns={'full_rule': 'rule'})
    unique_rules_df['rule'] = unique_rules_df.apply(lambda row: remove_descs(row['rule'], row['left_desc']), axis=1).apply(lambda row: replace_consts(row))
    unique_rules_df['rule'] = unique_rules_df.apply(lambda row: remove_descs(row['rule'], row['right_desc']), axis=1).apply(lambda row: replace_consts(row))
    unique_rules_df['rule'] = unique_rules_df['rule'].apply(remove_underscore_words)
    unique_rules_df = unique_rules_df.drop(columns=['left', 'right', 'left_desc', 'right_desc', 'formatted_rule'])
    unique_rules_df = unique_rules_df.drop_duplicates()
    unique_rules_df.reset_index(drop=True, inplace=True)
    unique_rules_df.index = unique_rules_df.index + 1
    unique_rules_df.to_csv('unique_rule_types.csv', index_label='id')

    df.reset_index(inplace=True)
    formatted_df.reset_index(inplace=True)

    merged_df = df.merge(formatted_df[['index', 'left_desc', 'right_desc', 'formatted_rule']], on='index', how='left')
    merged_df.drop(columns=['index'], inplace=True)

    counted_df = task1_forRawDf(merged_df)
    merged_df['id'] = merged_df.index + 1  
    counted_df['id'] = counted_df.index + 1  
    merged_df = pd.merge(merged_df, counted_df[['id', 'left_count', 'right_count']], on='id', how='left')
    merged_df.drop(columns=['id', 'left_desc', 'right_desc'], inplace=True)
    merged_df.rename(columns={'left_count': 'left_concat_count', 'right_count': 'right_concat_count', 'formatted_rule': 'rule_type'}, inplace=True)
    rule_type_to_id = task2(formatted_df)
    merged_df['rule_type'] = merged_df['rule_type'].map(rule_type_to_id)
    merged_df.to_csv('new_updated_rules.csv', index=False)



    #get statistics on the rules
    print("Statistics: \n")
    print(task1(formatted_df))
    print("""
           
    ========================
          
    """)
    # print the unique rule types
    print(unique_rules_df)
