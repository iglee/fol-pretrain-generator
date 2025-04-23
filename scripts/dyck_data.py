from src.generate_data import tokenize_with_cl100k_base, read_file_lines
import json
import os
from tqdm import tqdm

def process_dyck_data(k: int, m: int, input_base_path: str, output_base_path: str, start_index: int):
    split_names = ['train', 'dev', 'test']
    current_index = start_index
    output_file = os.path.join(output_base_path, f"dyck_k{k}m{m}.jsonl")

    with open(output_file, 'w') as out_f:
        for split in split_names:
            input_filename = f"k{k}_m{m}_tr2000000.{split}"
            input_file = os.path.join(input_base_path, input_filename)
            data = read_file_lines(input_file)

            # Add tqdm to track progress while processing each line
            for line in tqdm(data, total=len(data), desc=f"Processing {split} split for k={k}, m={m}", ncols=100):
                line = line.removesuffix(" END").strip()
                datum = f"<|endoftext|> {line}"
                tokens, length = tokenize_with_cl100k_base(datum)
                entry = {
                    "id": f"dyck_{current_index}",
                    "rule_id": f"dyck_k{k}m{m}",
                    "datum": datum,
                    "tokens": tokens,
                    "length": length
                }
                out_f.write(json.dumps(entry) + '\n')

                current_index += 1  # Increment for continuous index across splits

    return current_index  # Return the last index used (for tracking purposes)

def main():
    input_base = "dyckkm-learning/data"
    output_base = "/mnt/isabelle-pretrain-data/fol-pretrain/raw/dyck"
    os.makedirs(output_base, exist_ok=True)

    km_pairs = [(8, 4), (8, 8), (32, 4), (32, 8)]
    all_index_info = {}
    global_index = 0  # Start with an initial index

    for k, m in km_pairs:
        print(f"Processing k={k}, m={m}...")
        global_index = process_dyck_data(k, m, input_base, output_base, global_index)
        all_index_info[(k, m)] = global_index

    print("\nFinal index summary:")
    for (k, m), last_index in all_index_info.items():
        print(f"  k={k}, m={m} -> Last index used: {last_index}")

if __name__ == "__main__":
    main()
