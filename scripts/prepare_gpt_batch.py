from src.fol_util import read_jsonl_to_list, read_json_file
import random

fol_example_prompt = "config/fol_batch_example.json"
train_data_pth = "data/unique_train_fol_rules.jsonl"
train_data = read_jsonl_to_list(train_data_pth)
preds = read_jsonl_to_list("data/predicates.jsonl")

for x in train_data:
    example = read_json_file(fol_example_prompt)
    example["custom_id"] = x["id"]

    
    topic = random.sample(preds,1)[0]
    predicates = random.sample(topic["predicates"],3)
    prompt = example["body"]["messages"][1]["content"]


    prompt = prompt.format(
                    rule = x["exprs"][0], \
                    topic = topic["topic"], \
                    predicate1 = predicates[0], \
                    predicate2 = predicates[1], \
                    predicate3 = predicates[2] \
                )
    print(prompt)
    example["body"]["messages"][1]["content"]=prompt

    break