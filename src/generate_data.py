import os
import re
import random
import tiktoken
import json
from src.fol_util import read_jsonl_to_list

def read_file_lines(filepath):
    """
    Reads a file line by line and returns a list of stripped lines.

    :param filepath: Path to the file.
    :return: List of lines with leading/trailing whitespace removed.
    """
    lines = []
    with open(filepath, 'r') as file:
        for line in file:
            lines.append(line.strip())
    return lines

def tokenize(text):
    """
    Tokenize a string using the cl100k_base tokenizer.

    Parameters:
    - text (str): The input string to tokenize.

    Returns:
    - tokens (list of int): The token IDs.
    - decoded (list of str): The decoded text chunks for each token.
    """
    enc = tiktoken.get_encoding("gpt2")
    tokens = enc.encode(text, allowed_special={"<|endoftext|>"})
    return tokens, len(tokens)

def replace_greek_with_functions(expr, function_names):
    greek_letters = ['α', 'β', 'γ', 'δ']
    
    if len(function_names) > len(greek_letters):
        raise ValueError("Too many function names provided — max is 4 (α to δ).")

    # Create mapping from Greek letter to provided function name
    greek_map = dict(zip(greek_letters, function_names))

    # Replace each Greek letter in the string
    for greek, func in greek_map.items():
        expr = re.sub(rf'\b{re.escape(greek)}\b', func, expr)

    return expr



predicates_pth = "/home/isabelle/fol-pretrain-generator/data/processed_predicates_total.jsonl"
predicates_total = read_jsonl_to_list(predicates_pth)


def generate_data(rule_datum, data_type="train", temp_dir=None, i_start=0):
    generated = []
    i = i_start

    if data_type in {"train", "basic"}:
        if data_type == "basic":
            k = 300000 
        else:
            k = random.randint(2, 6)

        for _ in range(k):
            for attempt in range(3):
                try:
                    predicates = random.sample(predicates_total, 1)[0]["predicates"].copy()
                    random.shuffle(predicates)
                    
                    datum = "<|endoftext|> " + replace_greek_with_functions(rule_datum['rule'], predicates) + " <|endoftext|>"
                    tokens, length = tokenize(datum)
                    if length < 1024:
                        data = {
                            "id": f"traindata_{i}",
                            "fol_type": rule_datum["id"],
                            "raw_data": datum,
                            "gpt2_tokens": tokens,
                            "num_tokens": length
                        }
                        generated.append(data)
                        i += 1
                    break  # Success, break out of retry loop
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for rule: {rule_datum['rule']} with predicates: {predicates}")
                    if attempt == 2:
                        print("Final failure after 3 attempts:", e)
    elif data_type == "train_repeated":
        for _ in range(100000):
            for attempt in range(3):
                try:
                    predicates = random.sample(predicates_total, 1)[0]["predicates"].copy()
                    random.shuffle(predicates)
                    datum = "<|endoftext|> " + replace_greek_with_functions(rule_datum['rule'], predicates)
                    tokens, length = tokenize(datum)
                    data = {
                        "id": f"traindata_{i}",
                        "fol_type": rule_datum["id"],
                        "raw_data": datum,
                        "gpt2_tokens": tokens,
                        "num_tokens": length
                    }
                    generated.append(data)
                    i += 1
                    break  # Success, break out of retry loop
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for rule: {rule_datum['rule']} with predicates: {predicates}")
                    if attempt == 2:
                        print("Final failure after 3 attempts:", e)
            
    else:
        try: 
            predicates = random.sample(predicates_total, 1)[0]["predicates"].copy()
            random.shuffle(predicates)
            datum = "<|endoftext|> " + replace_greek_with_functions(rule_datum['rule'] + " <|endoftext|>", predicates)
            tokens, length = tokenize(datum)
            data = {
                "id": f"traindata_{i}",
                "fol_type": rule_datum["id"],
                "raw_data": datum,
                "gpt2_tokens": tokens,
                "num_tokens": length
            }
            generated.append(data)
            i += 1
        except:
            print("failed rule: ", rule_datum['rule'], "predicates: ", predicates)

    return generated

train_rules = "/home/isabelle/fol-pretrain-generator/fol-rules/train_rules.json"
basic_rules = "/home/isabelle/fol-pretrain-generator/rules/basic_rules.json"
test_rules = "/home/isabelle/fol-pretrain-generator/fol-rules/test_rules.json"
dev_rules = "/home/isabelle/fol-pretrain-generator/fol-rules/dev_rules.json"
tf_test_rules = "/home/isabelle/fol-pretrain-generator/fol-rules/tf_test_rules.json"
tf_train_rules = "/home/isabelle/fol-pretrain-generator/fol-rules/tf_train_rules.json"

rules_data = {}

for rules in [basic_rules, test_rules, dev_rules, tf_test_rules, tf_train_rules, train_rules]:
    filename_without_ext = os.path.splitext(os.path.basename(rules))[0]

    with open(rules, 'r') as f:
        rules_data[filename_without_ext] = json.load(f)
        