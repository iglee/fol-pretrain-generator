import json
import os
from pathlib import Path

def load_all_jsonl_files(directory):
    """Yields JSON objects from all .jsonl files in the given directory."""
    jsonl_files = sorted(Path(directory).glob("*.jsonl"))
    for filepath in jsonl_files:
        with open(filepath, 'r') as f:
            for line in f:
                yield json.loads(line)

def save_chunk(chunk_data, output_dir, chunk_idx):
    """Save a list of packed examples to a chunked output file."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = Path(output_dir) / f"packed_{chunk_idx:04d}.jsonl"
    with open(out_path, 'w') as f:
        for item in chunk_data:
            f.write(json.dumps(item) + '\n')
    print(f"✅ Saved {len(chunk_data)} packed examples to {out_path}")

def pack_examples_from_dir(input_dir, output_dir, max_seq_length=2048, eos_token_id=None, chunk_size=1000):
    dataset = load_all_jsonl_files(input_dir)

    packed = []
    current_pack = {
        "tokens": [],
        "example_ids": [],
        "rule_ids": [],
        "length": 0
    }
    current_len = 0
    chunk_counter = 0

    for item in dataset:
        tokens = item["tokens"]
        length = len(tokens)
        if eos_token_id is not None:
            tokens = tokens + [eos_token_id]
            length += 1
        if length > max_seq_length:
            print(f"⚠️ Skipping example id={item['id']} (length {length} > max {max_seq_length})")
            continue

        if current_len + length <= max_seq_length:
            current_pack["tokens"].extend(tokens)
            current_pack["example_ids"].append(item["id"])
            current_pack["rule_ids"].append(item["rule_id"])
            current_len += length
            current_pack["length"] = current_len
        else:
            packed.append(current_pack)
            if len(packed) >= chunk_size:
                save_chunk(packed, output_dir, chunk_counter)
                packed = []
                chunk_counter += 1

            current_pack = {
                "tokens": tokens[:],
                "example_ids": [item["id"]],
                "rule_ids": [item["rule_id"]],
                "length": length
            }
            current_len = length

    if current_pack["tokens"]:
        packed.append(current_pack)
    if packed:
        save_chunk(packed, output_dir, chunk_counter)

# ==== Example usage ====
if __name__ == "__main__":
    input_path = "/mnt/isabelle-pretrain-data/fol-3/raw/train/"
    output_path = "/mnt/isabelle-pretrain-data/fol-3/packed/train/"
    pack_examples_from_dir(input_path, output_path, max_seq_length=1024, eos_token_id=None)