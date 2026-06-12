VENV := .venv
PYTHON := $(VENV)/bin/python
UVICORN := $(VENV)/bin/uvicorn

.PHONY: run install test

run:
	$(UVICORN) app.api:app --reload --port 8002

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest
