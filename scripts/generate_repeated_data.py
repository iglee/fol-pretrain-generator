import json
import os
from scripts.generate_data_runs import process_and_save

###
input_path = '/home/isabelle/fol-pretrain-generator/fol-rules/sampled_train_low.json'

# Load the whole array
with open(input_path, 'r', encoding='utf-8') as infile:
    repeated_rules = json.load(infile)

data_type = "train_repeated_low_complexity"

output_dir = os.path.join("/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/", data_type)
id_train = process_and_save(
    data=repeated_rules,
    output_dir=output_dir,
    chunk_size=100000,
    data_type="basic"  
)


###
input_path = '/home/isabelle/fol-pretrain-generator/fol-rules/sampled_train_mid.json'

# Load the whole array
with open(input_path, 'r', encoding='utf-8') as infile:
    repeated_rules = json.load(infile)

data_type = "train_repeated_mid_complexity"

output_dir = os.path.join("/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/", data_type)
id_train = process_and_save(
    data=repeated_rules,
    output_dir=output_dir,
    chunk_size=100000,
    data_type="basic"  
)


###
input_path = '/home/isabelle/fol-pretrain-generator/fol-rules/sampled_train_high.json'

# Load the whole array
with open(input_path, 'r', encoding='utf-8') as infile:
    repeated_rules = json.load(infile)

data_type = "train_repeated_high_complexity"

output_dir = os.path.join("/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/", data_type)
id_train = process_and_save(
    data=repeated_rules,
    output_dir=output_dir,
    chunk_size=100000,
    data_type="basic"  
)