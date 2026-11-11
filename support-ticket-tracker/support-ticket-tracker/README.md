# AI-Assisted Support Ticket Tracker

Full-stack app: users register, log in, and submit support tickets. Each ticket is automatically
categorised, prioritised and summarised, and a reply is drafted, using an LLM API. If the LLM is
unavailable or returns invalid output, a keyword-based fallback triages the ticket instead.

**Stack:** Python, FastAPI, SQLAlchemy, MySQL, JWT auth, React (Vite), Docker Compose, pytest.

## Architecture

```
React (Vite)  --/api-->  FastAPI  -->  MySQL
                           |
                           +--> LLM API (free provider) with rule-based fallback
```

```
backend/app
  main.py        app creation, CORS, router registration
  core/          settings read from environment (.env)
  database/      engine, session, Base
  models/        SQLAlchemy models: User, Ticket
  schemas/       Pydantic request/response models
  auth/          password hashing (bcrypt), JWT create/verify
  api/           shared dependencies (current user from JWT)
  routers/       users.py (register, login, me), tickets.py (CRUD)
  services/      triage.py (LLM call, validation, rule-based fallback)
backend/tests    pytest tests (LLM mocked, in-memory SQLite)
frontend/src     React app (AuthForm, TicketForm, TicketList)
```

## Run with Docker Compose (easiest)

1. Copy `.env.example` to `.env` and set `MYSQL_ROOT_PASSWORD` and `SECRET_KEY`.
   Optionally add a free LLM key in `LLM_API_KEY` (see below).
2. `docker compose up --build`
3. Open http://localhost:3000 (API docs: http://localhost:8000/docs).

## Run without Docker

**Backend** (needs MySQL, or use SQLite for a quick try):
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env  - then edit it
uvicorn app.main:app --reload
```
For a quick run without MySQL set `DATABASE_URL=sqlite:///./dev.db` in `backend/.env`.
For MySQL create the database first: `CREATE DATABASE ticketdb;`

**Frontend** (new terminal, needs Node 18+):
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 (requests to `/api` are proxied to the backend on port 8000).

## Free LLM key (Groq)

Create a free key at https://console.groq.com, then set `LLM_API_KEY`. Any OpenAI-compatible
provider works by changing `LLM_BASE_URL` and `LLM_MODEL`. Model names change over time, so
check the provider's current model list if you get an error. With no key, the app uses only the
rule-based triage. Use fake test tickets, because free tiers may use prompts for training.

## Tests
```bash
cd backend
python -m pytest
```

## API
| Method | Path | Description |
|---|---|---|
| POST | /api/users/register | Create account |
| POST | /api/users/login | Returns JWT (form fields: username = email, password) |
| GET | /api/users/me | Current user |
| POST | /api/tickets | Create ticket (triaged by LLM or fallback) |
| GET | /api/tickets | List your tickets |
| GET | /api/tickets/{id} | Get one of your tickets |
| PATCH | /api/tickets/{id}/status | open / in_progress / resolved |

## Design notes
- Every ticket query filters by the logged-in user's id, so users only see their own tickets.
- The LLM output is parsed and validated (allowed categories and priorities); anything invalid
  falls back to the rules, so ticket creation never fails because of the AI.
- Ticket text is treated as untrusted input in the prompt (prompt-injection mitigation).
- The AI call is isolated in `services/triage.py`, so the provider can be swapped by changing
  three environment variables.
