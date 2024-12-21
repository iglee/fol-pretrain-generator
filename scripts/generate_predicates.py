import os
import time
from src.gpt_util import read_file_into_list, load_config, process_prompt, prompt_chatgpt_from_config, extract_and_append_json

topics = read_file_into_list("data/topics")

if os.path.exists("data/predicates.jsonl"):
    os.remove("data/predicates.jsonl")

max_retries = 3  # Set the maximum number of retries
retry_delay = 2  # Delay between retries (in seconds)


for x in topics:
    
    retries = 0
    while retries < max_retries:
        try:
            # Generate the response and append to the JSON file
            config = load_config("config/prompt_for_predicates.yaml")
            config["prompt"] = process_prompt(config["prompt"].format(topic=x))
            
            response = prompt_chatgpt_from_config(config)
            response_lines = response.splitlines()
            
            # Remove the first and last lines if there are enough lines
            if response_lines[0].startswith("```"):
                response_lines = response_lines[1:-1]  # Remove first and last lines
            
            # Join the lines back into a cleaned response
            cleaned_response = "\n".join(response_lines)
            
            # Attempt to extract and append the JSON data
            extract_and_append_json(cleaned_response, "data/predicates.jsonl")
            break
            
        except Exception as e:
            retries += 1
            print(f"Error processing topic '{x}': {e}")
            if retries < max_retries:
                print(f"Retrying... ({retries}/{max_retries})")
                time.sleep(retry_delay)  # Wait before retrying
            else:
                print(f"Failed after {max_retries} retries. Skipping topic '{x}'.")