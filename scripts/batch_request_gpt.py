from openai import OpenAI
import time
import glob
import os

client = OpenAI()

files = glob.glob("data/batched_prompts_test/*")
preamble = "test_"

for file in files:
    request_type = os.path.basename(file)

    batch_input_file = client.files.create(
        file=open(
            file,
            "rb",
        ),
        purpose="batch",
    )
    
    file_name = os.path.basename(file)

    batch_input_file_id = batch_input_file.id
    
    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": preamble + file_name},
    )
    time.sleep(0.05)
    