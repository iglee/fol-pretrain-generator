from openai import OpenAI
import os
import yaml
import random
import json
from tqdm import tqdm

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def process_prompt(prompt, system_instruction="You're a helpful assistant designed for creating synthetic data."):
    return [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]


def batch_prompt_items(prompt):
    return {"method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4o", "messages": prompt}}

def save_batch_list_to_jsonl(batches, chunk_size=1000, base_filename="batch", base_dir="."):
    os.makedirs(base_dir, exist_ok=True)  # Ensure the directory exists

    for i in range(0, len(batches), chunk_size):
        chunk = batches[i:i+chunk_size]
        filename = os.path.join(base_dir, f"{base_filename}_{i//chunk_size + 1}.jsonl")
        with open(filename, "w", encoding="utf-8") as f:
            for obj in chunk:
                f.write(json.dumps(obj) + "\n")
        print(f"Saved {len(chunk)} items to {filename}")

def start_batch_jobs_from_dir(batch_dir, project_name="fol_pretrain", run_date="2025-04-22"):
    # Iterate through each file in the batch directory
    for filename in tqdm(os.listdir(batch_dir), desc="Processing files"):
        if filename.endswith(".jsonl"):
            file_path = os.path.join(batch_dir, filename)

            with open(file_path, "rb") as f:
                batch_input_file = client.files.create(
                    file=f,
                    purpose="batch"
                )
                
                metadata = {
                    "project": project_name,
                    "run_date": run_date,
                    "source_file": filename,
                }

                batch_input_file_id = batch_input_file.id
                client.batches.create(
                    input_file_id=batch_input_file_id,
                    endpoint="/v1/chat/completions",
                    completion_window="24h",
                    metadata=metadata
                )
        
def get_response_from_batch_items(x):
    return x['response']['body']['choices'][0]['message']['content']