import random
import json
import os
from pathlib import Path
from typing import Union, List
from tqdm import tqdm

def load_all_jsonl_files(input_source: Union[str, Path, List[str], List[Path]]):
    """Yields JSON objects from all .jsonl files in the input path(s)."""
    if isinstance(input_source, (str, Path)):
        input_source = Path(input_source)
        if input_source.is_dir():
            jsonl_files = sorted(input_source.glob("*.jsonl"))
        elif input_source.is_file():
            jsonl_files = [input_source]
        else:
            raise ValueError(f"Input path {input_source} is neither a directory nor a valid file.")
    elif isinstance(input_source, list):
        jsonl_files = [Path(p) for p in input_source]
    else:
        raise TypeError("Input must be a path, file, or list of file paths.")

    for filepath in tqdm(jsonl_files, desc="📂 Loading .jsonl files"):
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

def pack_examples_from_input(input_source,
                             output_dir,
                             max_seq_length=2048,
                             eos_token_id=None,
                             chunk_size=3000,
                             start_pack_idx=0,
                             shuffle=True) -> int:
    """
    Pack tokenized examples into blocks with max token length.

    Returns:
        next_pack_idx: next available unique pack ID
    """
    dataset = load_all_jsonl_files(input_source)
    dataset_list = list(dataset)
    print(f"📦 Found {len(dataset_list)} examples to process.")
    if shuffle:
        random.shuffle(dataset_list)

    packed = []
    chunk_counter = 0
    current_pack_idx = start_pack_idx

    current_pack = {
        "tokens": [],
        "example_ids": [],
        "rule_ids": [],
        "packed_seq_lengths": [],
        "length": 0
    }
    current_len = 0

    # Reserve space for EOS token if needed
    max_pack_len = max_seq_length - 1 if eos_token_id is not None else max_seq_length

    for item in tqdm(dataset_list, desc="🚀 Packing examples"):
        tokens = item["tokens"]
        length = item["length"]  # Use provided length

        if length > max_pack_len:
            #tqdm.write(f"⚠️ Skipping example id={item['id']} (length {length} > max {max_pack_len})")
            continue

        if current_len + length <= max_pack_len:
            current_pack["tokens"].extend(tokens)
            current_pack["example_ids"].append(item["id"])
            current_pack["rule_ids"].append(item["rule_id"])
            current_pack["packed_seq_lengths"].append(length)
            current_len += length
            current_pack["length"] = current_len
        else:
            # Finalize current pack
            if eos_token_id is not None:
                current_pack["tokens"].append(eos_token_id)
                current_pack["length"] += 1
                current_len += 1
                current_pack["packed_seq_lengths"][-1] += 1  # Update length of last example

            current_pack["pack_id"] = current_pack_idx
            packed.append(current_pack)
            current_pack_idx += 1

            if len(packed) >= chunk_size:
                save_chunk(packed, output_dir, chunk_counter)
                packed = []
                chunk_counter += 1

            # Start new pack
            current_pack = {
                "tokens": tokens[:],
                "example_ids": [item["id"]],
                "rule_ids": [item["rule_id"]],
                "packed_seq_lengths": [length],
                "length": length
            }
            current_len = length

    # Final pack
    if current_pack["tokens"]:
        if eos_token_id is not None:
            current_pack["tokens"].append(eos_token_id)
            current_pack["length"] += 1
            current_pack["packed_seq_lengths"][-1] += 1
        current_pack["pack_id"] = current_pack_idx
        packed.append(current_pack)
        current_pack_idx += 1

    if packed:
        save_chunk(packed, output_dir, chunk_counter)

    return current_pack_idx  # Return the next available unique pack ID
"""
input_path = "/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/raw/test/"
output_path = "/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/packed/test/"

next_id = pack_examples_from_input(
    input_source=input_path,        # single .jsonl file as input
    output_dir=output_path,      # where to write packed_0000.jsonl, etc.
    max_seq_length=1024,
    eos_token_id=100257,
    chunk_size=3000,
    start_pack_idx=0
)

input_path = "/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/raw/dev/"
output_path = "/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/packed/dev/"

next_id = pack_examples_from_input(
    input_source=input_path,        # single .jsonl file as input
    output_dir=output_path,      # where to write packed_0000.jsonl, etc.
    max_seq_length=1024,
    eos_token_id=100257,
    chunk_size=3000,
    start_pack_idx=0
)
"""
input_path = "/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/raw/train/"
output_path = "/mnt/isabelle-pretrain-data/dataset_v3/fol-pretrain/packed/train/"

next_id = pack_examples_from_input(
    input_source=input_path,        # single .jsonl file as input
    output_dir=output_path,      # where to write packed_0000.jsonl, etc.
    max_seq_length=1024,
    eos_token_id=100257,
    chunk_size=3000,
    start_pack_idx=68293+1
)

