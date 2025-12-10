from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class Park(SQLModel, table=True):
    __tablename__ = "parks"

    id: Optional[int] = Field(default=None, primary_key=True)
    park_code: str = Field(index=True, nullable=False, unique=True)
    name: str
    state_code: str  # 'AZ', 'UT', 'NV', or 'CA'
    entrance_fee: int = Field(
        default=0,
        description="Entrance fee in dollars (private vehicle)",
        ge=0,
    )
    total_activities: int = Field(default=0, ge=0)


class VisitorCenter(SQLModel, table=True):
    __tablename__ = "visitor_centers"

    id: Optional[int] = Field(default=None, primary_key=True)
    park_code: str = Field(index=True, foreign_key="parks.park_code")
    center_name: str


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    park_code: str = Field(index=True, foreign_key="parks.park_code")
    event_title: str
    start_date: date
    end_date: Optional[date] = None
    is_free: bool = Field(default=True)

