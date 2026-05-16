from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import Article, EventDetection, TrainingLabel
from app.pipeline import process_article
from app.schemas import ArticleInput, DetectBatchRequest, EventDetectionResult

app = FastAPI(title="cuucuu-events-service", version="0.1.0")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect", response_model=EventDetectionResult)
def detect(article: ArticleInput):
    return process_article(article)


@app.post("/detect-batch", response_model=list[EventDetectionResult])
def detect_batch(request: DetectBatchRequest):
    return [process_article(article) for article in request.articles]


# --- Labeling UI endpoints ---


@app.get("/label/stats")
def label_stats():
    db = SessionLocal()
    try:
        total_detections = db.scalar(select(func.count(EventDetection.id)))
        total_labeled = db.scalar(select(func.count(TrainingLabel.id)))
        labeled_events = db.scalar(
            select(func.count(TrainingLabel.id)).where(TrainingLabel.is_event == True)
        )
        labeled_not_events = db.scalar(
            select(func.count(TrainingLabel.id)).where(TrainingLabel.is_event == False)
        )
        return {
            "total_detections": total_detections or 0,
            "total_labeled": total_labeled or 0,
            "labeled_events": labeled_events or 0,
            "labeled_not_events": labeled_not_events or 0,
            "remaining": (total_detections or 0) - (total_labeled or 0),
        }
    finally:
        db.close()


@app.get("/label/next")
def label_next(min_confidence: float = 0.0, max_confidence: float = 1.0):
    db = SessionLocal()
    try:
        stmt = (
            select(EventDetection, Article)
            .join(Article, EventDetection.article_id == Article.id)
            .outerjoin(TrainingLabel, EventDetection.article_id == TrainingLabel.article_id)
            .where(TrainingLabel.id.is_(None))
            .where(EventDetection.confidence >= min_confidence)
            .where(EventDetection.confidence <= max_confidence)
            .order_by(EventDetection.confidence.desc())
            .limit(1)
        )
        row = db.execute(stmt).first()

        if not row:
            return {"done": True}

        det, art = row
        return {
            "done": False,
            "article": {
                "id": art.id,
                "title": art.title,
                "content": (art.content or "")[:2000],
                "source": art.source,
                "published_at": str(art.published_at) if art.published_at else None,
            },
            "detection": {
                "is_event": det.is_event,
                "confidence": round(det.confidence, 4),
                "event_name": det.event_name,
                "city": det.city,
                "venue": det.venue,
                "start_date": str(det.start_date) if det.start_date else None,
                "end_date": str(det.end_date) if det.end_date else None,
                "start_time": str(det.start_time) if det.start_time else None,
                "end_time": str(det.end_time) if det.end_time else None,
                "admission": det.admission,
                "organizer": det.organizer,
                "event_type": det.event_type,
            },
        }
    finally:
        db.close()


class LabelSubmission(BaseModel):
    article_id: int
    is_event: bool


@app.post("/label/submit")
def label_submit(submission: LabelSubmission):
    db = SessionLocal()
    try:
        existing = db.scalars(
            select(TrainingLabel).where(TrainingLabel.article_id == submission.article_id)
        ).first()

        if existing:
            existing.is_event = submission.is_event
        else:
            label = TrainingLabel(
                article_id=submission.article_id,
                is_event=submission.is_event,
                labeled_by="human",
            )
            db.add(label)

        db.commit()
        return {"ok": True}
    finally:
        db.close()


@app.post("/label/skip/{article_id}")
def label_skip(article_id: int):
    db = SessionLocal()
    try:
        existing = db.scalars(
            select(TrainingLabel).where(TrainingLabel.article_id == article_id)
        ).first()

        if not existing:
            label = TrainingLabel(
                article_id=article_id,
                is_event=False,
                labeled_by="skipped",
            )
            db.add(label)
            db.commit()

        return {"ok": True}
    finally:
        db.close()


class BulkAutoLabelRequest(BaseModel):
    high_threshold: float = 0.9
    low_threshold: float = 0.15


@app.post("/label/bulk-auto")
def label_bulk_auto(req: BulkAutoLabelRequest):
    db = SessionLocal()
    try:
        already_labeled = select(TrainingLabel.article_id)

        high_stmt = (
            select(EventDetection)
            .where(EventDetection.confidence >= req.high_threshold)
            .where(EventDetection.article_id.notin_(already_labeled))
        )
        high_dets = db.scalars(high_stmt).all()
        for det in high_dets:
            db.add(TrainingLabel(article_id=det.article_id, is_event=True, labeled_by="auto-high"))

        low_stmt = (
            select(EventDetection)
            .where(EventDetection.confidence <= req.low_threshold)
            .where(EventDetection.article_id.notin_(already_labeled))
        )
        low_dets = db.scalars(low_stmt).all()
        for det in low_dets:
            db.add(TrainingLabel(article_id=det.article_id, is_event=False, labeled_by="auto-low"))

        db.commit()

        return {
            "auto_labeled_events": len(high_dets),
            "auto_labeled_not_events": len(low_dets),
            "total_auto_labeled": len(high_dets) + len(low_dets),
        }
    finally:
        db.close()


@app.get("/label/preview-bulk")
def label_preview_bulk(high_threshold: float = 0.9, low_threshold: float = 0.15):
    db = SessionLocal()
    try:
        already_labeled = select(TrainingLabel.article_id)

        high_count = db.scalar(
            select(func.count(EventDetection.id))
            .where(EventDetection.confidence >= high_threshold)
            .where(EventDetection.article_id.notin_(already_labeled))
        ) or 0

        low_count = db.scalar(
            select(func.count(EventDetection.id))
            .where(EventDetection.confidence <= low_threshold)
            .where(EventDetection.article_id.notin_(already_labeled))
        ) or 0

        manual_count = db.scalar(
            select(func.count(EventDetection.id))
            .where(EventDetection.confidence > low_threshold)
            .where(EventDetection.confidence < high_threshold)
            .where(EventDetection.article_id.notin_(already_labeled))
        ) or 0

        return {
            "will_auto_event": high_count,
            "will_auto_not_event": low_count,
            "remaining_manual": manual_count,
        }
    finally:
        db.close()
