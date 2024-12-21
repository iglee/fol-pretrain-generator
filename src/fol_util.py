import random
import json
import pickle
import re
import os

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

def find_unique_variables(expression, replacements):
    """
    Finds all unique variable names with Unicode subscripts in the order of their first appearance
    and creates a mapping to the provided replacements.

    Args:
        expression (str): The input string containing variables (e.g., p₀, p₁, ...).
        replacements (list): A list of replacement strings (e.g., ['α', 'β', ...]).

    Returns:
        list: A list of unique variable names in the order they appear.
        dict: A dictionary mapping variables to their replacements.
    """
    # Match variable names like p₀, p₁, ...
    pattern = r"p[\u2080-\u2089]+"
    seen = set()
    variables = []
    for match in re.finditer(pattern, expression):
        var = match.group(0)
        if var not in seen:
            variables.append(var)
            seen.add(var)

    # Create a mapping of variables to replacements
    variable_map = {var: replacements[i] for i, var in enumerate(variables) if i < len(replacements)}
    
    return variables, variable_map

def replace_variables(expression, variable_map):
    """
    Replaces the given variables in the expression based on the variable map.

    Args:
        expression (str): The input string containing variables.
        variable_map (dict): A dictionary mapping variable names to replacements.

    Returns:
        str: The modified expression with replaced variable names.
    """
    def replacer(match):
        return variable_map.get(match.group(0), match.group(0))

    # Match variable names like p₀, p₁, ...
    pattern = r"p[\u2080-\u2089]+"
    return re.sub(pattern, replacer, expression)