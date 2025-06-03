import json

input_file = 'DEF-JobAt.json'
output_file = 'DEF-Smartlions.json'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Pas webaddress aan
for item in data:
    if "webaddress" in item and isinstance(item["webaddress"], str):
        item["webaddress"] = item["webaddress"].replace("utm_source=jobat", "utm_source=smartlions")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
