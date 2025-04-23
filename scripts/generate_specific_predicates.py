import os
import time
from src.gpt_util import read_file_into_list, load_config, process_prompt, prompt_chatgpt_from_config, extract_and_append_json
import ast
import json
from tqdm import tqdm

def parse_predicate_list(predicate_string):
    try:
        predicate_string = predicate_string.strip()
        if predicate_string.startswith("```python"):
            predicate_string = predicate_string[len("```python"):].strip()
        if predicate_string.endswith("```"):
            predicate_string = predicate_string[:-3].strip()
        predicates = ast.literal_eval(predicate_string)
        if isinstance(predicates, list):
            return predicates
        else:
            raise ValueError("Input is not a list.")
    except Exception as e:
        print(f"Error parsing predicate list: {e}")
        return None


topics = read_file_into_list("data/topics")

if os.path.exists("data/predicates.jsonl"):
    os.remove("data/predicates.jsonl")

topic_predicates = {}


for _ in tqdm(range(40), desc="Processing", unit="iteration"):
    for x in ["Harry Potter"]:
        config = load_config("config/prompt_for_predicates_harrypotter.yaml")
        config["prompt"] = process_prompt(config["prompt"])
        
        response = prompt_chatgpt_from_config(config)
        predicates = parse_predicate_list(response)
        
        # Initialize a set for the topic if it doesn't exist
        if x not in topic_predicates:
            topic_predicates[x] = set()
        
        # Update the set for the topic with the new predicates
        if predicates:
            topic_predicates[x].update(predicates)


# Print the total unique predicates for each topic
for topic, preds in topic_predicates.items():
    print(f"Total unique predicates for topic '{topic}': {len(preds)}")

# Convert the dictionary to a regular list of predicates for each topic
topic_predicates_list = {topic: list(preds) for topic, preds in topic_predicates.items()}

# Save the dictionary of lists to a file using JSON
with open('data/topic_predicates_harrypotter.json', 'w') as file:
    json.dump(topic_predicates_list, file)