from src.fol_util import read_jsonl_to_list
import glob
import os
from tqdm import tqdm
import json
import random

# File paths and dataset size configurations
files = glob.glob("/mnt/isabelle-pretrain-data/packed_training_examples/*")
model_sizes = [44.646912, 123.653376, 353.774592, 772.71936]  # in millions
dataset_sizes = [x * 1e6 * 20.5 for x in model_sizes]  # dataset sizes in examples
dataset_names = ["nanogpt-smaller", "nanogpt-small", "nanogpt-medium", "nanogpt-large"]

# Output directory for datasets
output_dir = "/mnt/isabelle-pretrain-data/datasets"
os.makedirs(output_dir, exist_ok=True)

# Set random seed for reproducibility
random.seed(42)

# Create datasets of specified sizes
for i, (max_size, name) in enumerate(zip(dataset_sizes, dataset_names)):
    dataset = []
    current_size = 0

    print(f"Creating dataset '{name}' with target size: {max_size} examples")

    for file in tqdm(files, desc=f"Building Dataset '{name}'"):
        data = read_jsonl_to_list(file)

        for datum in data:
            dataset.append(datum)
            current_size += datum["length"]

            # Stop adding to dataset once the size limit is reached
            if current_size >= max_size:
                break
        if current_size >= max_size:
            break

    # Shuffle the dataset for random validation sampling
    random.shuffle(dataset)

    # Create validation set with 0.1% of the data
    val_size = max(1, int(0.001 * len(dataset)))  # Ensure at least 1 example
    validation_set = dataset[:val_size]
    training_set = dataset[val_size:]

    # Save the training dataset to a file
    output_file_train = os.path.join(output_dir, f"dataset-{name}.jsonl")
    with open(output_file_train, "w") as f:
        for entry in training_set:
            f.write(json.dumps(entry) + "\n")
    print(f"Training Dataset 'dataset-{name}' created: {output_file_train}, Total size: {len(training_set)} examples")

    # Save the validation dataset to a file
    output_file_val = os.path.join(output_dir, f"dataset-{name}_val.jsonl")
    with open(output_file_val, "w") as f:
        for entry in validation_set:
            f.write(json.dumps(entry) + "\n")
    print(f"Validation Dataset 'dataset-{name}' created: {output_file_val}, Total size: {len(validation_set)} examples")
