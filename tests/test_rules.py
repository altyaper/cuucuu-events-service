from app.normalizer import normalize
from app.rules import score_article
from tests.conftest import (
    CONCERT_ARTICLE,
    CRIME_ARTICLE,
    EVENT_WITH_DATE_RANGE,
    GOVERNMENT_ANNOUNCEMENT,
    PAST_EVENT_ARTICLE,
    SAMPLE_EVENT_ARTICLE,
)


def _score(article):
    text = normalize(f"{article.title} {article.content}")
    return score_article(text)


def test_clear_event_high_confidence():
    confidence, breakdown = _score(SAMPLE_EVENT_ARTICLE)
    assert confidence > 0.8
    assert breakdown.invitation > 0
    assert breakdown.venue > 0


def test_crime_article_low_confidence():
    confidence, breakdown = _score(CRIME_ARTICLE)
    assert confidence < 0.3
    assert breakdown.crime_penalty < 0


def test_government_announcement_not_event():
    confidence, _ = _score(GOVERNMENT_ANNOUNCEMENT)
    assert confidence < 0.65


def test_event_with_date_range():
    confidence, breakdown = _score(EVENT_WITH_DATE_RANGE)
    assert confidence > 0.7
    assert breakdown.future_event > 0
    assert breakdown.event_type > 0


def test_past_event_lower_confidence():
    confidence, breakdown = _score(PAST_EVENT_ARTICLE)
    assert breakdown.past_tense_penalty < 0
    assert confidence < 0.65


def test_concert_with_time():
    confidence, breakdown = _score(CONCERT_ARTICLE)
    assert confidence > 0.7
    assert breakdown.invitation > 0
    assert breakdown.event_type > 0


def test_empty_text():
    confidence, breakdown = _score(
        type("A", (), {"title": "", "content": ""})()
    )
    assert confidence < 0.1
