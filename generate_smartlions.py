import json
import re

input_file = 'DEF-JobAt.json'
output_file = 'DEF-Smartlions.json'

UITGESLOTEN_CATEGORIEEN = [
    "500", "501", "502", "503",         # Gezondheidszorg
    "740", "741", "742", "743", "744", "745",  # Onderwijs
    "720", "721", "722", "723", "724", "725"   # Sociaal werk
]

def strip_cdata(text):
    if isinstance(text, str):
        return re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    return text

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

gefilterde_items = []

for item in data:
    categorie = str(item.get("job_function_category", "")).strip()
    if categorie not in UITGESLOTEN_CATEGORIEEN:
        # pas CDATA-strip toe
        item["description"] = strip_cdata(item.get("description"))
        item["description_program"] = strip_cdata(item.get("description_program"))
        item["description_extrainfo"] = strip_cdata(item.get("description_extrainfo"))

        # pas webaddress aan
        if "webaddress" in item and isinstance(item["webaddress"], str):
            item["webaddress"] = item["webaddress"].replace("utm_source=jobat", "utm_source=smartlions")

        gefilterde_items.append(item)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(gefilterde_items, f, indent=2, ensure_ascii=False)
