import os
import json
from collections import defaultdict

def count_tokens_by_fol_type(directory, count_categories = True):
    total_tokens = 0
    if count_categories:
        fol_type_counts = defaultdict(int)
        fol_type_tokens = defaultdict(int)
    else:
        fol_type_counts = fol_type_tokens = None

    for filename in os.listdir(directory):
        if filename.endswith('.jsonl'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        data = json.loads(line)
                        num_tokens = data.get('num_tokens', 0)
                        fol_type = data.get('fol_type', 'UNKNOWN')
                        
                        total_tokens += num_tokens
                        if count_categories:
                            fol_type_counts[fol_type] += 1
                            fol_type_tokens[fol_type] += num_tokens

              
    return total_tokens, fol_type_counts, fol_type_tokens

# Example usage
if __name__ == "__main__":
    directory_path = '/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/train_2'  
    total, counts, tokens_by_type = count_tokens_by_fol_type(directory_path, count_categories = False)

    print(f"Total number of tokens: {total}\n")
    print("Breakdown by fol_type:")
    for fol_type in counts:
        print(f"- {fol_type}: {counts[fol_type]} occurrences, {tokens_by_type[fol_type]} tokens")
