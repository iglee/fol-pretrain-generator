from src.fol_util import read_jsonl_to_list
import glob
import os
from tqdm import tqdm
import json
import random

# File paths and dataset size configurations
files = glob.glob("/mnt/isabelle-pretrain-data/packed_training_examples/*")
model_sizes = [44.646912, 123.653376, 353.774592, 772.71936]  # in millions
dataset_sizes = [x * 1e6 * 20.5 for x in model_sizes]  # dataset sizes in tokens
dataset_names = ["nanogpt-smaller", "nanogpt-small", "nanogpt-medium", "nanogpt-large"]

# Output directory for datasets
output_dir = "/mnt/isabelle-pretrain-data/datasets"
os.makedirs(output_dir, exist_ok=True)

# Set random seed for reproducibility
random.seed(42)

# Create datasets of specified sizes
for max_size, name in zip(dataset_sizes, dataset_names):
    current_size = 0
    training_file = os.path.join(output_dir, f"dataset-{name}.jsonl")
    validation_file = os.path.join(output_dir, f"dataset-{name}_val.jsonl")

    print(f"Creating dataset '{name}' with target size: {max_size} tokens")

    with open(training_file, "w") as train_f, open(validation_file, "w") as val_f:
        val_buffer = []
        for file in tqdm(files, desc=f"Building Dataset '{name}'"):
            data = read_jsonl_to_list(file)

            for datum in data:
                if current_size < max_size:
                    

                    # Collect 0.1% of data for validation
                    if random.random() < 0.001:
                        val_buffer.append(datum)
                    else:
                        train_f.write(json.dumps(datum) + "\n")
                    current_size += datum["length"]

                if current_size >= max_size:
                    break
            if current_size >= max_size:
                break

        # Write the validation set at the end
        for val_entry in val_buffer:
            val_f.write(json.dumps(val_entry) + "\n")

    print(f"Training Dataset 'dataset-{name}' created: {training_file}, Total tokens: {current_size}")
    print(f"Validation Dataset 'dataset-{name}' created: {validation_file}, Total examples: {len(val_buffer)}")
