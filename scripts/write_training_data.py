from src.fol_util import read_jsonl_to_list, find_unique_variables, replace_variables, write_list_to_jsonl
import re
import tiktoken
import glob
import os

TOTAL_TOKEN_CNT=0
MAX_LEN=0
unique_set = set()
datum_id = 0

enc = tiktoken.get_encoding("gpt2")
encode = lambda s: enc.encode(s, allowed_special={"<|endoftext|>"})
decode = lambda l: enc.decode(l)

# output path
output_path = "/mnt/isabelle-pretrain-data/training_data_v2"

if not os.path.exists(output_path):
    os.makedirs(output_path)


fol_rules_file = "data/unique_train_fol_rules.jsonl"
fol_rules = read_jsonl_to_list(fol_rules_file)
fol_rules = {x["id"] : x for x in fol_rules}


def clean_text(text):
    return re.sub(r'\d+\.\s*', '', text).strip()

def match_greek_to_predicates(template: str, expression: str):
    # Find all Greek letters (α, β, γ, etc.) in the template
    greek_letters = re.findall(r'[α-ω]', template)
    
    # Find all predicates in the concrete expression (using the format: PredicateName(...))
    predicates = re.findall(r'\w+\(.*?\)', expression)
    
    # Create a mapping by matching Greek letters to predicates in order
    mapping = {}
    for greek, predicate in zip(greek_letters, predicates):
        mapping[greek] = predicate
    
    return mapping


def process_batch_file(retrieved_pth, output_path, output_file):
    global datum_id, MAX_LEN, TOTAL_TOKEN_CNT
    dataset = []

    retrieved_data = read_jsonl_to_list(retrieved_pth)

    for x in retrieved_data:
        examples = x["response"]["body"]["choices"][0]["message"]["content"].split("\n")
        examples = [clean_text(y) for y in examples if y]

        for y in examples:
            datum = {"datum_id":datum_id, "rule" : fol_rules[x["custom_id"]], "string":""}

            matching = match_greek_to_predicates(fol_rules[x["custom_id"]]["exprs"][0], y)
            string = fol_rules[x["custom_id"]]["data"]

            for k,v in matching.items():
                string = string.replace(k,v)

            if string not in unique_set:

                datum["string"] = "<|endoftext|> " + string
                datum["tokens"] = encode(datum["string"])
                datum["length"] = len(datum["tokens"])
                datum["datum_id"] = datum_id
                dataset.append(datum)
                datum_id += 1
                unique_set.add(string)
                MAX_LEN = max(MAX_LEN, len(datum["tokens"]))
                TOTAL_TOKEN_CNT += len(datum["tokens"])
    write_list_to_jsonl(dataset, os.path.join(output_path, output_file))

output_file = "segment_{i}.jsonl"
files = glob.glob("/mnt/isabelle-pretrain-data/fol-pretrain-data-new/*")

for i, retrieved_pth in enumerate(files):
    process_batch_file(retrieved_pth, output_path, output_file.format(i=i))
    print(f"file {i}: total token cnt: {TOTAL_TOKEN_CNT}, max length of data: {MAX_LEN}")

print(f"final counts: total token cnt: {TOTAL_TOKEN_CNT}, max length of data: {MAX_LEN}")