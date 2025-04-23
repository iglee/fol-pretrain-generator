from src.fol_util import read_jsonl_to_list, read_json_file, write_list_to_jsonl
import random
import json
import os

datadir = "data/batched_prompts_train/"
preamble = datadir+"train_data_batch_"
os.makedirs(datadir, exist_ok=True)

fol_example_prompt = "config/fol_batch_example.json"
test_data_pth = "data/unique_train_fol_rules.jsonl"
test_data = read_jsonl_to_list(test_data_pth)
preds = read_jsonl_to_list("data/predicates.jsonl")

batch = []
batch_size = 1000

for i, x in enumerate(test_data):
    example = read_json_file(fol_example_prompt)
    example["custom_id"] = x["id"]

    topic = random.sample(preds, 1)[0]
    predicates = random.sample(topic["predicates"], 2)
    prompt = example["body"]["messages"][1]["content"]

    prompt = prompt.format(
                    rule = x["exprs"][0], \
                    topic = topic["topic"], \
                    predicate1 = predicates[0], \
                    predicate2 = predicates[1]
                )
    
    example["body"]["messages"][1]["content"] = prompt
    batch.append(example)
    
    if len(batch) >= batch_size:
        write_list_to_jsonl(batch, f'{preamble}{i // batch_size}.jsonl')
        batch = []  # Reset the batch after saving
if batch:
    write_list_to_jsonl(batch, f'{preamble}{i // batch_size}.jsonl')
