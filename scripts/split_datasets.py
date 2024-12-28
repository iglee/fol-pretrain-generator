import os
import json
import random
from tqdm import tqdm

# Directories
input_dir = "/mnt/isabelle-pretrain-data/packed_training_examples/"
train_dir = "/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/train/"
validation_dir = "/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/validation/"

# Create output directories if they don't exist
os.makedirs(train_dir, exist_ok=True)
os.makedirs(validation_dir, exist_ok=True)

# Random seed for reproducibility
random.seed(42)

# Get the total number of files in the directory
def get_file_count(directory, prefix):
    """
    Counts the number of files with the given prefix in a directory.

    Args:
        directory (str): The path to the directory.
        prefix (str): The prefix of the filenames to count.

    Returns:
        int: The total number of files with the specified prefix.
    """
    count = 0
    while os.path.exists(os.path.join(directory, f"{prefix}{count}.jsonl")):
        count += 1
    return count

file_prefix = "packed_examples_"
total_files = get_file_count(input_dir, file_prefix)

# Function to split data
def split_jsonl(file_path, train_dir, validation_dir, file_index):
    """
    Splits a JSONL file into training and validation datasets.

    Args:
        file_path (str): Path to the input JSONL file.
        train_dir (str): Directory to save the training files.
        validation_dir (str): Directory to save the validation files.
        file_index (int): File index for naming the output files.
    """
    train_data = []
    validation_data = []

    with open(file_path, "r") as f:
        lines = [json.loads(line.strip()) for line in f]

    # Randomly sample 1% of the data for validation
    validation_size = max(1, int(0.01 * len(lines)))  # Ensure at least 1 sample
    validation_data = random.sample(lines, validation_size)
    validation_set = set(json.dumps(item) for item in validation_data)

    # Filter out validation data from the original set
    train_data = [line for line in lines if json.dumps(line) not in validation_set]

    # Write train and validation data to separate files
    with open(os.path.join(train_dir, f"segment_{file_index}.jsonl"), "w") as train_file:
        for item in train_data:
            train_file.write(json.dumps(item) + "\n")

    with open(os.path.join(validation_dir, f"segment_{file_index}.jsonl"), "w") as val_file:
        for item in validation_data:
            val_file.write(json.dumps(item) + "\n")

# Process files sequentially
for idx in tqdm(range(total_files), desc="Splitting files"):
    file_path = os.path.join(input_dir, f"{file_prefix}{idx}.jsonl")
    split_jsonl(file_path, train_dir, validation_dir, idx)
