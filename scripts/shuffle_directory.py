import json
import random
import glob
import os
from tqdm import tqdm

# Path to your directory with JSONL files
directory = "/mnt/isabelle-pretrain-data/training_data_v2"
jsonl_files = glob.glob(os.path.join(directory, "*.jsonl"))

# Initialize tqdm for the outer loop
with tqdm(total=len(jsonl_files) // 2, desc="Merging files") as pbar:
    while len(jsonl_files) > 1:
        # Randomly pick two files
        file1, file2 = random.sample(jsonl_files, 2)

        # Load data from file1
        with open(file1, "r") as f:
            data1 = [json.loads(line) for line in f]

        # Load data from file2
        with open(file2, "r") as f:
            data2 = [json.loads(line) for line in f]

        # Combine, shuffle, and split data
        combined_data = data1 + data2
        random.shuffle(combined_data)

        # Save back to file1
        with open(file1, "w") as f:
            for item in tqdm(combined_data[:len(data1)], desc=f"Writing to {os.path.basename(file1)}", leave=False):
                f.write(json.dumps(item) + "\n")

        # Save back to file2
        with open(file2, "w") as f:
            for item in tqdm(combined_data[len(data1):], desc=f"Writing to {os.path.basename(file2)}", leave=False):
                f.write(json.dumps(item) + "\n")

        # Remove the processed files from the list
        jsonl_files.remove(file1)
        jsonl_files.remove(file2)

        # Update progress bar
        pbar.update(1)

# If there's an unpaired file left, leave it untouched
if jsonl_files:
    print(f"Unpaired file left: {jsonl_files[0]}")
