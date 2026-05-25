FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

RUN python -c "from huggingface_hub import snapshot_download; snapshot_download('AltYaper/beto-events', local_dir='models/beto-events')"

EXPOSE 8001

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8001"]
