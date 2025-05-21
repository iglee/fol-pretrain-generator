import json
import os

# Constants
TOKEN_TARGET = 310_000_000  # 1.88 billion tokens
FILE_TEMPLATE = "segment_{}.jsonl"

def count_files_to_token_target(directory):
    total_tokens = 0
    file_count = 0
    i = 0

    while True:
        file_path = os.path.join(directory, FILE_TEMPLATE.format(i))
        if not os.path.exists(file_path):
            print(f"File {file_path} not found. Stopping.")
            break

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                total_tokens += data.get("num_tokens", 0)
                if total_tokens >= TOKEN_TARGET:
                    print(f"Reached target in {file_count + 1} files.")
                    return file_count + 1

        file_count += 1
        i += 1

    print("Target not reached.")
    return file_count


def count_tokens(directory, num_files):
    total_tokens = 0
    file_count = 0
    i = 0

    while True:
        file_path = os.path.join(directory, FILE_TEMPLATE.format(i))

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                total_tokens += data.get("num_tokens", 0)

        if i == num_files -1:
            return total_tokens
                

        file_count += 1
        i += 1


# Example usage
directory = "/mnt/isabelle-pretrain-data/fol-pretrain/train_repeated_low_complexity"
count = count_files_to_token_target(directory)
print(f"Files needed: {count}")
token_count = count_tokens(directory, count)
print(f"Token count: {token_count}")