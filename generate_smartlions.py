import json
import re
from datetime import datetime

input_file = 'DEF-JobAt.json'
output_file = 'DEF-Smartlions.json'

UITGESLOTEN_CATEGORIEEN = [
    "500", "501", "502", "503",
    "740", "741", "742", "743", "744", "745",
    "720", "721", "722", "723", "724", "725"
]

def strip_cdata(text):
    if isinstance(text, str):
        return re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    return text

def format_datum_iso_naar_slash(iso_date):
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return iso_date

def build_session_id(internal_id, iso_date, description):
    clean_desc = description.lower().replace(" ", "-").replace("ë", "e").replace("é", "e")
    return f"{internal_id}-{iso_date}-{clean_desc}"

def genereer_sessions(item):
    locatieblok = item.get("location_and_date", [])
    if not locatieblok or not isinstance(locatieblok, list):
        return []

    locatie = locatieblok[0]
    internal_id = item.get("internal_id", "zonder-id")
    location_name = locatie.get("location_name", "").lower()
    is_online = "online" in location_name

    def locatie_veld(veld):
        return "" if is_online else locatie.get(veld, "")

    def volledig_adres(adres):
        return "Online" if is_online else adres.strip() if adres else ""

    adres = volledig_adres(locatie.get("location_address", ""))

    def sessie(iso_date, beschrijving):
        return {
            "date": format_datum_iso_naar_slash(iso_date),
            "sessionDescription": beschrijving,
            "sessionId": build_session_id(internal_id, iso_date, beschrijving),
            "locationName": locatie.get("location_name", ""),
            "address": adres,
            "zipCode": locatie_veld("location_zip"),
            "city": "" if is_online else "Antwerpen",
            "startTime": "00:00",
            "endTime": "00:00"
        }

    sessions = []
    if locatie.get("date_start"):
        sessions.append(sessie(locatie["date_start"], "Startdatum"))
    if locatie.get("date_end"):
        sessions.append(sessie(locatie["date_end"], "Einddatum"))

    return sessions

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

gefilterde_items = []

for item in data:
    categorie = str(item.get("job_function_category", "")).strip()
    if categorie not in UITGESLOTEN_CATEGORIEEN:
        # Strip CDATA
        item["description"] = strip_cdata(item.get("description"))
        item["description_program"] = strip_cdata(item.get("description_program"))
        item["description_extrainfo"] = strip_cdata(item.get("description_extrainfo"))

        # Pas UTM aan
        if "webaddress" in item and isinstance(item["webaddress"], str):
            item["webaddress"] = item["webaddress"].replace("utm_source=jobat", "utm_source=smartlions")

        internal_id = item.get("internal_id", "zonder-id")

        # Sessions toevoegen of aanpassen
        if "sessions" not in item or not isinstance(item["sessions"], list):
            item["sessions"] = genereer_sessions(item)
        else:
            for s in item["sessions"]:
                # Datumformaat
                if "date" in s:
                    s["date"] = format_datum_iso_naar_slash(s["date"])
                # Combineer street + number → address
                if "street" in s and "number" in s:
                    s["address"] = f"{s['street']} {s['number']}".strip()
                    s.pop("street", None)
                    s.pop("number", None)
                # Zet address op 'Online' als city leeg is én address leeg
                if s.get("city", "").strip() == "" and not s.get("address"):
                    s["address"] = "Online"
                # Voeg startTime en endTime toe als die ontbreken
                s["startTime"] = s.get("startTime", "00:00")
                s["endTime"] = s.get("endTime", "00:00")
                # Voeg sessionId toe
                if "sessionId" not in s:
                    raw_date = s.get("date")
                    iso_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d") if "/" in raw_date else raw_date
                    s["sessionId"] = build_session_id(internal_id, iso_date, s.get("sessionDescription", "sessie"))

        gefilterde_items.append(item)

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(gefilterde_items, f, indent=2, ensure_ascii=False)
