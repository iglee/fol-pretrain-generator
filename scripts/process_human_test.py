from src.fol_util import read_jsonl_to_list, write_list_to_jsonl
import re
import tiktoken

# Load the GPT-2 tokenizer
tokenizer = tiktoken.get_encoding("gpt2")


file_pth = "/mnt/isabelle-pretrain-data/fol-pretrain/fol-test-total.json"
data = read_jsonl_to_list(file_pth)

out_file_pth = "/mnt/isabelle-pretrain-data/dataset_v2/fol-pretrain/fol_test_human.jsonl"

UNIQUE_ID = 0

pattern = r"[∀∃][a-zA-Z]+"

new_data = []

for x in data:
    string = re.sub(pattern, "", x["raw_data"])
    string = "<|endoftext|>" + string + " <|endoftext|>"
    string = string.replace("  ,   ,  ", ",")
    string = string.replace("  ", " ")
    string = string.replace(" , ", ", ")
    string = string.replace("⟹", "→")
    string = string.replace("->", "→")
    string = string.replace("⊢", "→")
    string = string.replace(",,", ",")

    datum = {
        "id" : UNIQUE_ID,
        "gpt2_tokens" : tokenizer.encode(string, allowed_special={"<|endoftext|>"}),
        "raw_data" : string,
        "fol_rules" : [x["fol_type"]],
        "datum_ids" : []
    }
    datum["num_tokens"] = len(datum["gpt2_tokens"])
    new_data.append(datum)
    UNIQUE_ID += 1

write_list_to_jsonl(new_data, out_file_pth)