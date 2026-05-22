from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.pipeline import process_article
from app.schemas import ArticleRequest, EventResponse

app = FastAPI(title="cuucuu-events-service", version="0.2.0")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/get-event", response_model=EventResponse)
def get_event(article: ArticleRequest):
    return process_article(article)
