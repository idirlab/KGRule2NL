import pandas as pd
import re

def get_all_instances(df: pd.DataFrame, rule):
    mask = df['rule'] == rule
    filtered_df = df[mask].drop_duplicates(subset=['full_instance'])
    return list(zip(filtered_df['head'], filtered_df['tail']))


def replace_consts(part):
    pattern = r'/[a-zA-Z0-9]/[a-zA-Z0-9_]+'
    replacement = 'c'
    return re.sub(pattern, replacement, part)

if __name__ == '__main__':
    instances_df = pd.read_csv('instances.csv')
    instances_df['full_instance'] = instances_df['head'] + " " + instances_df['rule'] + " " + instances_df['tail']
    unique_rules_df = pd.read_csv('rules_with_desc.csv')
    rule_types_df = pd.read_csv('unique_rule_types.csv')  

    unique_rules = unique_rules_df['rule'].unique()
    unique_rules_dict = {rule: '' for rule in unique_rules}

    instances_set = set(instances_df.apply(lambda row: (row['head'], row['rule'], row['tail']), axis=1))

    rule_types_dict = {row['rule']: row['id'] for _, row in rule_types_df.iterrows()}

    for rule in unique_rules:
        left_rel = rule.split('=>')[0].strip()
        right_rel = rule.split('=>')[1].strip()

        left_parts = left_rel.split(' ')
        right_parts = right_rel.split(' ')

        if len(left_parts) == 3:
            rule_type = left_parts[0] + " " + left_parts[2] + " => " + right_parts[0] + " " + right_parts[2]
            rule_id = rule_types_dict[replace_consts(rule_type)] 

            left_rule = left_parts[1]
            right_rule = right_parts[1]

            left_instances = get_all_instances(instances_df, left_rule)
            right_instances = get_all_instances(instances_df, right_rule)

            left_instances_set = set(left_instances)
            right_instances_set = set(right_instances)

            # rules that have opposite relationships
            # ?b ?a => ?a ?b
            if rule_id == 1:
                for (right_head, right_tail) in right_instances_set:
                    if (right_tail, right_head) in left_instances_set and right_tail != right_head:
                        unique_rules_dict[rule] = f"{right_tail} {left_rule} {right_head} => {right_head} {right_rule} {right_tail}"
                        print("Found: ", unique_rules_dict[rule])
                        break
            # c ?a => ?a c, ?b c = > c ?b
            elif rule_id == 20:
                left_const = left_parts[0]
                right_const = right_parts[2]
                for (_, left_tail) in left_instances_set:
                    if (left_tail, right_const) in right_instances_set and (left_const, left_tail) in left_instances_set:
                        unique_rules_dict[rule] = f"{left_const} {left_rule} {left_tail} => {left_tail} {right_rule} {right_const}"
                        print("Found: ", unique_rules_dict[rule])
                        break
            # ?b c = > c ?b
            elif rule_id == 22:
                left_const = left_parts[2]
                right_const = right_parts[0]
                for (left_head, _) in left_instances_set:
                    if (right_const, left_head) in right_instances_set and (left_head, left_const) in left_instances_set:
                        unique_rules_dict[rule] = f"{left_head} {left_rule} {left_const} => {right_const} {right_rule} {left_head}"
                        print("Found: ", unique_rules_dict[rule])
                        break
            # rules that have the same relationships
            # ?a ?b => ?a ?b
            elif rule_id == 2:
                for (right_head, right_tail) in right_instances_set:
                    if (right_head, right_tail) in left_instances_set and right_tail != right_head:
                        unique_rules_dict[rule] = f"{right_head} {left_rule} {right_tail} => {right_head} {right_rule} {right_tail}"
                        print("Found: ", unique_rules_dict[rule])
                        break
            # ?a c => ?a c
            elif rule_id == 19:
                left_const = left_parts[2]
                right_const = right_parts[2]
                for (left_head, _) in left_instances_set:
                    if (left_head, right_const) in right_instances_set and (left_head, left_const) in left_instances_set:
                        unique_rules_dict[rule] = f"{left_head} {left_rule} {left_const} => {left_head} {right_rule} {right_const}"
                        print("Found: ", unique_rules_dict[rule])
                        break
            # c ?b = > c ?b
            elif rule_id == 21:
                left_const = left_parts[0]
                right_const = right_parts[0]
                for (_, left_tail) in left_instances_set:
                    if (right_const, left_tail) in right_instances_set and (left_const, left_tail) in left_instances_set:
                        unique_rules_dict[rule] = f"{left_const} {left_rule} {left_tail} => {right_const} {right_rule} {left_tail}"
                        print("Found: ", unique_rules_dict[rule])
                        break
            
        else :
            rule_type = left_parts[0] + " " + left_parts[2] + " " + left_parts[3] + " " + left_parts[5] + " => " + right_parts[0] + " " + right_parts[2]
            rule_id = rule_types_dict[rule_type]

            left_rule1 = left_parts[1]
            left_rule2 = left_parts[4]
            right_rule = right_parts[1]

            left_instances1 = get_all_instances(instances_df, left_rule1)
            left_instances2 = get_all_instances(instances_df, left_rule2)
            right_instances = get_all_instances(instances_df, right_rule)

            left_instances_set1 = set(left_instances1)
            left_instances_set2 = set(left_instances2)
            right_instances_set = set(right_instances)

            # ?a ?f ?b ?f => ?a ?b
            if rule_id == 3:
                tail_side_set2 = {left_tail for (_, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in tail_side_set2:
                        common_var = left_tail1
                        left_head2 = next((head for (head, tail) in left_instances_set2 if tail == left_tail1), None)
                        if left_head2 and left_head1 != left_head2 and left_head1 != common_var and left_head2 != common_var:
                            if (left_head1, left_head2) in right_instances_set :
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {left_head2} {left_rule2} {common_var} => {left_head1} {right_rule} {left_head2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?f ?a ?b ?f => ?a ?b
            elif rule_id == 4:
                tail_side_set2 = {left_tail for (_, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in tail_side_set2:
                        common_var = left_head1
                        left_head2 = next((head for (head, tail) in left_instances_set2 if tail == common_var), None)
                        if left_head2 and left_tail1 != left_head2 and left_tail1 != common_var and left_head2 != common_var:
                            if (left_tail1, left_head2) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {left_head2} {left_rule2} {common_var} => {left_tail1} {right_rule} {left_head2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?e ?a ?e ?b => ?a ?b
            elif rule_id == 5:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in head_side_set2:
                        common_var = left_head1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_tail1 != left_tail2 and left_tail1 != common_var and left_tail2 != common_var:
                            if (left_tail1, left_tail2) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {common_var} {left_rule2} {left_tail2} => {left_tail1} {right_rule} {left_tail2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?a ?e ?e ?b => ?a ?b
            elif rule_id == 6:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in head_side_set2:
                        common_var = left_tail1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_head1 != left_tail2 and left_head1 != common_var and left_tail2 != common_var:
                            if (left_head1, left_tail2) in right_instances_set:
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {common_var} {left_rule2} {left_tail2} => {left_head1} {right_rule} {left_tail2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?b ?a ?a ?b => ?a ?b
            elif rule_id == 7:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in head_side_set2:
                        common_var = left_tail1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_head1 == left_tail2 and common_var != left_tail2:
                            if (left_tail1, left_tail2) in right_instances_set:
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {common_var} {left_rule2} {left_tail2} => {left_tail1} {right_rule} {left_tail2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?b ?a ?b ?a => ?a ?b
            elif rule_id == 8:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in head_side_set2:
                        common_var = left_head1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_tail1 == left_tail2 and common_var != left_tail2:
                            if (left_tail2, left_head1) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {common_var} {left_rule2} {left_tail2} => {left_tail2} {right_rule} {left_head1}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?a ?b ?a ?b => ?a ?b
            elif rule_id == 9:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in head_side_set2:
                        common_var = left_head1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_tail1 == left_tail2 and common_var != left_tail2:
                            if (left_head1, left_tail2) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {common_var} {left_rule2} {left_tail2} => {left_head1} {right_rule} {left_tail2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?a ?b ?b ?a => ?a ?b
            elif rule_id == 10:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in head_side_set2:
                        common_var = left_tail1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_head1 == left_tail2 and left_head1 != common_var:
                            if (left_tail1, left_tail2) in right_instances_set:
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {common_var} {left_rule2} {left_tail2} => {left_tail1} {right_rule} {left_tail2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?b ?f ?a ?f = > ?a ?b
            elif rule_id == 11:
                tail_side_set2 = {left_tail for (_, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in tail_side_set2:
                        common_var = left_tail1
                        left_head2 = next((head for (head, tail) in left_instances_set2 if tail == left_tail1), None)
                        if left_head2 and left_head1 != left_head2 and left_head1 != common_var and left_head2 != common_var:
                            if (left_head2, left_head1) in right_instances_set:
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {left_head2} {left_rule2} {common_var} => {left_head2} {right_rule} {left_head1}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?b ?f ?f ?a => ?a ?b
            elif rule_id == 12:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in head_side_set2:
                        common_var = left_tail1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_head1 != left_tail2 and left_head1 != common_var and left_tail2 != common_var:
                            if (left_tail2, left_head1) in right_instances_set:
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {common_var} {left_rule2} {left_tail2} => {left_tail2} {right_rule} {left_head1}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?a ?f ?f ?b => ?a ?b
            elif rule_id == 13:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in head_side_set2:
                        common_var = left_tail1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_head1 != left_tail2 and left_head1 != common_var and left_tail2 != common_var:
                            if (left_head1, left_tail2) in right_instances_set:
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {common_var} {left_rule2} {left_tail2} => {left_head1} {right_rule} {left_tail2}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?f ?b ?a ?f => ?a ?b
            elif rule_id == 14:
                tail_side_set2 = {left_tail for (_, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in tail_side_set2:
                        common_var = left_head1
                        left_head2 = next((head for (head, tail) in left_instances_set2 if tail == common_var), None)
                        if left_head2 and left_tail1 != left_head2 and left_tail1 != common_var and left_head2 != common_var:
                            if (left_head2, left_tail1) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {left_head2} {left_rule2} {common_var} => {left_head2} {right_rule} {left_tail1}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?e ?b ?e ?a => ?a ?b
            elif rule_id == 15:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in head_side_set2:
                        common_var = left_head1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_tail1 != left_tail2 and left_tail1 != common_var and left_tail2 != common_var:
                            if (left_tail2, left_tail1) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {common_var} {left_rule2} {left_tail2} => {left_tail2} {right_rule} {left_tail1}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?e ?b ?a ?e => ?a ?b
            elif rule_id == 16:
                tail_side_set2 = {left_tail for (_, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in tail_side_set2:
                        common_var = left_head1
                        left_head2 = next((head for (head, tail) in left_instances_set2 if tail == common_var), None)
                        if left_head2 and left_tail1 != left_head2 and left_tail1 != common_var and left_head2 != common_var:
                            if (left_head2, left_tail1) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {left_head2} {left_rule2} {common_var} => {left_head2} {right_rule} {left_tail1}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?b ?e ?e ?a = > ?a ?b
            elif rule_id == 17:
                head_side_set2 = {left_head for (left_head, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_tail1 in head_side_set2:
                        common_var = left_tail1
                        left_tail2 = next((tail for (head, tail) in left_instances_set2 if head == common_var), None)
                        if left_tail2 and left_head1 != left_tail2 and left_head1 != common_var and left_tail2 != common_var:
                            if (left_tail2, left_head1) in right_instances_set:
                                unique_rules_dict[rule] = f"{left_head1} {left_rule1} {common_var} {common_var} {left_rule2} {left_tail2} => {left_tail2} {right_rule} {left_head1}"
                                print("Found: ", unique_rules_dict[rule])
                                break
            # ?e ?a ?b ?e => ?a ?b
            elif rule_id == 18:
                tail_side_set2 = {left_tail for (_, left_tail) in left_instances_set2}

                for (left_head1, left_tail1) in left_instances_set1:
                    if left_head1 in tail_side_set2:
                        common_var = left_head1
                        left_head2 = next((head for (head, tail) in left_instances_set2 if tail == common_var), None)
                        if left_head2 and left_tail1 != left_head2 and left_tail1 != common_var and left_head2 != common_var:
                            if (left_tail1, left_head2) in right_instances_set:
                                unique_rules_dict[rule] = f"{common_var} {left_rule1} {left_tail1} {left_head2} {left_rule2} {common_var} => {left_tail1} {right_rule} {left_head2}"
                                print("Found: ", unique_rules_dict[rule])
                                break



    results_df = pd.DataFrame(list(unique_rules_dict.items()), columns=['rule', 'rule_instance'])
    results_df.to_csv('examples.csv', index=False)

    head_side_set2 = {left_head for (left_head, _) in left_instances_set2}
    tail_side_set2 = {left_tail for (_, left_tail) in left_instances_set2}
    print("CSV file 'examples.csv' has been created.")

