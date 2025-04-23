import random
import json
import pickle
import re
import os

def read_pkl_fie(file_path):
    with open(file_path, "rb") as file:
        data = pickle.load(file)
    return data

def read_json_file(file_path):
    """Reads a JSON file and returns its content as a Python dictionary."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file at {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

def select_random_element(lst):
    """
    Parameters:
        lst (list): The list to select an element from.

    Returns:
        element: A randomly selected element from the list.
    """
    if not lst:
        raise ValueError("The list is empty. Cannot select a random element.")
    return random.choice(lst)


# Function to process each data point (replace with actual processing logic)
def data_process(x):
    data = {}
    data["data"] = x[0].replace("\n", "")
    data["total_complexity"] = x[1]
    for k, v in x[2].items():
        data[k] = v
    data["exprs"] = [y.replace("\n", "") for y in data["exprs"]]
    return data


def write_rules_dataset(data_list, output_file):
    with open(output_file, "w") as f:
        for data_point in data_list:
            # Process the data point
            processed_data = data_process(data_point)

            # Write the processed data to the JSONL file
            f.write(json.dumps(processed_data) + "\n")

def write_list_to_json(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_list_to_jsonl(data_list, file_path):
    """
    Writes a list of JSON objects to a JSONL file.

    Args:
        data_list (list): A list of dictionaries to write to the JSONL file.
        file_path (str): Path to the JSONL file.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    try:
        with open(file_path, 'w') as file:
            for obj in data_list:
                json_line = json.dumps(obj)  # Convert the dictionary to a JSON string
                file.write(json_line + '\n')  # Write each JSON object as a line
    except Exception as e:
        print(f"Error writing to file: {e}")

def read_jsonl_to_list(file_path):
    """
    Reads a JSONL file and returns its contents as a list of dictionaries.
    """
    data_list = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                data_list.append(json.loads(line))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading the file: {e}")
    return data_list


def test_train_split_list(data, fraction=0.2):
    # Shuffle a copy of the original list
    data_copy = data[:]
    random.shuffle(data_copy)
    
    # Compute split index
    split_idx = int(len(data_copy) * fraction)
    
    return data_copy[:split_idx], data_copy[split_idx:]


## FOL specific
def standardize_variables(expr):
    """
    Rename variables in a logical expression to α, β, γ, ... in order of appearance.
    
    Args:
        expr (str): A string representing the logical expression.
    
    Returns:
        str: A new expression with variables renamed in order of appearance.
    """
    greek_vars = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 
                  'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
    
    # Find all Greek variables (assumes variables are single Greek letters in α-ω range)
    vars_found = re.findall(r"[α-ω]", expr)
    
    # Preserve order of first appearance
    seen = []
    for var in vars_found:
        if var not in seen:
            seen.append(var)
    
    # Map each unique variable to the next Greek letter
    rename_map = {var: greek_vars[i] for i, var in enumerate(seen)}
    
    # Replace variables in expression
    renamed_expr = ''.join(rename_map.get(ch, ch) for ch in expr)
    
    return renamed_expr