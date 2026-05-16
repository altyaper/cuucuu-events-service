from datetime import date, time

from app.pipeline import process_article
from tests.conftest import (
    CONCERT_ARTICLE,
    CRIME_ARTICLE,
    EVENT_WITH_DATE_RANGE,
    GOVERNMENT_ANNOUNCEMENT,
    PAST_EVENT_ARTICLE,
    SAMPLE_EVENT_ARTICLE,
)


def test_pipeline_sample_event():
    result = process_article(SAMPLE_EVENT_ARTICLE)
    assert result.is_event is True
    assert result.confidence > 0.8
    assert result.event_type == "expo"
    assert result.city == "Ciudad Juárez"
    assert result.start_date == date(2026, 5, 16)
    assert result.end_date == date(2026, 5, 17)
    assert result.start_time == time(11, 0)
    assert result.end_time == time(20, 0)
    assert result.admission == "libre"
    assert result.organizer is not None
    assert result.venue is not None


def test_pipeline_crime_not_event():
    result = process_article(CRIME_ARTICLE)
    assert result.is_event is False
    assert result.confidence < 0.3
    assert result.event_name is None
    assert result.venue is None


def test_pipeline_government_not_event():
    result = process_article(GOVERNMENT_ANNOUNCEMENT)
    assert result.is_event is False


def test_pipeline_date_range_event():
    result = process_article(EVENT_WITH_DATE_RANGE)
    assert result.is_event is True
    assert result.start_date == date(2026, 6, 20)
    assert result.end_date == date(2026, 6, 25)


def test_pipeline_past_event_not_detected():
    result = process_article(PAST_EVENT_ARTICLE)
    assert result.is_event is False


def test_pipeline_concert():
    result = process_article(CONCERT_ARTICLE)
    assert result.is_event is True
    assert result.event_type == "concierto"
    assert result.confidence > 0.7


def test_pipeline_returns_article_id():
    result = process_article(SAMPLE_EVENT_ARTICLE)
    assert result.article_id == 1


def test_pipeline_warnings_on_missing_fields():
    from app.schemas import ArticleInput

    article = ArticleInput(
        title="Gran Festival",
        body="Se llevará a cabo un gran festival. Invita a la comunidad a asistir.",
    )
    result = process_article(article)
    if result.is_event:
        assert isinstance(result.warnings, list)
