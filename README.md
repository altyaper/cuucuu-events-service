# cuucuu-events-service

Detects local events in Spanish news articles using rule-based NLP. Exposes a FastAPI HTTP endpoint and a CLI for batch processing.

## Quick Start

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Run the API server
uvicorn app.api:app --reload --port 8001

# Test with curl
curl -X POST http://localhost:8001/detect \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Invitan a Expo Viaja Juárez 2026",
    "body": "Ciudad Juárez.- La Secretaría de Turismo invita a la comunidad a asistir este sábado 16 y domingo 17 de mayo a la quinta edición de la Expo Viaja Juárez 2026 en el centro de convenciones Injectronic, a partir de las 11:00 de la mañana a 8:00 de la noche, la entrada es libre.",
    "published_at": "2026-05-15T00:00:00"
  }'
```

## Docker

```bash
docker compose up --build
```

## CLI Commands

```bash
# Process a single article
python -m app.cli process-one --id 123

# Process all unprocessed articles
python -m app.cli process-new --limit 500

# Reprocess since a date
python -m app.cli reprocess --since 2026-05-01

# Review labels for training data
python -m app.cli label-review --limit 50
```

## Running Tests

```bash
pytest tests/ -v
```

## Architecture

1. **Normalizer** — strips HTML, normalizes whitespace
2. **Rules scorer** — keyword/pattern matching with weighted scoring
3. **Classifier** — abstract interface, currently rule-based (future: BETO transformer)
4. **Extractor** — regex + dateparser for structured field extraction
5. **Pipeline** — orchestrates all steps

## Adding BETO Classifier (Phase 2)

1. Label 300+ articles using `python -m app.cli label-review`
2. Install: `pip install transformers torch`
3. Uncomment `TransformerClassifier` in `app/classifier.py`
4. Train: `python -m app.cli train --epochs 3`
5. Set `EVENT_CLASSIFIER_TYPE=transformer` in `.env`

## API Endpoints

- `GET /health` — health check
- `POST /detect` — detect event in single article
- `POST /detect-batch` — detect events in multiple articles
