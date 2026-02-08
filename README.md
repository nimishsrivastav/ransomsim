# RansomSim: AI-Driven Ransomware Negotiation Training

An AI-powered training platform for security teams to practice ransomware negotiations in a safe, controlled environment using Google Gemini.

> **Training Simulation Only** — This tool is for educational purposes. It contains no real payment mechanisms, cryptocurrency wallets, or actual threat actor communication channels.

## The Problem

Organizations face ransomware attacks every 11 seconds but are unprepared for the negotiation process, leading to poor decisions, overpayments, and compliance missteps. Traditional training methods like tabletop exercises fail to replicate the psychological pressure and dynamic nature of real negotiations.

## The Solution

RansomSim provides interactive simulations where Gemini role-plays as different ransomware threat actors, delivering realistic, adaptive negotiation experiences with post-simulation analysis and learning outcomes.

## Features

- **Three Threat Actor Personas** — Practice against varying difficulty levels:
  - *The Professional* — Sophisticated APT group (Hard)
  - *The Opportunist* — Mid-tier cybercriminal gang (Medium)
  - *The Script Kiddie* — Unsophisticated attacker (Easy)
- **Dynamic Scenario Generation** — Realistic breach narratives based on organization size, industry, and data sensitivity
- **Adaptive AI Behavior** — Threat actors adjust tactics based on your responses (stalling detection, lowball recognition, authority testing)
- **Real-Time Chat Interface** — Multi-turn negotiation with pressure indicators and deadline countdowns
- **Post-Simulation Analysis** — Performance scorecard, tactical breakdown, benchmark comparison, and improvement recommendations
- **Ethical Safeguards** — Training-only disclaimers, law enforcement resource links, no real payment mechanisms

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion |
| Backend | Python 3.12, FastAPI, Pydantic |
| AI | Google Gemini 3 (via `google-genai` SDK) |
| Deployment | Docker, Docker Compose |

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 22+
- [Google Gemini API Key](https://aistudio.google.com/apikey)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/ransomware-negotiator-simulator.git
cd ransomware-negotiator-simulator

# Set your Gemini API key in backend/.env
cp backend/.env.example backend/.env
# Edit backend/.env and set GEMINI_API_KEY

# Start both services
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/api/docs

### Option 2: Manual Setup

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set GEMINI_API_KEY

uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install

echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

## How It Works

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Configure  │────▶│   Generate   │ ────▶│  Negotiate   │────▶│   Analyze    │
│  Scenario   │      │   Scenario   │      │  (Chat UI)   │      │  Performance │
└─────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
  Org size,           AI creates a         Multi-turn           Scorecard,
  industry,           realistic breach     conversation         tactical
  persona             narrative            with threat actor    insights
```

1. **Configure** — Select organization size, industry, data sensitivity, and threat actor persona
2. **Generate** — Gemini creates a realistic breach scenario with ransom demand and deadline
3. **Negotiate** — Engage in multi-turn chat with the AI threat actor under time pressure
4. **Analyze** — Review your performance scorecard, tactical breakdown, and improvement recommendations

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/scenarios/generate` | Generate a new breach scenario |
| `GET` | `/api/v1/scenarios/{id}` | Retrieve a scenario |
| `POST` | `/api/v1/negotiations/start` | Start a negotiation session |
| `POST` | `/api/v1/negotiations/{id}/message` | Send a message |
| `GET` | `/api/v1/negotiations/{id}/history` | Get conversation history |
| `POST` | `/api/v1/negotiations/{id}/complete` | End a negotiation |
| `POST` | `/api/v1/analysis/{id}` | Generate performance analysis |
| `GET` | `/api/v1/analysis/{id}` | Retrieve cached analysis |

Full interactive docs available at `/api/docs` (Swagger) and `/api/redoc` (ReDoc).

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-3-flash-preview` | Gemini model to use |
| `GEMINI_TEMPERATURE` | No | `0.8` | AI response creativity |
| `APP_ENV` | No | `development` | Environment mode |
| `ALLOWED_ORIGINS` | No | `["http://localhost:3000"]` | CORS allowed origins |
| `RATE_LIMIT_PER_MINUTE` | No | `30` | Per-IP rate limit |
| `SESSION_EXPIRATION_HOURS` | No | `48` | Session TTL |
| `MAX_MESSAGES_PER_SESSION` | No | `50` | Max messages per session |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | — | Backend API URL |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/            # Routes, middleware (rate limiting, security headers)
│   │   ├── core/           # Config, exceptions, logging
│   │   ├── models/         # Pydantic schemas, domain models
│   │   ├── services/       # Gemini client, session manager, message validation
│   │   ├── prompts/        # Threat actor personas, scenario templates
│   │   └── main.py         # FastAPI entry point
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages (home, configure, negotiate, analysis)
│   │   ├── components/ui/  # shadcn/ui components
│   │   ├── lib/            # API client, utilities
│   │   └── types/          # TypeScript type definitions
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Security

- Prompt injection protection via message validation and sanitization
- Session ownership enforced with client tokens
- Per-IP rate limiting to prevent API abuse
- Server-side API key storage (never exposed to frontend)
- CORS origin whitelisting
- Security headers middleware

## Disclaimer

This is a **training and educational tool only**. It is not intended to facilitate, encourage, or assist in any actual ransomware activity. Users should always contact law enforcement when facing a real ransomware incident:

- [FBI IC3](https://www.ic3.gov/)
- [CISA](https://www.cisa.gov/stopransomware)

## License

MIT
