
import pandas as pd

def load_entity_to_id(file_path):
    """
    Load the entity to ID mapping from a file.
    Now the file is in the format: label, entityID
    """
    label_to_id = {}
    with open(file_path, 'r') as file:
        for line in file:
            label, entity_id = line.strip().split(',')
            label_to_id[entity_id] = label  # Map entity ID to label
    return label_to_id

def parse_instances(instances, rule_type):
    """
    Parse the instances based on the rule type.
    Returns a set of distinct entity IDs.
    """
    entity_ids = set()
    
    # Split the instances based on the rule type
    if rule_type == "Type 1":
        parts = instances.split(" => ")
        entity_ids.update(parts[0].split()[:3:2])  # entityID1, entityID2
        entity_ids.update(parts[1].split()[:3:2])  # entityID3, entityID4
    elif rule_type == "Type 2":
        parts = instances.split(" => ")
        entity_ids.update(parts[0].split()[:5:2])  # entityID1, entityID2, entityID3
        entity_ids.update(parts[1].split()[:5:2])  # entityID5, entityID6

    return entity_ids

def process_excel_and_generate_output(excel_file, entity_to_id_file, output_file):
    """
    Process the Excel file, parse instances, and output a file with distinct entity IDs and labels.
    """
    # Load the entity-to-ID mapping (now we have label-to-id)
    label_to_id = load_entity_to_id(entity_to_id_file)
    
    # Read the Excel file
    df = pd.read_excel(excel_file, engine='openpyxl')

    
    # Create a set to store distinct entity IDs
    all_entity_ids = set()
    
    # Loop through each row in the dataframe
    for index, row in df.iterrows():
        rule_type = row['Type']
        instances = row['Instances']
        
        # Parse instances based on the rule type
        entity_ids = parse_instances(instances, rule_type)
        
        # Add the parsed entity IDs to the set
        all_entity_ids.update(entity_ids)
    
    # Open the output file to write the results
    with open(output_file, 'w') as out_file:
        for entity_id in sorted(all_entity_ids):
            # Get the label for the entity_id (if available)
            label = label_to_id.get(entity_id, 'Unknown')  # Default to 'Unknown' if not found
            out_file.write(f"{entity_id},{label}\n")

# Example usage:
excel_file = 'fb+cvt-music-75-w-instances.xltx'  # Replace with your actual Excel file path
entity_to_id_file = 'entity2id.txt'  # Replace with the path to your entity-to-ID file
output_file = 'distinct_entities_pluscvt.txt'  # The file where the result will be saved

process_excel_and_generate_output(excel_file, entity_to_id_file, output_file)
