import os
import json

def process_jsonl_line(line):
    """
    Process a single line of a JSONL file.
    Replace this function with your desired processing logic.
    """
    data = json.loads(line)

    new = {
        "id": data["id"],
        "gpt2_tokens": [50256]+ data["gpt2_tokens"] +[50256],
        "num_tokens": data["num_tokens"]+2,
        "raw_data": "<|endoftext|> " + data["raw_data"] + " <|endoftext|>",
        "fol_rules": [data["fol_type"]],
        "datum_ids": []
    }

    return json.dumps(new)

def process_jsonl_files(source_dir, target_dir):
    """
    Reads all .jsonl files from the source directory, processes them, 
    and saves them under the same name in the target directory.
    
    Args:
        source_dir (str): Path to the source directory containing JSONL files.
        target_dir (str): Path to the target directory to save processed files.
    """
    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    for filename in os.listdir(source_dir):
        if filename.endswith('.jsonl'):
            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)

            with open(source_path, 'r', encoding='utf-8') as infile, \
                 open(target_path, 'w', encoding='utf-8') as outfile:
                
                for line in infile:
                    processed_line = process_jsonl_line(line.strip())
                    outfile.write(processed_line + '\n')
                    
            print(f"Processed and saved: {filename}")

# Example usage
source_directory = "/mnt/isabelle-pretrain-data/fol-pretrain/test-dyck"
target_directory = "/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/test_dyck"

process_jsonl_files(source_directory, target_directory)
