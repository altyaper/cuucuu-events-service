FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY models/beto-events/config.json models/beto-events/model.safetensors models/beto-events/tokenizer_config.json models/beto-events/tokenizer.json models/beto-events/

EXPOSE 8001

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8001"]
