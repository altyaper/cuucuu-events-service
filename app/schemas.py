from datetime import date, datetime, time

from pydantic import BaseModel


class ArticleInput(BaseModel):
    id: int | None = None
    title: str = ""
    content: str = ""
    published_at: datetime | None = None
    source: str | None = None


class EventDetectionResult(BaseModel):
    article_id: int | None = None
    is_event: bool
    confidence: float
    event_name: str | None = None
    city: str | None = None
    venue: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    admission: str | None = None
    organizer: str | None = None
    event_type: str | None = None
    evidence: str | None = None
    warnings: list[str] = []


class DetectBatchRequest(BaseModel):
    articles: list[ArticleInput]
