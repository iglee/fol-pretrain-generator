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
        
def retrieve_batches_by_metadata(project_name=None, run_date=None):
    # List all batches from OpenAI API
    batches = openai.Batch.list()

    # Filter batches by metadata
    filtered_batches = []
    for batch in batches['data']:
        batch_metadata = batch.get("metadata", {})

        # Check if batch metadata matches the provided filters
        if (project_name and batch_metadata.get("project") == project_name) or \
           (run_date and batch_metadata.get("run_date") == run_date):
            filtered_batches.append(batch)

    # If no matching batches, print a message
    if not filtered_batches:
        print("No batches found matching the provided metadata.")
    else:
        # Return or process matching batches
        for batch in filtered_batches:
            print(f"Batch ID: {batch['id']}")
            print(f"Project: {batch['metadata'].get('project')}")
            print(f"Run Date: {batch['metadata'].get('run_date')}")
            print(f"Status: {batch['status']}")
            print(f"Link: https://platform.openai.com/batch/{batch['id']}")
            print("-" * 50)

    return filtered_batches