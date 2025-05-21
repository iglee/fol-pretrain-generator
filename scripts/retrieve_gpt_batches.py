from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

N_files = 277*6

total_batches = []
batches = [x.id for x in client.batches.list(limit=100).data]

while batches:
    total_batches += batches
    batches = [x.id for x in client.batches.list(after=batches[-1], limit=100).data]

def retrieve_batches_and_save(batch_ids, filepath, tag="predicates_{}.jsonl", starting_idx = 0):

    files = [client.batches.retrieve(x).output_file_id for x in batch_ids]
    output_files = [tag.format(i + starting_idx) for i, x in enumerate(batch_ids)]

    for i, x in enumerate(files):
        try:
            if x:
                content = client.files.content(x)

                with open(os.path.join(filepath, output_files[i],), "w",) as f:
                    f.write(content.text)
        except:
            pass

path = "data/predicate_prompted_complex"

os.makedirs(path, exist_ok=True)
total_batches = total_batches[:N_files]

print(total_batches[0], total_batches[-1])

retrieve_batches_and_save(
    total_batches[::-1],
    path,
    starting_idx = 708
)
