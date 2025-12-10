"""
fetch_data.py

Script to fetch data from the NPS API and populate the SQLite database.

We:
- Initialize the database/tables
- Fetch data for EXACTLY 10 selected project parks (by parkCode)
- Insert parks, visitor centers, and events tied to those parks

Events now use start_date and end_date instead of a single event_date.
"""

from __future__ import annotations

import os
from datetime import datetime, date
from typing import List, Dict, Any

import requests
from sqlmodel import Session, delete

from .database import engine, init_db
from .models import Park, VisitorCenter, Event

NPS_BASE_URL = "https://developer.nps.gov/api/v1"
API_KEY = os.getenv("NPS_API_KEY")

# Our 10 project park codes (exactly 10)
PROJECT_PARK_CODES: List[str] = [
    "grca",  # Grand Canyon
    "yose",  # Yosemite
    "zion",  # Zion
    "yell",  # Yellowstone
    "seki",  # Sequoia & Kings Canyon
    "romo",  # Rocky Mountain
    "arch",  # Arches
    "brca",  # Bryce Canyon
    "lavo",  # Lassen Volcanic
    "jotr",  # Joshua Tree
]

# ---------- Helper: NPS requests ----------

def nps_get(endpoint: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Call the NPS API and return the 'data' list."""
    if not API_KEY:
        raise RuntimeError(
            "NPS_API_KEY not set. Make sure you created a .env file and exported it."
        )

    url = f"{NPS_BASE_URL}/{endpoint}"
    base_params = {"api_key": API_KEY}
    all_params = {**base_params, **params}

    headers = {
        "User-Agent": "IEE305 Term Project (dmartin@student.asu.edu)",
        "Accept": "application/json",
    }

    resp = requests.get(url, params=all_params, headers=headers, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("data", [])

# ---------- Data extraction helpers ----------

def extract_vehicle_entrance_fee(park_data: Dict[str, Any]) -> int:
    """Pick the 'Entrance - Private Vehicle' fee if present, else 0."""
    fees = park_data.get("entranceFees") or []
    for fee in fees:
        title = (fee.get("title") or "").lower()
        cost_str = fee.get("cost")
        if "vehicle" in title and cost_str not in (None, ""):
            try:
                return int(round(float(cost_str)))
            except ValueError:
                continue
    return 0

def extract_state_code(park_data: Dict[str, Any]) -> str:
    """Use the first state code listed (NPS returns comma-separated string)."""
    states = (park_data.get("states") or "").split(",")
    states = [s.strip() for s in states if s.strip()]
    return states[0] if states else ""

def parse_event_date(raw: str | None) -> date | None:
    """Parse NPS event date strings like '2025-03-15' into a date."""
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.date()
        except ValueError:
            continue
    return None

def extract_is_free(event_data: Dict[str, Any]) -> bool:
    """Extract event 'is free' flag from various possible fields."""
    if isinstance(event_data.get("isFree"), bool):
        return bool(event_data["isFree"])
    # Sometimes it may be a string "true"/"false"
    is_free_str = str(event_data.get("isFree") or "").lower()
    if is_free_str in ("true", "yes", "y", "1"):
        return True
    if is_free_str in ("false", "no", "n", "0"):
        return False
    # Fallback: if a numeric fee is present in feeInfo, treat as not free
    fee_info = (event_data.get("feeInfo") or "").strip()
    return fee_info == ""

# ---------- Loaders for each table ----------

def load_parks(session: Session) -> List[str]:
    print("Fetching park details for 10 selected project parks...")
    inserted_codes: List[str] = []

    for code in PROJECT_PARK_CODES:
        parks_data = nps_get("parks", {"parkCode": code, "limit": 1})
        if not parks_data:
            print(f"  WARNING: No park data returned for code '{code}', skipping.")
            continue

        p = parks_data[0]
        park = Park(
            park_code=code,
            name=p.get("fullName") or p.get("name") or code.upper(),
            state_code=extract_state_code(p),
            entrance_fee=extract_vehicle_entrance_fee(p),
            total_activities=len(p.get("activities") or []),
        )
        session.add(park)
        inserted_codes.append(code)
        print(f"  Inserted park {code}: {park.name}")

    print(f"Inserted {len(inserted_codes)} parks.")
    return inserted_codes

def load_visitor_centers(session: Session, park_codes: List[str]) -> None:
    print("Fetching visitor centers for selected parks...")
    inserted = 0

    for code in park_codes:
        centers_data = nps_get("visitorcenters", {"parkCode": code, "limit": 50})
        if not centers_data:
            print(f"  No visitor centers found for {code}.")
            continue

        for c in centers_data:
            vc = VisitorCenter(
                park_code=code,
                center_name=c.get("name") or "Unknown Visitor Center",
            )
            session.add(vc)
            inserted += 1

        print(f"  Inserted {len(centers_data)} visitor centers for {code}.")

    print(f"Inserted {inserted} visitor centers total.")

def load_events(session: Session, park_codes: List[str]) -> None:
    print("Fetching events for selected parks...")
    inserted = 0

    for code in park_codes:
        events_data = nps_get("events", {"parkCode": code, "limit": 50})
        if not events_data:
            print(f"  No events found for {code}.")
            continue

        for e in events_data:
            title = e.get("title")
            if not title:
                continue

            # Prefer datestart, fallback to dateend
            raw_start = e.get("datestart") or e.get("dateend")
            raw_end = e.get("dateend") or raw_start

            start_date = parse_event_date(raw_start)
            end_date = parse_event_date(raw_end) or start_date

            # Require at least a valid start_date
            if not start_date:
                continue

            ev = Event(
                park_code=code,
                event_title=title,
                start_date=start_date,
                end_date=end_date,
                is_free=extract_is_free(e),
            )
            session.add(ev)
            inserted += 1

        print(f"  Inserted events for {code} (count so far: {inserted}).")

    print(f"Inserted {inserted} events total.")

# ---------- Main entrypoint ----------

def main() -> None:
    print("Initializing database and tables...")
    init_db()

    with Session(engine) as session:
        # Clear existing data so we can re-run safely
        print("Clearing existing data (events, visitor centers, parks)...")
        session.exec(delete(Event))
        session.exec(delete(VisitorCenter))
        session.exec(delete(Park))
        session.commit()

        # Load fresh data
        selected_codes = load_parks(session)
        load_visitor_centers(session, selected_codes)
        load_events(session, selected_codes)

        session.commit()
        print("Data loading complete.")

if __name__ == "__main__":
    main()
