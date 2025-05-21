import os
import random
import json

def segment_jsonl_files_with_token_count(source_dir, output_dir, num_files=62, num_lines=100000):
    all_files = [f for f in os.listdir(source_dir) if f.endswith('.jsonl')]
    selected_files = random.sample(all_files, min(num_files, len(all_files)))

    total_tokens = 0

    for i, filename in enumerate(selected_files):
        input_path = os.path.join(source_dir, filename)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"segment_{i}.jsonl")

        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:

            for line_num, line in enumerate(infile):
                if line_num >= num_lines:
                    break
                try:
                    obj = json.loads(line)
                    tokens = obj.get("num_tokens", 0)
                    total_tokens += tokens
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON lines

                outfile.write(line)
    
    print(f"Processed {len(selected_files)} files.")
    print(f"Total tokens across all processed segments: {total_tokens:,}")

# Example usage
source_directory = "/mnt/isabelle-pretrain-data/fol-pretrain/basic"
output_directory = "/mnt/isabelle-pretrain-data/fol-pretrain/basic/random_selection"
segment_jsonl_files_with_token_count(source_directory, output_directory)
