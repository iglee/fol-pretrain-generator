import os
import json
from glob import glob
import tiktoken

def process_jsonl_files(directory):
    tokenizer = tiktoken.get_encoding("gpt2")
    random_data = []
    curated_data = []
    random_count = 0
    curated_count = 0
    random_file_index = 0
    curated_file_index = 0
    total_random_tokens = 0
    total_curated_tokens = 0
    BATCH_SIZE = 100000
    TOKEN_LIMIT = 1024

    def save_data(data, folder, file_index, data_type, token_counter):
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"segment_{file_index}.jsonl")
        with open(file_path, 'w') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
        print(f"Saved {data_type} file: {file_path} | Total {data_type} tokens: {token_counter}")
        return []

    files = sorted(glob(os.path.join(directory, "segment_*")))

    for file_path in files:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    datum = json.loads(line)

                    if "raw_data" not in datum:
                        continue  # skip entries without text

                    # Fix the raw_data and re-tokenize
                    fixed_text = datum["raw_data"].strip() + " <|endoftext|>"
                    tokens = tokenizer.encode(fixed_text, allowed_special={"<|endoftext|>"})

                    if len(tokens) > TOKEN_LIMIT:
                        continue  # skip too-long entries

                    datum["raw_data"] = fixed_text
                    datum["gpt2_tokens"] = tokens
                    datum["num_tokens"] = len(tokens)

                    if "fol_type" in datum and "random" in datum["fol_type"]:
                        random_data.append(datum)
                        random_count += 1
                        total_random_tokens += datum["num_tokens"]
                        if random_count % BATCH_SIZE == 0:
                            random_data = save_data(random_data, os.path.join(directory, "random"),
                                                    random_file_index, "random", total_random_tokens)
                            random_file_index += 1
                    else:
                        curated_data.append(datum)
                        curated_count += 1
                        total_curated_tokens += datum["num_tokens"]
                        if curated_count % BATCH_SIZE == 0:
                            curated_data = save_data(curated_data, os.path.join(directory, "curated"),
                                                     curated_file_index, "curated", total_curated_tokens)
                            curated_file_index += 1
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line in {file_path}")

    # Save any remaining data
    if random_data:
        save_data(random_data, os.path.join(directory, "random"), random_file_index, "random", total_random_tokens)
    if curated_data:
        save_data(curated_data, os.path.join(directory, "curated"), curated_file_index, "curated", total_curated_tokens)

process_jsonl_files("/mnt/isabelle-pretrain-data/fol-pretrain/train")
