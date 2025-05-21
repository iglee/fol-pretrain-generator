import os
import json

def count_examples_and_tokens(directory):
    total_examples = 0
    total_tokens = 0

    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        total_examples += 1
                        total_tokens += data.get("num_tokens", 0)
                    except json.JSONDecodeError:
                        print(f"Skipping invalid JSON in file: {file_path}")
    
    return total_examples, total_tokens

# Example usage
directory_path = "/mnt/isabelle-pretrain-data/fol-pretrain/train/curated"
examples, tokens = count_examples_and_tokens(directory_path)
print(f"Total examples: {examples}")
print(f"Total tokens: {tokens}")
