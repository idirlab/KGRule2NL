# Process the triples and split triples into domains (each domain as a file)
def process_files(relation_file, binarrels_file, output_file, data_file):
    # Read the relations and map IDs to their labels
    id_to_label = {}
    with open(relation_file, 'r') as rel_file:
        for line in rel_file:
            line = line.strip()
            if not line:
                continue
            label, id_str = line.rsplit(',', 1)  
            id_to_label[id_str.strip()] = label.strip()

    # Read the IDs from the second file and write the output
    # This part is needed for only processing binary relations
    """with open(binarrels_file, 'r') as bin_file, open(output_file, 'w') as out_file:
        for line in bin_file:
            line = line.strip()
            if not line:
                continue
            id_str = line.strip()
            if id_str in id_to_label:
                label = id_to_label[id_str]
                domain = label.split('/')[1] if '/' in label else 'unknown'
                out_file.write(f"{id_str}, {label}, {domain}\n")"""

    # Categorize triples into domain files
    domain_to_file = {}
    with open(data_file, 'r') as data_file_obj:
        for line in data_file_obj:
            line = line.strip()
            if not line:
                continue
            subject_id, relation_id, object_id = line.split(',')
            relation_id = relation_id.strip()
            if relation_id in id_to_label:
                label = id_to_label[relation_id]
                domain = label.split('/')[1] if '/' in label else 'unknown'

                # Open a file for this domain if not already opened
                if domain not in domain_to_file:
                    domain_to_file[domain] = open(f"{domain}.txt", 'w')

                # Write the triple to the domain file
                domain_to_file[domain].write(f"{subject_id},{relation_id},{object_id}\n")

    # Close all opened domain files
    for file in domain_to_file.values():
        file.close()

# Define file names
relation_file = 'relation2id.txt'
binarrels_file = 'binaryrelation_ids.txt'
output_file = 'binaryrelation_label_domain.txt'
data_file = 'dataCVT.txt'

# Process the files
process_files(relation_file, binarrels_file, output_file, data_file)

print(f"Processing completed. Results saved in {output_file} and domain-specific files.")
