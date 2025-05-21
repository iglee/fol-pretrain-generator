import os
import json
import random
from tqdm import tqdm
from math import ceil

BATCH_SIZE = 100_000

def load_json_objects_from_jsonl_files(directory):
    data = []
    filenames = os.listdir(directory)
    for filename in tqdm(filenames, desc="Reading JSONL files"):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            obj = json.loads(line)
                            data.append(obj)
                        except json.JSONDecodeError:
                            print(f"Skipping invalid JSON line in {filename}")
    return data

def write_batches_as_jsonl(data, output_dir, batch_size=BATCH_SIZE):
    os.makedirs(output_dir, exist_ok=True)
    total_batches = ceil(len(data) / batch_size)

    for i in tqdm(range(total_batches), desc="Writing shuffled JSONL batches"):
        batch = data[i * batch_size : (i + 1) * batch_size]
        output_path = os.path.join(output_dir, f"segment_{i}.jsonl")
        with open(output_path, 'w', encoding='utf-8') as out_file:
            for obj in batch:
                json.dump(obj, out_file, ensure_ascii=False)
                out_file.write('\n')

def main():
    input_dir = '/mnt/isabelle-pretrain-data/fol-pretrain/train_repeated_mid_complexity'
    output_subdir = os.path.join(input_dir, 'shuffled_segments')

    data = load_json_objects_from_jsonl_files(input_dir)
    random.shuffle(data)
    write_batches_as_jsonl(data, output_subdir)

if __name__ == '__main__':
    main()