import json

input_path = 'rules/sampled_rules.jsonl'  # despite the .jsonl name, this is JSON
output_path = 'rules/modified_rules.jsonl'

# Load the whole array
with open(input_path, 'r', encoding='utf-8') as infile:
    data = json.load(infile)

modified_data = []
for item in data:
    modified_entry = {
        "id": item["id"] + "_modified",
        "exprs": item["exprs"],  # No changes to exprs
        "rule": " ⇔ ".join(item["exprs"])  # Combine exprs into a single rule
    }
    modified_data.append(modified_entry)

# Write the entire modified list as a JSON array to the output file
with open(output_path, 'w', encoding='utf-8') as outfile:
    json.dump(modified_data, outfile, ensure_ascii=False, indent=4)