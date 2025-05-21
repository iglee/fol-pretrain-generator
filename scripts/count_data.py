import os
import json
from collections import defaultdict

def analyze_jsonl_files(directory):
    fol_type_counts = defaultdict(int)
    fol_type_tokens = defaultdict(int)

    random_count = 0
    random_tokens = 0

    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        fol_type = data.get("fol_type")
                        num_tokens = data.get("num_tokens", 0)

                        if fol_type is not None:
                            fol_type_counts[fol_type] += 1
                            fol_type_tokens[fol_type] += int(num_tokens)

                            if "random" in fol_type.lower():
                                random_count += 1
                                random_tokens += int(num_tokens)
                    except json.JSONDecodeError:
                        print(f"Skipping malformed line in {filename}")

    return fol_type_counts, fol_type_tokens, random_count, random_tokens

# Example usage
directory = "/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/train"
counts, tokens, random_count, random_tokens = analyze_jsonl_files(directory)

total_non_random_rules, total_non_random_tokens = 0,0

print("FOL Type Frequencies:")
random_rules = set()
for k, v in counts.items():
    if "random" not in k:
        print(f"{k}: {v} items, {tokens[k]} total tokens")
        total_non_random_rules += v
        total_non_random_tokens += tokens[k]
    else:
        random_rules.add(k)


print(f"\n'NON-Random' FOL Types: {total_non_random_rules} items, {total_non_random_tokens} total tokens")
print(f"\n'Random' FOL Types: {random_count} items, {random_tokens} total tokens")

print(f"\nUnique random rules: {len(random_rules)}")
