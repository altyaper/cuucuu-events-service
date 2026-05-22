import re
import unicodedata
from html import unescape


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = _strip_structural_noise(text)
    text = _normalize_text(text)

    return text


def _strip_structural_noise(text: str) -> str:
    text = re.sub(r"<(script|style|nav|footer)[^>]*>.*?</\1>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def _normalize_text(text: str) -> str:
    text = unescape(text)
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#(\w+)", _split_hashtag, text)
    text = re.sub(r"[‐‑‒–—―−﹘﹣－]", "-", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_hashtag(match: re.Match) -> str:
    word = match.group(1)
    parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", word)
    parts = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", parts)
    return parts
