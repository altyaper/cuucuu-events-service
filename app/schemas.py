from __future__ import annotations

from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel


class ArticleRequest(BaseModel):
    title: str = ""
    body: str = ""
    date: Optional[str] = None


class EventResponse(BaseModel):
    is_event: bool
    confidence: float
    event_name: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    venue: Optional[str] = None
    dates: List[date] = []
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    admission: Optional[str] = None
    organizer: Optional[str] = None
    event_type: Optional[str] = None
    evidence: Optional[str] = None
    warnings: List[str] = []
