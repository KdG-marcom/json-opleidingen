import os
import json

input_folder = 'EDIT-opleidingen'
output_file = 'DEF-JobAt.json'

merged_data = []

# Optioneel: uitsluiten op bepaalde job_function_category
UITGESLOTEN_CATEGORIEËN = []

for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        filepath = os.path.join(input_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                items = content if isinstance(content, list) else [content]
                for item in items:
                    if str(item.get("job_function_category")) not in UITGESLOTEN_CATEGORIEËN:
                        merged_data.append(item)
            except json.JSONDecodeError as e:
                print(f"Fout in {filename}: {e}")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)
