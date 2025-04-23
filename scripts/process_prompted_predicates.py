from src.fol_util import read_jsonl_to_list, write_list_to_jsonl
from src.gpt_util import get_response_from_batch_items
import os
import json
import re

predicates_dir = "data/predicate_prompted"
output_dir = "data/predicate_processed"
N_files = 177*2

def extract_jsonl_from_content(content):
    # Step 1: Extract the code block (if it's there)
    match = re.search(r"```jsonl\n(.*?)```", content, re.DOTALL)
    if match:
        jsonl_str = match.group(1)
    else:
        # Fallback if no ```jsonl block, use the raw string
        jsonl_str = content.strip()

    # Step 2: Split into lines and parse each as JSON
    return [json.loads(line) for line in jsonl_str.strip().split('\n') if line.strip()]


predicates_processed = []

for i in range(N_files):
    file = os.path.join(predicates_dir, f"predicates_{i}.jsonl")
    data = read_jsonl_to_list(file)
    for x in data:
        try:
            response = get_response_from_batch_items(x)
            predicates = extract_jsonl_from_content(response)
            for x in predicates:
                if len(x['predicates']) == 4:
                    predicates_processed.append(x)
        except:
            pass
        
write_list_to_jsonl(predicates_processed, "data/processed_predicates.jsonl")