import json

# Define the file paths
input_file = "data/fol_rules.json"
output_file = "data/fol_rules.jsonl"

# Read the JSONL file
data = []
with open(input_file, "r") as f:
    for line in f:
        entry = json.loads(line.strip())
        data.append(entry)

# Add unique IDs to each entry
for idx, entry in enumerate(data):
    entry["id"] = f"fol-rule-{idx + 1}"

# Write the updated entries back to a JSONL file
with open(output_file, "w") as f:
    for entry in data:
        json.dump(entry, f)
        f.write("\n")

print(f"Updated entries written to {output_file}")
