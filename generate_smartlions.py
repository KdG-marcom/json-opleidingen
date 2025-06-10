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

def genereer_sessions(item):
    locatieblok = item.get("location_and_date", [])
    if not locatieblok or not isinstance(locatieblok, list):
        return []

    locatie = locatieblok[0]

    sessions = []
    if locatie.get("date_start"):
        sessions.append({
            "date": locatie["date_start"],
            "sessionDescription": "Startdatum",
            "locationName": locatie.get("location_name", ""),
            "street": locatie.get("location_address", "").rsplit(' ', 1)[0],  # straat zonder huisnummer
            "number": locatie.get("location_address", "").rsplit(' ', 1)[-1],  # huisnummer
            "zipCode": locatie.get("location_zip", ""),
            "city": locatie.get("location_name", "").split(",")[-1].strip() if "," in locatie.get("location_name", "") else "Antwerpen"
        })
    if locatie.get("date_end"):
        sessions.append({
            "date": locatie["date_end"],
            "sessionDescription": "Einddatum",
            "locationName": locatie.get("location_name", ""),
            "street": locatie.get("location_address", "").rsplit(' ', 1)[0],
            "number": locatie.get("location_address", "").rsplit(' ', 1)[-1],
            "zipCode": locatie.get("location_zip", ""),
            "city": locatie.get("location_name", "").split(",")[-1].strip() if "," in locatie.get("location_name", "") else "Antwerpen"
        })
    return sessions

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

gefilterde_items = []

for item in data:
    categorie = str(item.get("job_function_category", "")).strip()
    if categorie not in UITGESLOTEN_CATEGORIEEN:

        # Verwijder CDATA
        item["description"] = strip_cdata(item.get("description"))
        item["description_program"] = strip_cdata(item.get("description_program"))
        item["description_extrainfo"] = strip_cdata(item.get("description_extrainfo"))

        # Pas UTM-tag aan
        if "webaddress" in item and isinstance(item["webaddress"], str):
            item["webaddress"] = item["webaddress"].replace("utm_source=jobat", "utm_source=smartlions")

        # Genereer sessions indien afwezig
        if "sessions" not in item or not isinstance(item["sessions"], list):
            item["sessions"] = genereer_sessions(item)

        gefilterde_items.append(item)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(gefilterde_items, f, indent=2, ensure_ascii=False)
