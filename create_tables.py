"""Create event_detections and training_labels tables in the existing cuucuu_dev database."""
from app.db import engine
from app.models import EventDetection, TrainingLabel

if __name__ == "__main__":
    EventDetection.__table__.create(engine, checkfirst=True)
    TrainingLabel.__table__.create(engine, checkfirst=True)
    print("Tables created: event_detections, training_labels")
