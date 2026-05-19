import logging

from app.classifier import get_classifier
from app.extractor import extract_all
from app.normalizer import normalize
from app.refiner import refine
from app.schemas import ArticleInput, EventDetectionResult

logger = logging.getLogger(__name__)


def process_article(article: ArticleInput) -> EventDetectionResult:
    full_text = f"{article.title or ''} {article.content or ''}"
    normalized = normalize(full_text)

    classifier = get_classifier()
    classification = classifier.classify(normalized)

    warnings: list[str] = []

    if not classification.is_event:
        return EventDetectionResult(
            article_id=article.resolved_id,
            is_event=False,
            confidence=round(classification.confidence, 4),
            warnings=warnings,
        )

    refined = refine(article.title or "", article.content or "", article.published_at)

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

        return EventDetectionResult(
            article_id=article.resolved_id,
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
    fields = extract_all(normalized, reference_date=article.published_at)

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

    return EventDetectionResult(
        article_id=article.resolved_id,
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
