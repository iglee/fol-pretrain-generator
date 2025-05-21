import json

input_file = 'data/processed_predicates_total.jsonl'
output_file = 'data/processed_predicates_total.jsonl.deduped'

seen_predicates = set()

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        data = json.loads(line)
        predicates = json.dumps(data.get('predicates'))  # Serialize to handle lists/dicts properly
        if predicates not in seen_predicates:
            seen_predicates.add(predicates)
            outfile.write(json.dumps(data) + '\n')

print(f"Deduplication complete! Output saved to {output_file}")
