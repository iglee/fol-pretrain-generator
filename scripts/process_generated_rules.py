"""
script to process raw generated fol rules
--
1. deduplicate rules
2. test/train split
3. save all files
"""
from src.fol_util import read_pkl_fie, standardize_variables, test_train_split_list, write_list_to_json
import copy
import random
from collections import defaultdict

pkl_file = "unique_fol_rules.pkl"
data = read_pkl_fie(pkl_file)
print(f"total number of rules: {len(data)}")

# deduplicate rules
unique = set()
unique_data = []
i = 0

for x,_,z in data:
    cleaned = standardize_variables(x)
    if cleaned not in unique:
        unique.add(cleaned)
        z['rule'] = x
        z['id'] = f"rule_{i}"
        unique_data.append(z)
        i+=1

print(f"total number of unique rules: {len(unique)}")

# test train split
print(f"\n\ntest train dev split...")
test, train = test_train_split_list(unique_data, 0.004)
sampled = random.sample(train, k=int(len(train) * 0.02))
dev = [copy.deepcopy(x) for x in sampled[:5000]]
print(f"split complete: test ({len(test)}), train ({len(train)}), dev ({len(dev)})")

# save data to files
print(f"save data to files...")
write_list_to_json(train, "fol-rules/train_rules.json")
write_list_to_json(test, "fol-rules/test_rules.json")
write_list_to_json(dev, "fol-rules/dev_rules.json")

# get true or false dataset
for data in [test, sampled]:
    if data == test:
        print("generate true/false datasets from the withheld testset.. only considering 1 step T/F")
        outfile = "fol-rules/tf_test_rules.json"
    else:
        print("generate true/false datasets from the dev set.. only considering 1 step T/F")
        outfile = "fol-rules/tf_train_rules.json"
    tf_test = []

    for x in data:
        if "True" in x["exprs"][-1] or "False" in x["exprs"][-1]:
            tf_test.append(x)

    grouped_tests_by_expr_length = defaultdict(list)

    for x in tf_test:
        k = len(x["exprs"])
        if k not in grouped_tests_by_expr_length:
            grouped_tests_by_expr_length[k] = []
        grouped_tests_by_expr_length[k].append(x)

    count_t, count_f = 0,0

    for x in grouped_tests_by_expr_length[2]:
        if "True" in x['rule']:
            count_t += 1
        else:
            count_f += 1

    print("true count: {}, false count: {}".format(count_t, count_f))

    grouped_by_elimination_complexity = defaultdict(list)
    for x in grouped_tests_by_expr_length[2]:
        key = x['elimination_complexity'][0]
        grouped_by_elimination_complexity[key].append(x)

    selected_data = []

    print("frequencies:")
    for k,v in grouped_by_elimination_complexity.items():
        print(f"\telimination complexity: {k}, frequency: {len(v)}")

    for k,v in grouped_by_elimination_complexity.items():
        if len(v)>100:
            selected_data += random.sample(v, 100)
        else:    
            selected_data += v
    print(f"save selected data to {outfile}")
    write_list_to_json(selected_data, outfile)
    print(f"=======")