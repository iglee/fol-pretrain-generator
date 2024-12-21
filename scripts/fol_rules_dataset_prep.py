from src.fol_util import read_jsonl_to_list, find_unique_variables, replace_variables, write_list_to_jsonl
import random

fol_data_file = "data/fol_rules.jsonl"
dataset = read_jsonl_to_list(fol_data_file)

replacements = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ']  # Replacement variables

unique_data = set()
unique_set = []

for x in dataset:
    _, variable_map = find_unique_variables(x["exprs"][0], replacements)
    result = replace_variables(x["exprs"][0], variable_map)
    exprs = [result]

    for expression in x["exprs"][1:]:
        result = replace_variables(expression, variable_map)
        exprs.append(result)

    x["exprs"] = exprs

    datum = " ⇔ ".join(f"({y})" for y in exprs)
    if datum not in unique_data:
        x["data"] = datum
        unique_set.append(x)

    unique_data.add(datum)

    
print(len(dataset))
print(len(unique_set))
#write_list_to_jsonl(unique_set, "data/unique_fol_rules.jsonl")

random.shuffle(unique_set)
test = unique_set[:109582]
train = unique_set[109582:]

print(len(test), len(train))
write_list_to_jsonl(test, "data/unique_test_fol_rules.jsonl")
write_list_to_jsonl(train, "data/unique_train_fol_rules.jsonl")