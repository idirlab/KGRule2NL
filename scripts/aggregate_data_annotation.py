import pandas as pd
import openpyxl

def check_choices(devins_choice, nasims_choice, drLis_choice):
    # since dr Li did the least and devin did the second least amount of annotations
    unanimous = True
    choices = [choice for choice in [devins_choice, nasims_choice, drLis_choice] if not pd.isna(choice)]
    aggregate_choices = []
    
    # Calculate main_choice
    if choices:
        main_choice = round(sum(choices) / len(choices))
    else:
        main_choice = None  # or some default value if all choices are NaN
    
    # Check if choices match main_choice
    if devins_choice == main_choice:
        aggregate_choices.append('devin')
    if nasims_choice == main_choice:
        aggregate_choices.append('nasim')
    if drLis_choice == main_choice: 
        aggregate_choices.append('drLi')

    if any(choice != main_choice for choice in choices) or choices == []:
        unanimous = False

    print(choices, unanimous, main_choice)

    return aggregate_choices, main_choice, unanimous

def numerize_strs(df, columns):
    columns.append('which explanation 1 or 2 ')
    for column in columns:
        if column in df.columns and df[column].dtype == 'object':
            df[column] = pd.to_numeric(df[column], errors='coerce')

    columns.remove('which explanation 1 or 2 ')
    return df

def aggregate_row(aggregate_choices, main_choice, columns_to_aggregate, unanimous, index):
    aggregated_values = {}
    aggregated_values['id'] = drLis_annotations.iloc[index]['id']

    drLis_value = drLis_annotations.iloc[index] if 'drLi' in aggregate_choices else None
    devins_value = devins_annotations.iloc[index] if 'devin' in aggregate_choices else None
    nasims_value = nasims_annotations.iloc[index] if 'nasim' in aggregate_choices else None

    aggregated_values['which explanation 1 or 2 '] = main_choice
    aggregated_values['Unanimous'] = unanimous  # Add Unanimous directly as a boolean value

    # Add all the columns to be aggregated
    for column in columns_to_aggregate:
        values = []
        if devins_value is not None:
            values.append(devins_value[column])
        if nasims_value is not None:
            values.append(nasims_value[column])
        if drLis_value is not None:
            values.append(drLis_value[column])
        
        # Calculate the mean, ignoring None values
        aggregated_values[column] = pd.Series(values).mean()

    # Make sure the Series matches the columns of aggregated_annotations
    return pd.Series(aggregated_values, index=aggregated_annotations.columns)

if __name__ == '__main__':
    # Process annotations
    devins_annotations = pd.read_excel('annotations/Devin.xlsx').dropna(subset=['instance']).reset_index(drop=True)
    nasims_annotations = pd.read_excel('annotations/Nasim.xlsx').dropna(subset=['instance']).rename(columns={'is the rule meaningful 1-3': 'is the rule logically sound? (1-3)', 
                                                                                                             '# missed entities': '# missing entities', '#  missed relations':'#  missing relationships',
                                                                                                             '# extra relations': '# extra relationships'}).reset_index(drop=True)
    drLis_annotations = pd.read_excel('annotations/DrLi.xlsx').dropna(subset=['instance']).rename(columns={'is the rule logically (sound)? 1-3': 'is the rule logically sound? (1-3)'}).reset_index(drop=True)

    columns_to_aggregate = ['which explanation 1 or 2 ', '# missing entities', '#  missing relationships',
                            '# extra entities', '# extra relationships', 'correctness 1-5 ', 'clarity 1-5 ', 'is the rule logically sound? (1-3)']
    
    # Convert string columns to numeric values
    numerize_strs(devins_annotations, columns_to_aggregate)
    numerize_strs(nasims_annotations, columns_to_aggregate)
    numerize_strs(drLis_annotations, columns_to_aggregate)

    # Remove columns that are not part of the aggregation
    aggregated_annotations = devins_annotations.copy().drop(columns=['Rule', 'instance', 'explanation1_s', 'explanation2_y'])
    aggregated_annotations['Unanimous'] = None

    # Iterate through rows and aggregate
    for index, row in aggregated_annotations.iterrows():
        drLis_choice = drLis_annotations.iloc[index]['which explanation 1 or 2 '] if drLis_annotations.iloc[index]['which explanation 1 or 2 '] else None
        devins_choice = devins_annotations.iloc[index]['which explanation 1 or 2 '] if devins_annotations.iloc[index]['which explanation 1 or 2 '] else None
        nasims_choice = nasims_annotations.iloc[index]['which explanation 1 or 2 '] if nasims_annotations.iloc[index]['which explanation 1 or 2 '] else None

        aggregate_choices, main_choice, unanimous = check_choices(devins_choice, nasims_choice, drLis_choice)

        # Use .loc instead of .iloc for row assignment by index and column names
        aggregated_annotations.loc[index] = aggregate_row(aggregate_choices, main_choice, columns_to_aggregate, unanimous, index)

    # Clean up column names
    aggregated_annotations.columns = [col.strip() for col in aggregated_annotations.columns]
    aggregated_annotations.columns = [col.replace("  ", ' ') for col in aggregated_annotations.columns]

    # Save to CSV
    aggregated_annotations.to_excel('annotations/aggregated_annotations.xlsx', index=False)
