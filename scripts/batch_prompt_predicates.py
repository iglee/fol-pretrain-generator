import os
import re
import random
from src.fol_util import read_file_into_list
from src.gpt_util import process_prompt, batch_prompt_items, save_batch_list_to_jsonl, start_batch_jobs_from_dir

directory = '/home/isabelle/fol-pretrain-generator/rules/predicates' 
# regular
prompt = "Generate 10 sets of predicates about {}. e.g. {}, {}, {}. Make sure to generate 4 predicates per set.\nSimply list the data and nothing else. Please format it as a jsonl, with {{\"predicates\": [PREDICATES], \"topic\": [TOPIC]}}"
# semantically complex:
#prompt = "Generate 10 sets of predicates about {}. e.g. {}, {}, {}. Make sure to generate 4 predicates per set.\nSimply list the data and nothing else. Generate semantically complex predicates, with complex/composite words. Please format it as a jsonl, with {{\"predicates\": [PREDICATES], \"topic\": [TOPIC]}}"
model = "gpt-4o"


n_repeat_triplet = 6
n_repeat_singlet = 10000
i = 0

def separate_predicates(input_string):
    return re.findall(r'\b\w+\s*\([^)]*\)', input_string)

triplets = {}
singles = {}
fundamentals = ["Is(x)", "Feels(x)", "Exists(x)", "Does(x)", "Stands(x)", "There(x)", "Are(x)", "Do(x)",\
                "Has(x)", "Have(x)", "Comes(x)", "Come(x)", "Goes(x)", "Gone(x)", "Moves(x)", "Becomes(x)", \
                "Happens(x)", "Changes(x)", "Lives(x)", "Alive(x)","Hard(x)", "Soft(x)",\
                "Remains(x)", "Remembers(x)", "Looks(x)", "Sounds(x)", "Belongs(x)", "Matters(x)", "Begins(x)", "Works(x)"]


for filename in os.listdir(directory):
    pth = os.path.join(directory, filename)
    k = filename.split("_")[0]
    v = read_file_into_list(pth)
    if "triplet" in filename:
        triplets[k] = [separate_predicates(x) for x in v if x and (("True" not in x) or ("False" not in x))]
        triplets[k] = [x for x in triplets[k] if len(x) == 3]
    else:
        singles[k] = [x for x in v if x and (("True" not in x) or ("False" not in x))]


batches = []

for k,v in triplets.items():
    topic = k
    for _ in range(n_repeat_triplet):
        for predicates in v:
            message = process_prompt(prompt.format(topic, *predicates))
            batch_item = batch_prompt_items(message)
            batch_item['custom_id'] = f"predicates_{i}"
            i += 1
            batches.append(batch_item)


for k,v in singles.items():
    topic = k
    for _ in range(n_repeat_singlet):
        predicates = random.sample(v + fundamentals, 3)[:]
        message = process_prompt(prompt.format(topic, *predicates))
        batch_item = batch_prompt_items(message)
        batch_item['custom_id'] = f"predicates_{i}"
        i += 1
        batches.append(batch_item)
        
        
save_batch_list_to_jsonl(batches, chunk_size=1000, base_filename="batch", base_dir="data/batches/")
start_batch_jobs_from_dir("data/batches/", project_name="fol_pretrain_predicates", run_date="2025-04-27")