import os
import json

input_folder = 'per-opleidingstype'
output_file = 'DEF-test.json'

merged_data = {}

for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        filepath = os.path.join(input_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                key = filename.replace('.json', '')
                merged_data[key] = content
            except json.JSONDecodeError as e:
                print(f"Fout in {filename}: {e}")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)
