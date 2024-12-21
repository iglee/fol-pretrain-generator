from openai import OpenAI
import os
import yaml
import random
import json

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def read_file_into_list(file_path):
    """Reads the entire file and returns its contents as a list of lines."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Strip newline characters from each line
    return [line.strip() for line in lines]

def load_config(file_path):
    """Loads the prompting configuration from a YAML file."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def process_prompt(prompt, system_instruction="You're a helpful assistant designed for creating synthetic data"):
    return [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]


def prompt_chatgpt_from_config(config):
    """Reads a YAML configuration file and sends a prompt to ChatGPT."""

    # Send the request to OpenAI
    response = client.chat.completions.create(model=config.get("model", "gpt-4"),
    messages=config.get("prompt", ""),
    max_tokens=config.get("max_tokens", 1000),
    temperature=config.get("temperature", 1.0))

    return response.choices[0].message.content

def extract_and_append_json(data_string, file_path):
    """
    Extracts JSON data from a string and appends it to a file.
    
    Args:
        data_string (str): A string containing JSON data.
        file_path (str): Path to the file where the JSON data will be appended.
    """
    try:
        # Parse the string to extract JSON data
        data = json.loads(data_string)
        
        # Open the file in append mode
        with open(file_path, 'a') as file:
            # Append the data to the file as a JSON string
            json.dump(data, file)
            file.write("\n")  # Ensure each entry is on a new line
            
    
    except json.JSONDecodeError:
        print("Error: Invalid JSON data in the string")
    except Exception as e:
        print(f"An error occurred: {e}")

