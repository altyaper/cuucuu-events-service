from abc import ABC, abstractmethod

from app.config import settings
from app.rules import ScoringBreakdown, score_article


class ClassificationResult:
    def __init__(self, is_event: bool, confidence: float, breakdown: ScoringBreakdown | None = None):
        self.is_event = is_event
        self.confidence = confidence
        self.breakdown = breakdown


class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, text: str) -> ClassificationResult:
        pass


class RuleBasedClassifier(BaseClassifier):
    def __init__(self, threshold: float | None = None):
        self.threshold = threshold or settings.event_threshold

    def classify(self, text: str) -> ClassificationResult:
        confidence, breakdown = score_article(text)
        is_event = confidence >= self.threshold
        return ClassificationResult(is_event=is_event, confidence=confidence, breakdown=breakdown)


class TransformerClassifier(BaseClassifier):
    def __init__(self, model_path: str | None = None):
        from transformers import pipeline

        path = model_path or settings.model_path
        self.pipe = pipeline("text-classification", model=path, tokenizer=path)

    def classify(self, text: str) -> ClassificationResult:
        result = self.pipe(text[:512], truncation=True)[0]
        is_event = result["label"] == "EVENTO"
        confidence = result["score"] if is_event else 1.0 - result["score"]
        return ClassificationResult(is_event=is_event, confidence=confidence)


def get_classifier() -> BaseClassifier:
    if settings.classifier_type == "transformer":
        return TransformerClassifier()
    return RuleBasedClassifier()
