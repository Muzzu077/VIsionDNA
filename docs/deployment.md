# Deployment & Production Guide

VisionDNA supports both local zero-dependency development (SQLite + FastAPI + Vite) and containerized multi-service production deployment (Docker Compose + PostgreSQL + Nginx).

---

## 1. Quick Start with Docker Compose

To deploy the entire production stack (PostgreSQL, Backend API, Frontend React Web App):

```bash
# 1. Clone repository
cd VISIONDNA

# 2. Copy and configure environment
cp .env.example .env

# 3. Build and launch containers
docker compose up --build -d
```

### Services Deployed:
| Service | Internal Port | Host Port | Purpose |
| :--- | :--- | :--- | :--- |
| `postgres` | 5432 | 5432 | Production relational event database |
| `backend` | 8000 | 8000 | FastAPI REST API & WebSocket server |
| `frontend` | 80 | 3000 | Production Nginx web server hosting React UI |

---

## 2. Local Development Startup (Without Docker)

### Backend:
```bash
cd backend
source venv/bin/activate  # or activate virtualenv
pip install -r requirements.txt

# Run migrations & seed data
alembic upgrade head

# Start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
# Accessible at http://localhost:5173
```

---

## 3. Environment Variables Reference

| Variable | Default (Local Dev) | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./visiondna.db` | Database connection string |
| `JWT_SECRET` | Secure random string | Secret key for signing JWT tokens |
| `JWT_EXPIRATION_MINUTES` | `60` | JWT token lifetime |
| `MODEL_PATH` | `./ml/models` | Storage path for trained model weights |
| `VIDEO_STORAGE_PATH` | `./data/videos` | Storage path for recorded footage |
| `INFERENCE_FPS` | `10` | Default inference frame rate |
| `DEMO_MODE` | `true` | Enables built-in deterministic demo telemetry |
| `CORS_ORIGINS` | `["http://localhost:3000", "http://localhost:5173"]` | Allowed CORS origins |
