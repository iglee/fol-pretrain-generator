import json
import os

def enrich_data(train_file, rules_json_file, output_file):
    # Load the rules data (a list of rule dicts)
    with open(rules_json_file, 'r', encoding='utf-8') as rf:
        rules_data = json.load(rf)

    # Build a lookup dict from rule["id"] → complexity info
    rule_complexities = {
        rule["id"]: {
            "program_complexity": rule.get("program_complexity"),
            "original_complexity": rule.get("original_complexity")
        }
        for rule in rules_data if "id" in rule
    }

    # Enrich training examples and write to output
    with open(train_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line in infile:
            example = json.loads(line)
            fol_type = example.get("fol_type")
            if fol_type in rule_complexities:
                example.update(rule_complexities[fol_type])
            else:
                example.update({
                    "program_complexity": None,
                    "original_complexity": None
                })
            outfile.write(json.dumps(example) + '\n')

# Example usage
train_jsonl = "/mnt/isabelle-pretrain-data/fol-pretrain/tf_test/segment_0.jsonl"
rules_jsonl = "/mnt/isabelle-pretrain-data/fol-pretrain/fol-rules/tf_test_rules.json"
output_jsonl = "/mnt/isabelle-pretrain-data/fol-pretrain/tf_test/segment_0_with_rules.jsonl"

enrich_data(train_jsonl, rules_jsonl, output_jsonl)
