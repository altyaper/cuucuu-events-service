from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(BigInteger, primary_key=True)
    url = Column(Text, nullable=False, unique=True)
    title = Column(Text)
    content = Column(Text)
    summary = Column(Text)
    author = Column(Text)
    thumbnail_url = Column(Text)
    published_at = Column(DateTime(timezone=False))
    tags = Column(ARRAY(Text), default=[])
    category = Column(Text)
    source = Column(Text, nullable=False)
    scraped_at = Column(DateTime(timezone=False), nullable=False)
    raw_html = Column(Text)
    content_hash = Column(String(64), unique=True)
    hash_id = Column(String, unique=True)
    word_count = Column(Integer)
    reading_time_minutes = Column(Integer)
    clicks = Column(Integer, default=0)
    votes = Column(Integer, default=0)
    thumb_path = Column(Text)
    inserted_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now())

    detection = relationship("EventDetection", back_populates="article", uselist=False)


class EventDetection(Base):
    __tablename__ = "event_detections"

    id = Column(BigInteger, primary_key=True)
    article_id = Column(BigInteger, ForeignKey("articles.id"), unique=True, nullable=False)
    is_event = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    event_name = Column(String(500))
    city = Column(String(255))
    venue = Column(String(500))
    start_date = Column(Date)
    end_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    admission = Column(String(255))
    organizer = Column(String(500))
    event_type = Column(String(100))
    evidence = Column(Text)
    raw_output_json = Column(JSON)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())

    article = relationship("Article", back_populates="detection")


class TrainingLabel(Base):
    __tablename__ = "training_labels"

    id = Column(BigInteger, primary_key=True)
    article_id = Column(BigInteger, ForeignKey("articles.id"), unique=True, nullable=False)
    is_event = Column(Boolean, nullable=False)
    labeled_by = Column(String(100), default="human")
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    article = relationship("Article")
