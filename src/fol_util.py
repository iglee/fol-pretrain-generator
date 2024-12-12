import random
import json
import pickle


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


## write rules to json
# with open("data/unique_fol_rules.pkl", "rb") as f:
#    rules = pickle.load(f)

# write_rules_dataset(rules, "data/fol_rules.json")
