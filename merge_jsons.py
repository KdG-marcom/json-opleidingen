import os
import json

input_folder = 'EDIT-opleidingen'
output_file = 'DEF-JobAt.json'

merged_data = []

# Mapping van foutieve naar correcte values
duration_type_corrections = {
    "year": ("years", None),
    "semester": ("years", 0.5),
    "dagen": ("days", None),
    "lesweken": ("weeks", None),
    "avonden": ("days", None),
    "weken": ("weeks", None),
    "academiejaar": ("years", None),
    "weken (per module)": ("weeks", None),
    "semester (sommige een jaar)": ("years", 0.5),
    "uur (5 donderdagen)": ("hours", None),
    "maanden (voltijds)": ("months", None),
    "jaar": ("years", None),
    "semester (8 lessen)": ("years", 0.5),
    "semester (per module)": ("years", 0.5)
}

for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        filepath = os.path.join(input_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                items = content if isinstance(content, list) else [content]

                for item in items:
                    # Zorg dat location_and_date een lijst is
                    loc = item.get("location_and_date")
                    if isinstance(loc, dict):
                        item["location_and_date"] = [loc]

                    # Corrigeer duration_type indien nodig
                    original_type = item.get("duration_type", "").strip().lower()
                    if original_type in duration_type_corrections:
                        corrected_type, corrected_length = duration_type_corrections[original_type]
                        item["duration_type"] = corrected_type
                        if corrected_length is not None:
                            item["duration_length"] = corrected_length

                    merged_data.append(item)

            except json.JSONDecodeError as e:
                print(f"Fout in {filename}: {e}")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)

print(f"Ingelezen bestand: {filename}, items: {len(items)}")

merged_data.append({"internal_id": "debug-test-entry", "title": "TEST – zichtbaar?"})
