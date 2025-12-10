from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import SQLModel, Session, select
from sqlalchemy import func

from .database import engine, init_db
from .models import Park, VisitorCenter, Event

# -----------------------------------------------------------------------------
# FastAPI app
# -----------------------------------------------------------------------------

app = FastAPI(
    title="IEE 305 – NPS Visitor Information & Event Planning",
    description="Decision support tool using NPS data (parks, visitor centers, events).",
    version="1.0.0",
)

# -----------------------------------------------------------------------------
# Dependency: DB session
# -----------------------------------------------------------------------------

def get_session() -> Session:
    with Session(engine) as session:
        yield session

# -----------------------------------------------------------------------------
# Startup – ensure tables exist
# -----------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    init_db()

# -----------------------------------------------------------------------------
# DTOs for stats endpoints
# -----------------------------------------------------------------------------

class EventCountPerPark(SQLModel):
    park_code: str
    name: str
    event_count: int

class VisitorCenterCountPerPark(SQLModel):
    park_code: str
    name: str
    center_count: int

# -----------------------------------------------------------------------------
# Root endpoint (simple health / info)
# -----------------------------------------------------------------------------

@app.get("/")
def read_root() -> dict:
    return {
        "project": "IEE 305 Term Project",
        "description": "NPS parks, visitor centers, and events (10 selected parks).",
        "status": "backend running",
    }

# =============================================================================
# 1) PARKS – LIST (covers Q1 via parameters)
#    Q1: Parks in CA with entrance fee < 35
#        -> GET /parks?state_code=CA&max_fee=35
# =============================================================================

@app.get("/parks", response_model=List[Park])
def list_parks(
    state_code: Optional[str] = Query(None, description="Filter by state code, e.g. 'CA'"),
    max_fee: Optional[int] = Query(
        None,
        description="Maximum entrance fee (e.g. 35 for Q1: CA parks with fee < 35)",
    ),
    session: Session = Depends(get_session),
) -> List[Park]:
    stmt = select(Park)

    if state_code:
        # Make state-code filter case-insensitive
        code = state_code.upper()
        stmt = stmt.where(func.upper(Park.state_code) == code)

    if max_fee is not None:
        stmt = stmt.where(Park.entrance_fee < max_fee)

    stmt = stmt.order_by(Park.park_code)
    parks = session.exec(stmt).all()
    return parks

# =============================================================================
# 2) PARKS – DETAIL
# =============================================================================

@app.get("/parks/{park_code}", response_model=Park)
def get_park(park_code: str, session: Session = Depends(get_session)) -> Park:
    # Normalize input and compare case-insensitively
    code = park_code.upper()
    park = session.exec(
        select(Park).where(func.upper(Park.park_code) == code)
    ).first()
    if not park:
        raise HTTPException(status_code=404, detail="Park not found")
    return park

# =============================================================================
# 3) VISITOR CENTERS – LIST (base for Q5/Q6 via stats endpoint)
# =============================================================================

@app.get("/visitor-centers", response_model=List[VisitorCenter])
def list_visitor_centers(
    park_code: Optional[str] = Query(None, description="Filter by park_code"),
    session: Session = Depends(get_session),
) -> List[VisitorCenter]:
    stmt = select(VisitorCenter)
    if park_code:
        # Case-insensitive filter on park_code
        code = park_code.upper()
        stmt = stmt.where(func.upper(VisitorCenter.park_code) == code)
    stmt = stmt.order_by(VisitorCenter.center_name)
    centers = session.exec(stmt).all()
    return centers

# =============================================================================
# 4) EVENTS – LIST (covers Q4, Q7, Q10 via parameters)
#
#   Q4: Free events in a given park
#       -> GET /events?park_code=ZION&free_only=true
#   Q7: All events for a park ordered by date
#       -> GET /events?park_code=ZION
#   Q10: Events in a date range
#       -> GET /events?start=2025-06-01&end=2025-06-30
# =============================================================================

@app.get("/events", response_model=List[Event])
def list_events(
    park_code: Optional[str] = Query(None, description="Filter by park_code"),
    free_only: Optional[bool] = Query(
        None, description="If true, only free events (is_free = 1)"
    ),
    start: Optional[date] = Query(
        None, description="Start of date range (inclusive, YYYY-MM-DD)"
    ),
    end: Optional[date] = Query(
        None, description="End of date range (inclusive, YYYY-MM-DD)"
    ),
    session: Session = Depends(get_session),
) -> List[Event]:
    stmt = select(Event)

    if park_code:
        # Case-insensitive filter on park_code
        code = park_code.upper()
        stmt = stmt.where(func.upper(Event.park_code) == code)

    if free_only is True:
        stmt = stmt.where(Event.is_free == True)  # noqa: E712
    if start is not None:
        stmt = stmt.where(Event.start_date >= start)
    if end is not None:
        stmt = stmt.where(Event.start_date <= end)

    stmt = stmt.order_by(Event.start_date, Event.event_title)
    events = session.exec(stmt).all()
    return events

# =============================================================================
# 5) STATS – EVENTS PER PARK
#
#   Q2: Event count per park (by year)
#       -> /stats/events-per-park?year=2025
#   Q3: Parks with more events than the average (that year)
#       -> /stats/events-per-park?year=2025&above_avg=true
#   Q8: Top N parks by events
#       -> /stats/events-per-park?year=2025&top_n=5
#   Q9: Parks with zero events in a year
#       -> /stats/events-per-park?year=2025&include_zero_only=true
# =============================================================================

@app.get("/stats/events-per-park", response_model=List[EventCountPerPark])
def stats_events_per_park(
    year: int = Query(..., description="4-digit year, e.g. 2025"),
    above_avg: bool = Query(
        False, description="If true, return only parks with event_count > average"
    ),
    top_n: Optional[int] = Query(
        None, description="If set (and not using above_avg/include_zero_only), return top N parks"
    ),
    include_zero_only: bool = Query(
        False, description="If true, return only parks with 0 events in that year"
    ),
    session: Session = Depends(get_session),
) -> List[EventCountPerPark]:
    year_str = str(year)

    # Base query: count events per park for the given year (LEFT JOIN to include 0)
    stmt = (
        select(
            Park.park_code,
            Park.name,
            func.count(Event.id).label("event_count"),
        )
        .select_from(Park)
        .join(
            Event,
            (Event.park_code == Park.park_code)
            & (func.strftime("%Y", Event.start_date) == year_str),
            isouter=True,
        )
        .group_by(Park.park_code, Park.name)
    )

    rows = session.exec(stmt).all()
    base: List[EventCountPerPark] = [
        EventCountPerPark(
            park_code=r.park_code,
            name=r.name,
            event_count=r.event_count or 0,
        )
        for r in rows
    ]

    # Apply Python-side filters for the different queries
    if above_avg:
        if not base:
            return []
        avg = sum(p.event_count for p in base) / len(base)
        base = [p for p in base if p.event_count > avg]

    if include_zero_only:
        base = [p for p in base if p.event_count == 0]

    # Sort by count desc, then name
    base.sort(key=lambda p: (-p.event_count, p.name))

    if top_n is not None and not (above_avg or include_zero_only):
        base = base[:top_n]

    return base

# =============================================================================
# 6) STATS – VISITOR CENTERS PER PARK
#
#   Q5: Visitor center count per park
#       -> /stats/visitor-centers-per-park
#   Q6: Parks with at least N visitor centers
#       -> /stats/visitor-centers-per-park?min_centers=2
# =============================================================================

@app.get(
    "/stats/visitor-centers-per-park",
    response_model=List[VisitorCenterCountPerPark],
)
def stats_visitor_centers_per_park(
    min_centers: Optional[int] = Query(
        None,
        description="If set, only return parks with at least this many visitor centers",
    ),
    session: Session = Depends(get_session),
) -> List[VisitorCenterCountPerPark]:
    stmt = (
        select(
            Park.park_code,
            Park.name,
            func.count(VisitorCenter.id).label("center_count"),
        )
        .select_from(Park)
        .join(
            VisitorCenter,
            VisitorCenter.park_code == Park.park_code,
            isouter=True,
        )
        .group_by(Park.park_code, Park.name)
    )

    rows = session.exec(stmt).all()
    base: List[VisitorCenterCountPerPark] = [
        VisitorCenterCountPerPark(
            park_code=r.park_code,
            name=r.name,
            center_count=r.center_count or 0,
        )
        for r in rows
    ]

    if min_centers is not None:
        base = [p for p in base if p.center_count >= min_centers]

    base.sort(key=lambda p: (-p.center_count, p.name))
    return base
