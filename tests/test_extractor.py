from datetime import date, datetime, time

from app.cleaning import clean_text
from app.extractor import (
    extract_admission,
    extract_all,
    extract_city,
    extract_dates,
    extract_event_name,
    extract_event_type,
    extract_organizer,
    extract_times,
    extract_venue,
)
from tests.conftest import CONCERT_ARTICLE, EVENT_WITH_DATE_RANGE, SAMPLE_EVENT_ARTICLE

REF_DATE = datetime(2026, 5, 15)

SAMPLE_TEXT = clean_text(f"{SAMPLE_EVENT_ARTICLE.title} {SAMPLE_EVENT_ARTICLE.body}")


def test_extract_city_from_lead():
    assert extract_city(SAMPLE_TEXT) == "Ciudad Juárez"


def test_extract_city_fallback():
    assert extract_city("Algo random", "Chihuahua") == "Chihuahua"


def test_extract_venue_sample():
    venue = extract_venue(SAMPLE_TEXT)
    assert venue is not None
    assert "convenciones" in venue.lower()


def test_extract_event_type_expo():
    assert extract_event_type(SAMPLE_TEXT) == "expo"


def test_extract_event_type_concierto():
    text = clean_text(f"{CONCERT_ARTICLE.title} {CONCERT_ARTICLE.body}")
    assert extract_event_type(text) == "concierto"


def test_extract_event_name():
    name = extract_event_name(SAMPLE_TEXT)
    assert name is not None
    assert "Expo" in name or "Viaja" in name or "Juárez" in name


def test_extract_organizer():
    org = extract_organizer(SAMPLE_TEXT)
    assert org is not None
    assert "Turismo" in org


def test_extract_admission_libre():
    assert extract_admission(SAMPLE_TEXT) == "libre"


def test_extract_admission_price():
    text = "Los boletos tienen un costo de $150 pesos."
    admission = extract_admission(text)
    assert admission is not None
    assert "150" in admission


def test_extract_dates_range_sabado_domingo():
    start, end = extract_dates(SAMPLE_TEXT, REF_DATE)
    assert start == date(2026, 5, 16)
    assert end == date(2026, 5, 17)


def test_extract_dates_del_al():
    text = clean_text(f"{EVENT_WITH_DATE_RANGE.title} {EVENT_WITH_DATE_RANGE.body}")
    start, end = extract_dates(text, REF_DATE)
    assert start == date(2026, 6, 20)
    assert end == date(2026, 6, 25)


def test_extract_times_range():
    start_time, end_time = extract_times(SAMPLE_TEXT)
    assert start_time == time(11, 0)
    assert end_time == time(20, 0)


def test_extract_times_single():
    text = "el concierto a las 20:00 hrs en el Teatro."
    start_time, end_time = extract_times(text)
    assert start_time == time(20, 0)


def test_extract_all_sample_article():
    fields = extract_all(SAMPLE_TEXT, reference_date=REF_DATE)

    assert fields["event_type"] == "expo"
    assert fields["city"] == "Ciudad Juárez"
    assert fields["admission"] == "libre"
    assert fields["start_date"] == date(2026, 5, 16)
    assert fields["end_date"] == date(2026, 5, 17)
    assert fields["start_time"] == time(11, 0)
    assert fields["end_time"] == time(20, 0)
    assert fields["organizer"] is not None
    assert fields["venue"] is not None
    assert fields["evidence"] is not None
