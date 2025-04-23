from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

total_batches = []
batches = [x.id for x in client.batches.list(limit=100).data]

while batches:
    total_batches += batches
    batches = [x.id for x in client.batches.list(after=batches[-1], limit=100).data]

def retrieve_batches_and_save(batch_ids, filepath, tag="predicates_{}.jsonl"):

    files = [client.batches.retrieve(x).output_file_id for x in batch_ids]
    output_files = [tag.format(i) for i, x in enumerate(batch_ids)]

    for i, x in enumerate(files):

        if x:
            content = client.files.content(x)

            with open(os.path.join(filepath, output_files[i],), "w",) as f:
                f.write(content.text)


path = "data/predicate_prompted"

os.makedirs(path, exist_ok=True)
N_files = 177*2
total_batches = total_batches[:N_files]

retrieve_batches_and_save(
    total_batches[::-1],
    path,
)
