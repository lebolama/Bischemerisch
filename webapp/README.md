# Webapp Deployment (Bischemerisch Übersetzer)

## Lokal starten

```bash
cd webapp/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Dann im Browser: `http://localhost:8000`

## Deployment-Zielstruktur für https://www.beierstettel.de/bischemerisch/

Empfehlung auf dem Server:

- `bischemerisch/backend/` (FastAPI-App)
- `bischemerisch/frontend/` (wird über FastAPI als static ausgeliefert)
- `bischemerisch/data/`, `bischemerisch/analysis/`, `bischemerisch/generator/`, `bischemerisch/output/`

Die App nutzt direkt die vorhandenen Python-Module des Repositories.
