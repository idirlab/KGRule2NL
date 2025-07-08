import pandas as pd
import re

def process_rule_part(part):
    """Process a rule part: normalize whitespace, split, and replace digits with 'c'"""
    normalized = re.sub(r'\s+', ' ', part).strip()
    tokens = normalized.split(' ')
    return ['c' if token.isdigit() else token for token in tokens]

def format_df(df):
    
    # Split rules into left and right parts
    rule_parts = df['rule'].str.split('=>', expand=True)
    
    my_df = pd.DataFrame({
        'left': rule_parts[0].apply(process_rule_part),
        'right': rule_parts[1].apply(process_rule_part)
    })

    # Format as rule strings: join list elements with spaces and combine left/right with =>
    my_df['formatted_rule'] = my_df.apply(lambda row: ' '.join(row['left']) + ' => ' + ' '.join(row['right']), axis=1)

    return my_df



if __name__ == '__main__':
    df = pd.read_csv('data/instance/biokg_all_rules.csv')
    
    formatted_df = format_df(df)

    # Create a new csv file with unique rules
    unique_rules_df = pd.DataFrame(formatted_df['formatted_rule'].unique(), columns=['rule'])
    unique_rules_df.to_csv('data/unique_rule_types.csv', index_label='id')

   
    print("Unique rules saved to data/unique_rule_types.csv")
