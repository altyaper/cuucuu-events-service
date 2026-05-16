from app.classifier import get_classifier
from app.extractor import extract_all
from app.normalizer import normalize
from app.schemas import ArticleInput, EventDetectionResult


def process_article(article: ArticleInput) -> EventDetectionResult:
    full_text = f"{article.title} {article.content}"
    normalized = normalize(full_text)

    classifier = get_classifier()
    classification = classifier.classify(normalized)

    warnings: list[str] = []

    if not classification.is_event:
        return EventDetectionResult(
            article_id=article.id,
            is_event=False,
            confidence=round(classification.confidence, 4),
            warnings=warnings,
        )

    fields = extract_all(
        normalized,
        reference_date=article.published_at,
    )

    if not fields["start_date"]:
        warnings.append("No se pudo extraer fecha del evento")
    if not fields["venue"]:
        warnings.append("No se pudo extraer lugar del evento")
    if not fields["event_name"]:
        warnings.append("No se pudo extraer nombre del evento")

    return EventDetectionResult(
        article_id=article.id,
        is_event=True,
        confidence=round(classification.confidence, 4),
        event_name=fields["event_name"],
        city=fields["city"],
        venue=fields["venue"],
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
