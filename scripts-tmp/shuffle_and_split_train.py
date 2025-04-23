import os
import json
import random
from tqdm import tqdm

temp_dir = "/mnt/isabelle-pretrain-data/fol-3/tmp/train"
output_dir = "/mnt/isabelle-pretrain-data/fol-3/raw/train"
chunk_size = 10000
shuffle_passes = 5

def pairwise_shuffle(file1_path, file2_path, temp_dir):
    temp_file1 = os.path.join(temp_dir, "temp1.jsonl")
    temp_file2 = os.path.join(temp_dir, "temp2.jsonl")

    lines = []

    # Read both files into memory (line-wise)
    with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
        lines.extend(f1.readlines())
        lines.extend(f2.readlines())

    random.shuffle(lines)

    mid = len(lines) // 2

    # Write back to original files
    with open(temp_file1, 'w', encoding='utf-8') as out1:
        out1.writelines(lines[:mid])
    with open(temp_file2, 'w', encoding='utf-8') as out2:
        out2.writelines(lines[mid:])

    os.replace(temp_file1, file1_path)
    os.replace(temp_file2, file2_path)

def multi_pass_shuffle(file_paths, temp_dir, passes=5):
    print(f"Shuffling files with {passes} passes...")
    for _ in tqdm(range(passes), desc="Shuffling"):
        shuffled_files = file_paths[:]
        random.shuffle(shuffled_files)
        pairs = list(zip(shuffled_files[::2], shuffled_files[1::2]))
        print(pairs)
        for file1, file2 in pairs:
            pairwise_shuffle(file1, file2, temp_dir)

def save_shuffled_chunks(file_paths, chunk_size, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    current_chunk = []
    chunk_index = 1
    total_records = 0

    def save_chunk(chunk, idx):
        file_path = os.path.join(output_dir, f"split_{idx:05d}.jsonl")
        with open(file_path, "w", encoding="utf-8") as f:
            for item in chunk:
                json.dump(item, f, ensure_ascii=False)
                f.write("\n")

    print("Saving shuffled chunks...")
    for file_path in tqdm(file_paths, desc="Processing files"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    current_chunk.append(item)
                    total_records += 1
                except json.JSONDecodeError:
                    continue

                if len(current_chunk) >= chunk_size:
                    save_chunk(current_chunk, chunk_index)
                    chunk_index += 1
                    current_chunk = []

    if current_chunk:
        save_chunk(current_chunk, chunk_index)

    print(f"\nDone! Saved {total_records} records in {chunk_index} files.")

# === Run the full pipeline ===

# Step 1: Get all jsonl files
file_paths = sorted([
    os.path.join(temp_dir, fname)
    for fname in os.listdir(temp_dir)
    if fname.endswith(".jsonl")
])

# Step 2: Shuffle across files
multi_pass_shuffle(file_paths, temp_dir, passes=shuffle_passes)

# Step 3: Save shuffled output to chunked files
save_shuffled_chunks(file_paths, chunk_size, output_dir)
