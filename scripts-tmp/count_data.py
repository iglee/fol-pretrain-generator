import os
import json
from tqdm import tqdm 

# Directory containing the dataset
data_dir = "/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/train"

# Specify the file indices to check
N_values = [159, 438, 1250, 2728]

# Sort N_values to ensure proper counting order
N_values = sorted(N_values)

total_examples = 0
total_num_tokens = 0
current_checkpoint = 0

# Iterate over files, stopping at the maximum value in N_values
for i in tqdm(range(max(N_values) + 1), desc="Processing files", unit="file"):
    file_path = os.path.join(data_dir, f"segment_{i}.jsonl")
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            for line in f:
                total_examples += 1
                # Parse the JSON line and add the num_tokens field value
                record = json.loads(line)
                if 'num_tokens' in record:
                    total_num_tokens += record['num_tokens']
    else:
        print(f"File not found: {file_path}")
        break

    # Print total counts when reaching a checkpoint in N_values
    if i == N_values[current_checkpoint]:
        print(f"Files 0 to {i}:")
        print(f"  Total number of examples: {total_examples}")
        print(f"  Total num_tokens: {total_num_tokens}")
        current_checkpoint += 1
        if current_checkpoint >= len(N_values):
            break