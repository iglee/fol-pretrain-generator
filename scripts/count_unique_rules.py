import os
import json

def count_unique_fol_types_across_dirs(dir_file_pairs):
    fol_types = set()

    for directory, num_files in dir_file_pairs:
        for i in range(num_files):
            filename = os.path.join(directory, f"segment_{i}.jsonl")
            if not os.path.exists(filename):
                print(f"File not found: {filename}")
                continue

            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if "fol_type" in data:
                            fol_types.add(data["fol_type"])
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in file: {filename}")
    
    print(f"Total unique fol_type values across all files: {len(fol_types)}")
    return fol_types

# Example usage
dir_file_pairs = [
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train_2", 53),  # segment_0.jsonl to segment_9.jsonl
    # Add more as needed
]

unique_fol_types = count_unique_fol_types_across_dirs(dir_file_pairs)



# Example usage
dir_file_pairs = [
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train_2", 40),  # segment_0.jsonl to segment_9.jsonl
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train/curated", 89),   # segment_0.jsonl to segment_99.jsonl
    # Add more as needed
]

unique_fol_types = count_unique_fol_types_across_dirs(dir_file_pairs)


dir_file_pairs = [
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train_2", 40),  # segment_0.jsonl to segment_9.jsonl
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train_repeated_low_complexity", 79),   # segment_0.jsonl to segment_99.jsonl
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train_repeated_mid_complexity", 3),   # segment_0.jsonl to segment_99.jsonl
]

unique_fol_types = count_unique_fol_types_across_dirs(dir_file_pairs)


dir_file_pairs = [
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train_2", 40),  # segment_0.jsonl to segment_9.jsonl
    ("/mnt/isabelle-pretrain-data/fol-pretrain/train_repeated_low_complexity", 138),   # segment_0.jsonl to segment_99.jsonl
    # Add more as needed
]

unique_fol_types = count_unique_fol_types_across_dirs(dir_file_pairs)

