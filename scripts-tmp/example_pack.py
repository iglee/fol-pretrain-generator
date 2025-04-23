from src.fol_util import read_jsonl_to_list
import glob
import os
from tqdm import tqdm
import json

UNIQUE_ID = 0

MAX_LEN = 6200
SAVE_DIR = "/mnt/isabelle-pretrain-data/packed_training_examples"
os.makedirs(SAVE_DIR, exist_ok=True)

files = glob.glob("/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/training_data_v2/*")

current_example = {
        "id": UNIQUE_ID,
        "fol_rules": [],
        "num_tokens": 0,
        "raw_data":"",
        "gpt2_tokens": [],
        "datum_ids" : []
    }
packed_examples = []
file_counter = 0

for file in tqdm(files, desc="Processing files"):
    data = read_jsonl_to_list(file)
    
    for item in data:
        item_length = item['length']
        item_tokens = item['tokens']
        item_string = item['string']
        item_rule = item['rule']['id']

        if current_example['num_tokens'] + item_length > MAX_LEN - 1:
            current_example['gpt2_tokens'].append(50256)
            current_example['num_tokens'] += 1
            
            
            packed_examples.append(current_example)
            UNIQUE_ID +=1
            current_example = {
                "id":UNIQUE_ID,
                "fol_rules": [],
                "num_tokens": 0,
                "raw_data":"",
                "gpt2_tokens": [],
                "datum_ids" : []
            }
        
        current_example['datum_ids'].append(item['datum_id'])
        current_example['num_tokens'] += item_length
        current_example['gpt2_tokens'].extend(item_tokens)
        if not current_example['raw_data']:
            current_example['raw_data'] = item_string
        else:
            current_example['raw_data'] = " ".join([current_example['raw_data'], item_string])
        current_example['fol_rules'].append(item_rule)
        
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
