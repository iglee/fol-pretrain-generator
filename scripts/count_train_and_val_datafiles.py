from src.fol_util import read_jsonl_to_list
import os
from tqdm import tqdm
import random

# File paths and dataset size configurations
file_prefix = "/mnt/isabelle-pretrain-data/packed_training_examples/packed_examples_"
model_sizes = [44.646912, 123.653376, 353.774592, 772.71936]  # in millions
dataset_sizes = [x * 1e6 * 20 * 1.01 for x in model_sizes]  # dataset sizes in tokens
dataset_names = ["nanogpt-smaller", "nanogpt-small", "nanogpt-medium", "nanogpt-large"]

# Set random seed for reproducibility
random.seed(42)

# Find the maximum number of files in the directory
def get_max_file_count(file_prefix):
    """
    Determines the maximum number of files in the directory with the given prefix.

    Args:
        file_prefix (str): The file prefix to check for numbered files.

    Returns:
        int: The total number of files in the directory.
    """
    index = 0
    while os.path.exists(f"{file_prefix}{index}.jsonl"):
        index += 1
    return index

max_files = get_max_file_count(file_prefix)

# Function to find how many files are needed to meet dataset sizes
def find_files_needed(file_prefix, max_files, dataset_sizes):
    """
    Determines how many files are required to meet each dataset size in `dataset_sizes`.

    Args:
        file_prefix (str): File prefix to generate filenames (e.g., "segment_").
        max_files (int): The maximum number of files available.
        dataset_sizes (list): List of dataset sizes in tokens.

    Returns:
        dict: Mapping of dataset sizes to number of files needed.
    """
    file_counts = {}
    for size in dataset_sizes:
        total_tokens = 0
        files_used = 0

        for file_index in tqdm(range(max_files), desc=f"Processing for {size:.0f} tokens"):
            filename = f"{file_prefix}{file_index}.jsonl"

            try:
                # Read the JSONL file
                data = read_jsonl_to_list(filename)

                # Sum tokens from the `num_tokens` field
                total_tokens += sum(item.get('num_tokens', 0) for item in data)
                files_used += 1

                # Check if the target size has been reached
                if total_tokens >= size:
                    file_counts[size] = files_used
                    break
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

        # If the size is not reached
        if size not in file_counts:
            file_counts[size] = -1  # Indicate failure

    return file_counts

# Find files needed for each dataset size
file_counts = find_files_needed(file_prefix, max_files, dataset_sizes)

# Output the results
for dataset_name, size, count in zip(dataset_names, dataset_sizes, file_counts.values()):
    if count == -1:
        print(f"{dataset_name} ({size:.0f} tokens): Could not be reached with available files.")
    else:
        print(f"{dataset_name} ({size:.0f} tokens): Requires {count} files.")
