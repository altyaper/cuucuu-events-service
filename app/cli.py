from datetime import datetime

import click
from sqlalchemy import select

from app.config import settings
from app.db import SessionLocal
from app.models import Article, EventDetection
from app.pipeline import process_article
from app.schemas import ArticleInput


@click.group()
def cli():
    """cuucuu-events-service: Detect events in Spanish news articles."""
    pass


@cli.command()
@click.option("--id", "article_id", required=True, type=int, help="Article ID to process")
def process_one(article_id: int):
    """Process a single article by ID."""
    db = SessionLocal()
    try:
        article = db.get(Article, article_id)
        if not article:
            click.echo(f"Article {article_id} not found.")
            return

        article_input = ArticleInput(
            id=article.id,
            title=article.title or "",
            content=article.content or "",
            published_at=article.published_at,
            source=article.source,
        )
        result = process_article(article_input)
        _save_detection(db, result)
        db.commit()

        click.echo(result.model_dump_json(indent=2))
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=100, type=int, help="Max articles to process")
def process_new(limit: int):
    """Process articles that don't have an event detection yet."""
    db = SessionLocal()
    try:
        stmt = (
            select(Article)
            .outerjoin(EventDetection, Article.id == EventDetection.article_id)
            .where(EventDetection.id.is_(None))
            .where(Article.content.isnot(None))
            .order_by(Article.id.desc())
            .limit(limit)
        )
        articles = db.scalars(stmt).all()

        if not articles:
            click.echo("No unprocessed articles found.")
            return

        events_found = 0
        for article in articles:
            article_input = ArticleInput(
                id=article.id,
                title=article.title or "",
                content=article.content or "",
                published_at=article.published_at,
                source=article.source,
            )
            result = process_article(article_input)
            _save_detection(db, result)

            if result.is_event:
                events_found += 1

        db.commit()
        click.echo(f"Processed {len(articles)} articles. Events found: {events_found}")
    finally:
        db.close()


@cli.command()
@click.option("--since", required=True, type=str, help="Reprocess articles since YYYY-MM-DD")
@click.option("--limit", default=1000, type=int, help="Max articles to reprocess")
def reprocess(since: str, limit: int):
    """Reprocess articles from a given date."""
    since_date = datetime.strptime(since, "%Y-%m-%d")
    db = SessionLocal()
    try:
        stmt = (
            select(Article)
            .where(Article.published_at >= since_date)
            .where(Article.content.isnot(None))
            .order_by(Article.id.desc())
            .limit(limit)
        )
        articles = db.scalars(stmt).all()

        if not articles:
            click.echo("No articles found for that date range.")
            return

        events_found = 0
        for article in articles:
            article_input = ArticleInput(
                id=article.id,
                title=article.title or "",
                content=article.content or "",
                published_at=article.published_at,
                source=article.source,
            )
            result = process_article(article_input)
            _save_detection(db, result)

            if result.is_event:
                events_found += 1

        db.commit()
        click.echo(f"Reprocessed {len(articles)} articles. Events found: {events_found}")
    finally:
        db.close()


@cli.command()
@click.option("--limit", default=50, type=int)
@click.option("--min-confidence", default=0.4, type=float)
@click.option("--max-confidence", default=0.85, type=float)
def label_review(limit: int, min_confidence: float, max_confidence: float):
    """Review auto-labeled articles to build training data."""
    from app.models import TrainingLabel

    db = SessionLocal()
    try:
        stmt = (
            select(EventDetection)
            .where(EventDetection.confidence >= min_confidence)
            .where(EventDetection.confidence <= max_confidence)
            .order_by(EventDetection.confidence.desc())
            .limit(limit)
        )
        detections = db.scalars(stmt).all()

        if not detections:
            click.echo("No detections in that confidence range.")
            return

        labeled = 0
        for det in detections:
            article = db.get(Article, det.article_id)
            if not article:
                continue

            existing = db.scalars(
                select(TrainingLabel).where(TrainingLabel.article_id == article.id)
            ).first()
            if existing:
                continue

            click.echo(f"\n{'='*60}")
            click.echo(f"Article #{article.id} | Confidence: {det.confidence:.2f} | Auto: {'EVENT' if det.is_event else 'NO EVENT'}")
            click.echo(f"Title: {(article.title or '')[:100]}")
            click.echo(f"Content: {(article.content or '')[:300]}...")
            click.echo(f"{'='*60}")

            choice = click.prompt("Is this an event? [y/n/s(skip)/q(quit)]", type=str)

            if choice.lower() == "q":
                break
            if choice.lower() == "s":
                continue

            is_event = choice.lower() == "y"
            label = TrainingLabel(article_id=article.id, is_event=is_event, labeled_by="human")
            db.add(label)
            labeled += 1

        db.commit()
        click.echo(f"\nLabeled {labeled} articles.")
    finally:
        db.close()


def _save_detection(db, result):
    existing = db.scalars(
        select(EventDetection).where(EventDetection.article_id == result.article_id)
    ).first()

    data = {
        "is_event": result.is_event,
        "confidence": result.confidence,
        "event_name": result.event_name,
        "city": result.city,
        "venue": result.venue,
        "start_date": result.start_date,
        "end_date": result.end_date,
        "start_time": result.start_time,
        "end_time": result.end_time,
        "admission": result.admission,
        "organizer": result.organizer,
        "event_type": result.event_type,
        "evidence": result.evidence,
        "raw_output_json": result.model_dump(mode="json"),
    }

    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
    else:
        detection = EventDetection(article_id=result.article_id, **data)
        db.add(detection)


@cli.command()
@click.option("--epochs", default=3, type=int, help="Number of training epochs")
@click.option("--batch-size", default=16, type=int, help="Training batch size")
@click.option("--output", default="./models/beto-events", type=str, help="Output directory for model")
def train(epochs: int, batch_size: int, output: str):
    """Fine-tune BETO on labeled data."""
    from app.trainer import train as run_training
    run_training(epochs=epochs, batch_size=batch_size, output_dir=output)


if __name__ == "__main__":
    cli()
