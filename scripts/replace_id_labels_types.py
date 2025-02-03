import pandas as pd
import ast

# Load the files
instances_df = pd.read_excel("newcvtinstances.xlsx")
relations_df = pd.read_csv("relation2id.txt", sep=",", header=None, names=["label", "id"])
entities_df = pd.read_excel("output_distinct_newcvt_toagg.xlsx")

# Create dictionaries for mapping IDs to labels
relation_id_to_label = relations_df.set_index("id")["label"].to_dict()
entity_id_to_label = entities_df.set_index("id")["entity_label"].to_dict()
entity_id_to_types = entities_df.set_index("id")["type_labels"].to_dict()

# Convert type_labels strings to lists
def parse_type_labels(type_label_str):
    return ast.literal_eval(type_label_str)

entities_df["type_labels"] = entities_df["type_labels"].apply(parse_type_labels)

# Helper functions
def replace_ids_with_labels(rule, instance):
    # Determine rule type (short or long)
    parts = rule.split("=>")
    left_part = parts[0].strip()
    left_triples = [x for x in left_part.split(" ") if x]
    

    if len(left_triples) == 3:  # Short rule
        entity_indices = [0, 2, 4, 6]
        relation_indices = [1, 5]
    elif len(left_triples) == 6:  # Long rule
        entity_indices = [0, 2, 3, 5, 7, 9]
        relation_indices = [1, 4, 8]
    else:
        raise ValueError("Invalid rule format")

    # Replace IDs in rule
    rule_parts = rule.split()
    for i, part in enumerate(rule_parts):
        if part.startswith("?"):  # Variable entity, skip
            continue
        if i in entity_indices and int(part) in entity_id_to_label:
            rule_parts[i] = str(entity_id_to_label[int(part)])
        elif i in relation_indices and int(part) in relation_id_to_label:
            rule_parts[i] = str(relation_id_to_label[int(part)])
        

    # Replace IDs in instance
    instance_parts = instance.split()
    for i, part in enumerate(instance_parts):
        if i in entity_indices and int(part) in entity_id_to_label:
            instance_parts[i] = str(entity_id_to_label[int(part)])
        elif i in relation_indices and int(part) in relation_id_to_label:
            instance_parts[i] = str(relation_id_to_label[int(part)])

    return " ".join(rule_parts), " ".join(instance_parts)

def add_variable_types(rule, instance):
    variable_types = {}
    rule_parts = rule.split()
    instance_parts = instance.split()

    for i, part in enumerate(rule_parts):
        if part.startswith("?"):  # Variable entity
            # Match variable to corresponding instance part
            instance_id = instance_parts[i]
            if int(instance_id) in entity_id_to_types:
                variable_types[part] = entity_id_to_types[int(instance_id)]
    return variable_types

# Process each row in the instances DataFrame
rules_with_labels = []
instances_with_labels = []
variable_types_list = []

for _, row in instances_df.iterrows():
    rule = row["Rule"]
    instance = row["Instances"]

    rule_with_labels, instance_with_labels = replace_ids_with_labels(rule, instance)
    variable_types = add_variable_types(rule, instance)

    rules_with_labels.append(rule_with_labels)
    instances_with_labels.append(instance_with_labels)
    variable_types_list.append(str(variable_types))

# Add columns to the DataFrame
instances_df["Rules_with_labels"] = rules_with_labels
instances_df["Instances_with_labels"] = instances_with_labels
instances_df["Variable_types"] = variable_types_list

# Save the updated DataFrame to a new CSV
output_file = "final_newcvt.csv"
instances_df.to_csv(output_file, index=False)

print(f"Updated instances file saved to {output_file}.")
