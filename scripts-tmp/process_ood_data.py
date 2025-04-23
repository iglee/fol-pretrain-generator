import os
import json 
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm
import random

def example_pack_and_save(data, dir, MAX_LEN=6200):
    UNIQUE_ID = 0
    SAVE_DIR = "/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/test_ood/" + dir
    os.makedirs(SAVE_DIR, exist_ok=True)


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

    for item in data:
            item_length = item['length']
            item_tokens = item['tokens']
            item_string = item['string']
            item_rule = item['rule']['id']

            if current_example['num_tokens'] + item_length > MAX_LEN - 1 and current_example["raw_data"]:
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
                save_path = os.path.join(SAVE_DIR, f"segment_{file_counter}.jsonl")
                with open(save_path, "w") as f:
                    for example in packed_examples:
                        f.write(json.dumps(example) + "\n")
                packed_examples = []  # Reset the list
                file_counter += 1

    # Save any remaining packed_examples
    if packed_examples:
        save_path = os.path.join(SAVE_DIR, f"segment_{file_counter}.jsonl")
        with open(save_path, "w") as f:
            for example in packed_examples:
                f.write(json.dumps(example) + "\n")


def plot_field_histogram(frequencies, title="Frequency Plot"):
    """
    Plots a histogram for the frequency of field values.

    Args:
        frequencies (dict): A dictionary of field values and their frequencies.
        title (str): Title of the histogram.
    """
    labels, counts = zip(*frequencies.items())
    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color='skyblue')
    plt.xlabel("Field Values")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    plt.savefig(f"./{title}.png", format='png', dpi=300)
    plt.show()

directory_path = "/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/test_excluded_data_raw"

all_json_objects = []

for filename in tqdm(os.listdir(directory_path), desc="Processing files"):
    file_path = os.path.join(directory_path, filename)
    # Check if it's a file and has a .jsonl extension
    if os.path.isfile(file_path) and filename.endswith('.jsonl'):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read and parse each line as a JSON object
                all_json_objects.extend(json.loads(line) for line in file)
        except Exception as e:
            print(f"Error reading JSONL file {filename}: {e}")

print(len(all_json_objects))

field_values = [obj["rule"]["total_complexity"] for obj in all_json_objects]
field_values = dict(Counter(field_values))

plot_field_histogram(field_values, "Total_Complexity_Frequency")

field_values = [obj["rule"]["original_complexity"] for obj in all_json_objects]
field_values = dict(Counter(field_values))

plot_field_histogram(field_values, "Original_Complexity_Frequency")

field_values = [obj["rule"]["complexity_by_step"][0] - obj["rule"]["complexity_by_step"][-1] for obj in all_json_objects]
field_values = dict(Counter(field_values))

plot_field_histogram(field_values, "Complexity_Compressibility_Frequency")


tf_1step = []
tf_2step = []
tf_3step = []

for x in all_json_objects:
    if x["rule"]["exprs"][-1] == "True" or x["rule"]["exprs"][-1] == "False":
        if len(x["rule"]["exprs"]) == 2:
            tf_1step.append(x)
        elif len(x["rule"]["exprs"]) == 3:
            tf_2step.append(x)
        elif len(x["rule"]["exprs"]) == 4:
            tf_3step.append(x)

print("\n\n")
print("tf dataset sizes", len(tf_1step), len(tf_2step), len(tf_3step))
print("\n\n")
random.shuffle(tf_1step)
example_pack_and_save(tf_1step[:1000], "tf1", 0)
random.shuffle(tf_2step)
example_pack_and_save(tf_2step[:1000], "tf2", 0)
random.shuffle(tf_3step)
example_pack_and_save(tf_3step[:1000], "tf3", 0)

ocomplex_1 = []
ocomplex_2 = []
ocomplex_3 = []

compressed_1 = []
compressed_2 = []

tcomplex_1 = []
tcomplex_2 = []
tcomplex_3 = []
tcomplex_4 = []

for x in all_json_objects:
    total_complexity = x["rule"]["total_complexity"]
    original_complexity = x["rule"]["original_complexity"]
    compressibility = x["rule"]["complexity_by_step"][0] - x["rule"]["complexity_by_step"][-1]

    if original_complexity <= 23:
        ocomplex_1.append(x)
    elif original_complexity < 40:
        ocomplex_2.append(x)
    else:
        ocomplex_3.append(x)

    if compressibility < 13 and compressibility > 0:
        compressed_1.append(x)
    elif compressibility >= 13:
        compressed_2.append(x)

    if total_complexity <=20:
        tcomplex_1.append(x)
    elif total_complexity < 50:
        tcomplex_2.append(x)
    elif total_complexity < 100:
        tcomplex_3.append(x)
    else:
        tcomplex_4.append(x)

print("original complexity: ",len(ocomplex_1), len(ocomplex_2), len(ocomplex_3))
print("\n\n")
random.shuffle(ocomplex_1)
example_pack_and_save(ocomplex_1[:2000], "original_complexity_1")
random.shuffle(ocomplex_2)
example_pack_and_save(ocomplex_2[:2000], "original_complexity_2")
random.shuffle(ocomplex_3)
example_pack_and_save(ocomplex_3[:2000], "original_complexity_3")

print("total complexity: ",len(tcomplex_1), len(tcomplex_2), len(tcomplex_3), len(tcomplex_4))
print("\n\n")
random.shuffle(tcomplex_1)
example_pack_and_save(tcomplex_1[:2000], "total_complexity_1")
random.shuffle(tcomplex_2)
example_pack_and_save(tcomplex_2[:2000], "total_complexity_2")
random.shuffle(tcomplex_3)
example_pack_and_save(tcomplex_3[:2000], "total_complexity_3")
random.shuffle(tcomplex_4)
example_pack_and_save(tcomplex_4[:2000], "total_complexity_4")


print("compressibility: ",len(compressed_1), len(compressed_2))
print("\n\n")
random.shuffle(compressed_1)
example_pack_and_save(compressed_1[:2000], "compressibility_1")
random.shuffle(compressed_2)
example_pack_and_save(compressed_2[:2000], "compressibility_2")
