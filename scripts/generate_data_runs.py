from src.generate_data import generate_data, rules_data
import os
import json
import random
from tqdm import tqdm

# Global counters for IDs
id_counter = {
    "train": 0,  # Shared counter for train and basic data
    "test": 0,   # Separate counter for test data
}


def process_and_save(data, output_dir, chunk_size=3000, data_type="train"):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating and saving {data_type} data without shuffling...")
    buffer = []
    file_counter = 0

    counter_type = "train" if data_type in ["train", "basic"] else "test"
    current_id = id_counter[counter_type]  # Starting ID

    for rule in tqdm(data, desc=f"Processing {data_type} rules"):
        generated = generate_data(
            rule_datum=rule,
            data_type=data_type,
            temp_dir=None,
            i_start=current_id
        )

        if not isinstance(generated, list):
            continue

        if generated:
            current_id = int(generated[-1]["id"].split("_")[1]) + 1

        buffer.extend(generated)

        while len(buffer) >= chunk_size:
            #chunk = buffer[:chunk_size]
            #buffer = buffer[chunk_size:]
            chunk = buffer[:]
            buffer = []
            file_path = os.path.join(output_dir, f"split_{file_counter + 1}.jsonl")
            with open(file_path, "w", encoding="utf-8") as f:
                for item in chunk:
                    json.dump(item, f, ensure_ascii=False)
                    f.write("\n")
            file_counter += 1

    # Save any remaining items in the buffer
    if buffer:
        file_path = os.path.join(output_dir, f"split_{file_counter + 1}.jsonl")
        with open(file_path, "w", encoding="utf-8") as f:
            for item in buffer:
                json.dump(item, f, ensure_ascii=False)
                f.write("\n")

    print(f"\nDone! Saved all generated data in {file_counter + 1} file(s).")
    return current_id


# Runner block
for k, v in rules_data.items():
    data_type = "_".join(k.split("_")[:-1])
    print(f"Processing: {data_type}")
    
    if data_type == "train":
        output_dir = os.path.join("/mnt/isabelle-pretrain-data/fol-pretrain/raw", data_type)
        temp_dir = os.path.join("/mnt/isabelle-pretrain-data/fol-3/tmp", data_type)
        id_counter['train'] = process_and_save(
            data=v,
            output_dir=output_dir,
            chunk_size=10000,
            data_type=data_type,  # RERUN BASIC
        )
    elif data_type in ["dev", "test"]:
        output_dir = os.path.join("/mnt/isabelle-pretrain-data/fol-pretrain/raw", data_type)
        temp_dir = os.path.join("/mnt/isabelle-pretrain-data/fol-3/tmp", data_type)
        process_and_save(
            data=v,
            output_dir=output_dir,
            chunk_size=10000,
            data_type="test",
            temp_dir=temp_dir
        )
