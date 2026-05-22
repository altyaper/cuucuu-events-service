from __future__ import annotations

import logging
import time as _time
from datetime import datetime

from app.classifier import get_classifier
from app.cleaning import clean_text
from app.extractor import extract_all
from app.refiner import refine
from app.schemas import ArticleRequest, EventResponse

logger = logging.getLogger(__name__)


def process_article(article: ArticleRequest) -> EventResponse:
    t0 = _time.perf_counter()

    title = clean_text(article.title)
    body = clean_text(article.body)
    full_text = f"{title} {body}"

    classifier = get_classifier()
    t1 = _time.perf_counter()
    classification = classifier.classify(full_text)
    t2 = _time.perf_counter()
    logger.info(f"BETO classify: {t2 - t1:.2f}s")

    published_at = None
    if article.date:
        try:
            published_at = datetime.strptime(article.date, "%Y-%m-%d")
        except ValueError:
            pass

    warnings: list[str] = []

    if not classification.is_event:
        return EventResponse(
            is_event=False,
            confidence=round(classification.confidence, 4),
            warnings=warnings,
        )

    t3 = _time.perf_counter()
    refined = refine(title, body, published_at)
    t4 = _time.perf_counter()
    logger.info(f"OpenAI refine: {t4 - t3:.2f}s | Total so far: {t4 - t0:.2f}s")

    if refined:
        dates = refined["dates"]
        start_date = dates[0] if dates else None
        end_date = dates[-1] if len(dates) > 1 else None

        if not refined["event_name"]:
            warnings.append("No se pudo extraer nombre del evento")
        if not dates:
            warnings.append("No se pudo extraer fecha del evento")
        if not refined["venue"]:
            warnings.append("No se pudo extraer lugar del evento")

        return EventResponse(
            is_event=True,
            confidence=round(classification.confidence, 4),
            event_name=refined["event_name"],
            description=refined["description"],
            dates=dates,
            start_date=start_date,
            end_date=end_date,
            start_time=refined["start_time"],
            end_time=refined["end_time"],
            city=refined["city"],
            venue=refined["venue"],
            event_type=refined["event_type"],
            admission=refined["admission"],
            organizer=refined["organizer"],
            evidence=refined["evidence"],
            warnings=warnings,
        )

    logger.info("Falling back to regex extraction")
    fields = extract_all(full_text, reference_date=published_at)

    if not fields["start_date"]:
        warnings.append("No se pudo extraer fecha del evento")
    if not fields["venue"]:
        warnings.append("No se pudo extraer lugar del evento")
    if not fields["event_name"]:
        warnings.append("No se pudo extraer nombre del evento")

    dates = []
    if fields["start_date"]:
        dates.append(fields["start_date"])
    if fields["end_date"] and fields["end_date"] != fields["start_date"]:
        dates.append(fields["end_date"])

    return EventResponse(
        is_event=True,
        confidence=round(classification.confidence, 4),
        event_name=fields["event_name"],
        city=fields["city"],
        venue=fields["venue"],
        dates=dates,
        start_date=fields["start_date"],
        end_date=fields["end_date"],
        start_time=fields["start_time"],
        end_time=fields["end_time"],
        admission=fields["admission"],
        organizer=fields["organizer"],
        event_type=fields["event_type"],
        evidence=fields["evidence"],
        warnings=warnings,
    )
