# RansomSim: AI‑Driven Ransomware Negotiation Training - Backend

AI-powered ransomware negotiation training platform built with FastAPI and Google Gemini 3.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. Run development server:
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core configuration
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── prompts/          # AI prompts
│   └── storage/          # Data storage
├── tests/                # Unit and integration tests
└── scripts/              # Utility scripts
```

## Testing

```bash
pytest
```

## Development

```bash
# Run with auto-reload
./scripts/run_dev.sh

# Test Gemini connection
python scripts/test_gemini.py
```
