import os
import re
import random
import tiktoken
import json

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

def tokenize_with_cl100k_base(text):
    """
    Tokenize a string using the cl100k_base tokenizer.

    Parameters:
    - text (str): The input string to tokenize.

    Returns:
    - tokens (list of int): The token IDs.
    - decoded (list of str): The decoded text chunks for each token.
    """
    enc = tiktoken.get_encoding("cl100k_base")
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


def separate_predicates(input_string):
    return re.findall(r'\b\w+\s*\([^)]*\)', input_string)

directory = '/home/isabelle/fol-pretrain-generator/rules/predicates'  # Replace with the actual directory path

# List all files and directories in the given directory

triplets = {}
singles = {}
fundamentals = ["Is(x)", "Feels(x)", "Exists(x)", "Does(x)", "Stands(x)", "There(x)", "Are(x)", "Do(x)",\
                "Has(x)", "Have(x)", "Comes(x)", "Come(x)", "Goes(x)", "Gone(x)", "Moves(x)", "Becomes(x)", \
                "Happens(x)", "Changes(x)", "Lives(x)", "Alive(x)","Hard(x)", "Soft(x)",\
                "Remains(x)", "Remembers(x)", "Looks(x)", "Sounds(x)", "Belongs(x)", "Matters(x)", "Begins(x)", "Works(x)"]



for filename in os.listdir(directory):
    pth = os.path.join(directory, filename)
    k = filename.split("_")[0]
    v = read_file_lines(pth)
    if "triplet" in filename:
        triplets[k] = [separate_predicates(x) for x in v if x and (("True" not in x) or ("False" not in x))]
        triplets[k] = [x for x in triplets[k] if len(x) == 3]

    else:
        singles[k] = [x for x in v if x and (("True" not in x) or ("False" not in x))]




def generate_data(rule_datum, data_type="train", temp_dir=None, i_start=0):
    generated = []
    i = i_start

    if data_type in {"train", "basic"}:
        k = 1000 if data_type == "basic" else 6

        for _ in range(k):
            for datalist in triplets.values():
                try:
                    predicates = random.sample(datalist, 1)[0].copy()
                    predicates += [random.choice(fundamentals)]
                    datum = "<|endoftext|> " + replace_greek_with_functions(rule_datum['rule'], predicates)
                    tokens, length = tokenize_with_cl100k_base(datum)
                    data = {
                        "id": f"traindata_{i}",
                        "rule_id": rule_datum["id"],
                        "datum": datum,
                        "tokens": tokens,
                        "length": length
                    }
                    generated.append(data)
                    i += 1
                except Exception as e:
                    print(f"[Triplet Error] {e}")

            for datalist in singles.values():
                try:
                    predicates = random.sample(datalist, 4)
                    datum = "<|endoftext|> " + replace_greek_with_functions(rule_datum['rule'], predicates)
                    tokens, length = tokenize_with_cl100k_base(datum)
                    data = {
                        "id": f"traindata_{i}",
                        "rule_id": rule_datum["id"],
                        "datum": datum,
                        "tokens": tokens,
                        "length": length
                    }
                    generated.append(data)
                    i += 1
                except Exception as e:
                    print(f"[Single Error] {e}")

    elif data_type == "test" or data_type == "dev":
        try:
            if random.random() < 0.3:
                datalist = random.choice(list(triplets.values()))
                predicates = random.sample(datalist, 1)[0].copy()
                predicates += [random.choice(fundamentals)]
            else:
                datalist = random.choice(list(singles.values()))
                predicates = random.sample(datalist, 4)

            datum = "<|endoftext|> " + replace_greek_with_functions(rule_datum['rule'], predicates)
            tokens, length = tokenize_with_cl100k_base(datum)
            data = {
                "id": f"test_{i}",
                "rule_id": rule_datum["id"],
                "datum": datum,
                "tokens": tokens,
                "length": length
            }
            generated.append(data)
        except Exception as e:
            print(f"[Test Error] {e}")

    return generated

train_rules = "/home/isabelle/fol-pretrain-generator/rules/train_rules.json"
basic_rules = "/home/isabelle/fol-pretrain-generator/rules/basic_rules.json"
test_rules = "/home/isabelle/fol-pretrain-generator/rules/test_rules.json"
dev_rules = "/home/isabelle/fol-pretrain-generator/rules/dev_rules.json"
tf_test_rules = "/home/isabelle/fol-pretrain-generator/rules/tf_test_rules.json"
tf_train_rules = "/home/isabelle/fol-pretrain-generator/rules/tf_train_rules.json"

rules_data = {}



for rules in [basic_rules, test_rules, dev_rules, tf_test_rules, tf_train_rules, train_rules]:
    filename_without_ext = os.path.splitext(os.path.basename(rules))[0]

    with open(rules, 'r') as f:
        rules_data[filename_without_ext] = json.load(f)
        