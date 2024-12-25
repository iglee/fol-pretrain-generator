from src.fol_util import read_jsonl_to_list
import glob
import os
from tqdm import tqdm
import json

MAX_LEN = 6200
SAVE_DIR = "/mnt/isabelle-pretrain-data/packed_training_examples"
os.makedirs(SAVE_DIR, exist_ok=True)

files = glob.glob("/mnt/isabelle-pretrain-data/training_data_v2/*")

current_example = {
        "ids": [],
        "length": 0,
        "tokens": []
    }
packed_examples = []
file_counter = 0

for file in tqdm(files, desc="Processing files"):
    data = read_jsonl_to_list(file)
    
    for item in data:
        item_length = item['length']
        item_tokens = item['tokens']

        if current_example['length'] + item_length > MAX_LEN - 1:
            current_example['tokens'].append(50256)
            current_example['length'] += 1
            
            packed_examples.append(current_example)
            current_example = {
                "ids": [],
                "length": 0,
                "tokens": []
            }
        
        current_example['ids'].append(item['datum_id'])
        current_example['length'] += item_length
        current_example['tokens'].extend(item_tokens)
        
        # Save and reset if packed_examples reaches 2000
        if len(packed_examples) >= 1000:
            save_path = os.path.join(SAVE_DIR, f"packed_examples_{file_counter}.jsonl")
            with open(save_path, "w") as f:
                for example in packed_examples:
                    f.write(json.dumps(example) + "\n")
            packed_examples = []  # Reset the list
            file_counter += 1

# Save any remaining packed_examples
if packed_examples:
    save_path = os.path.join(SAVE_DIR, f"packed_examples_{file_counter}.jsonl")
    with open(save_path, "w") as f:
        for example in packed_examples:
            f.write(json.dumps(example) + "\n")
