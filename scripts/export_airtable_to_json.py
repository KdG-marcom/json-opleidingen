#!/usr/bin/env python3
import os
import json
import sys
import time
from typing import Any, Dict, List, Optional
import urllib.parse
import urllib.request

AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]
BASE_ID = os.environ["AIRTABLE_BASE_ID"]
TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

# Optional: export only a specific view (recommended)
AIRTABLE_VIEW = os.getenv("AIRTABLE_VIEW", "").strip()  # e.g. "Published"

# Output paths
OUT_JSON = os.getenv("OUT_JSON", "data/BIJSCHOLING-kortlopend.json")
OUT_REPORT_UNMAPPED = os.getenv("OUT_REPORT_UNMAPPED", "reports/unmapped_fields.json")

# Which Airtable field contains the title? (adjust once)
TITLE_FIELD = os.getenv("TITLE_FIELD", "TITLE")  # e.g. "TITLE" or "title"

API_ROOT = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

def airtable_get(url: str) -> Dict[str, Any]:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {AIRTABLE_TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def fetch_all_records() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    offset: Optional[str] = None

    while True:
        params = {"pageSize": "100"}
        if AIRTABLE_VIEW:
            params["view"] = AIRTABLE_VIEW
        if offset:
            params["offset"] = offset

        url = API_ROOT + "?" + urllib.parse.urlencode(params)
        payload = airtable_get(url)

        batch = payload.get("records", [])
        records.extend(batch)

        offset = payload.get("offset")
        if not offset:
            break

        # be nice to the API
        time.sleep(0.15)

    return records

def transform(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform Airtable record -> JSON object.

    Baseline: we export all Airtable 'fields' as-is, plus record id.
    Jij kan hier later exact naar Jobat-schema mappen.
    """
    out: List[Dict[str, Any]] = []
    unmapped: List[Dict[str, Any]] = []

    for r in records:
        rid = r.get("id")
        fields = r.get("fields", {}) or {}

        title = fields.get(TITLE_FIELD)
        if not title:
            unmapped.append({"record_id": rid, "missing": TITLE_FIELD, "fields_present": list(fields.keys())})

        item = {"airtable_record_id": rid, **fields}
        out.append(item)

    # schrijf rapportje voor ontbrekende kernvelden
    if unmapped:
        os.makedirs(os.path.dirname(OUT_REPORT_UNMAPPED), exist_ok=True)
        with open(OUT_REPORT_UNMAPPED, "w", encoding="utf-8") as f:
            json.dump(unmapped, f, ensure_ascii=False, indent=2)

    return out

def main() -> int:
    records = fetch_all_records()
    data = transform(records)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(data)} records -> {OUT_JSON}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
