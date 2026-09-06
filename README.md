# 🧬 VisionDNA: AI-Based Visual Digital Twin for Predictive Human Activity and Risk Analysis

> **Observe → Understand → Build Digital State → Analyze Behavior → Estimate Risk → Predict Near-Term Risk → Alert → Learn from History**

VisionDNA is an enterprise-grade AI and computer vision platform that transforms real-time video into a continuously synchronized **Visual Digital Twin** to predict human behaviors, assess physical risks, and prevent critical incidents across industrial facilities, hospitals, laboratories, campuses, and monitored environments.

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Key Innovation](#3-key-innovation)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Installation](#6-installation)
7. [Environment Setup](#7-environment-setup)
8. [Running Locally](#8-running-locally)
9. [Running with Docker](#9-running-with-docker)
10. [Demo & Simulation Mode](#10-demo--simulation-mode)
11. [Camera Setup](#11-camera-setup)
12. [AI Models & Pipeline](#12-ai-models--pipeline)
13. [Dataset Preparation](#13-dataset-preparation)
14. [Model Training Pipeline](#14-model-training-pipeline)
15. [Evaluation & Benchmarking](#15-evaluation--benchmarking)
16. [API Documentation](#16-api-documentation)
17. [Database Architecture](#17-database-architecture)
18. [Privacy & Security](#18-privacy--security)
19. [Real-World Limitations](#19-real-world-limitations)
20. [Future Scope](#20-future-scope)

---

## 1. Project Overview
VisionDNA operates on the core philosophy that human safety monitoring must focus on **risk prediction and incident prevention**, not merely post-incident surveillance. By bridging deep learning computer vision, multi-object tracking, pose estimation, and temporal kinematics with a digital twin state machine, VisionDNA delivers sub-second explainable risk insights and trajectory forecasting.

---

## 2. Problem Statement
Traditional CCTV surveillance systems are passive and reactive:
- Operators suffer from vigilance fatigue and miss developing hazards.
- Legacy computer vision systems trigger unexplainable false alarms on single static frames without temporal context.
- Incidents (falls, machinery collisions, unauthorized hazardous zone breaches) are detected only after injury or damage has occurred.

VisionDNA solves this by modeling the continuous physical state of the environment and using temporal trajectory analysis to predict collisions and zone intrusions seconds before they take place.

---

## 3. Key Innovation
> **VisionDNA transforms visual observations into a continuously updated digital representation of human/environmental state and uses temporal AI analysis to estimate and predict supported near-term risks.**

- **Strict Concept Separation**: Clearly distinguishes *detected event*, *inferred activity*, *anomaly*, *estimated risk*, and *predicted future risk*.
- **Spatial Digital Twin**: Maps pixel bounding boxes to ground plane contact coordinates and calculates real-time containment and distance metrics against virtual polygonal zones.
- **Explainable Multi-Factor Risk**: Never presents an opaque number; every score breaks down individual contributions (Activity, Zone, Proximity, Kinematics, Anomaly).
- **Graceful Fallbacks**: Fully operational even if heavy GPU models are offline, with explicit labeling between live AI telemetry and deterministic simulation.

---

## 4. System Architecture

```mermaid
graph TD
    A[Camera / Video Input] --> B[Video Ingestion & Preprocessing]
    B --> C[Object & Person Detection YOLOv8]
    C --> D[Multi-Object Tracker SORT/ByteTrack]
    D --> E[Pose Estimation 33 Keypoints]
    D --> F[Spatial Context & Zones]
    E --> G[Temporal Feature Extraction]
    F --> G
    G --> H[Activity Recognition GRU/Heuristic]
    H --> I[Visual Digital Twin State Engine]
    I --> J[Anomaly Detection Rule + ML]
    I --> K[Short-Horizon Trajectory Predictor]
    J --> L[Multi-Factor Risk Engine]
    K --> L
    L --> M[Real-Time Alert Dispatcher]
    L --> N[Historical Persistence & Analytics]
    M --> O[Interactive React Monitoring Dashboard]
    N --> O
```

---

## 5. Technology Stack

- **AI & Computer Vision**: Python 3.10+, PyTorch, Ultralytics YOLOv8, MediaPipe Pose, OpenCV, Shapely, NumPy, scikit-learn, joblib.
- **Backend & Real-Time API**: FastAPI, Async SQLAlchemy 2.0, Pydantic v2, WebSockets, aiosqlite, asyncpg, Alembic.
- **Frontend Dashboard**: React 19, TypeScript, Vite, Tailwind CSS v4, Recharts, Lucide React, Zustand, TanStack Query.
- **Database & Deployment**: SQLite (local development), PostgreSQL 15 (production), Docker, Docker Compose.

---

## 6. Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ & npm
- Git

### Clone Repository
```bash
git clone https://github.com/your-org/VISIONDNA.git
cd VISIONDNA
```

---

## 7. Environment Setup

Create your environment configuration:
```bash
cp .env.example .env
```

Configuration variables in `.env`:
```env
DATABASE_URL=sqlite+aiosqlite:///./visiondna.db
JWT_SECRET=your-secure-jwt-secret-key
MODEL_PATH=./ml/models
VIDEO_STORAGE_PATH=./data/videos
LOG_LEVEL=INFO
DEMO_MODE=true
```

---

## 8. Running Locally

### 1. Backend:
```bash
cd backend
source venv/bin/activate  # or create a new virtual environment
pip install -r requirements.txt

# Start FastAPI server (auto-initializes schema and seeds demo accounts)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`. Default credentials:
- **Admin**: `admin@visiondna.com` / `admin`
- **Operator**: `operator@visiondna.com` / `operator`
- **Viewer**: `viewer@visiondna.com` / `viewer`

---

## 9. Running with Docker

Deploy the complete multi-container production stack with PostgreSQL, Backend API, and Frontend Web App:
```bash
docker compose up --build -d
```
Access the application at `http://localhost:3000` (API documentation at `http://localhost:8000/docs`).

---

## 10. Demo & Simulation Mode
VisionDNA includes a dedicated **Demo Mode** enabled by default (`DEMO_MODE=true`).
- Generates a continuous telemetry feed demonstrating person tracking, zone transition from Main Sector to Restricted Area, risk escalation, trajectory intersection prediction, and automated alert triggering.
- Explicitly labeled in the UI as **SIMULATION MODE** to adhere to AI ethics principles and never present synthetic output as live inference.

---

## 11. Camera Setup
VisionDNA supports 4 primary input streams configured via the Camera Management dashboard:
1. **Webcam**: Direct local video capture device index (`0`, `1`).
2. **Uploaded Video**: MP4/AVI recorded inspection videos.
3. **RTSP Stream**: Real-time IP camera streams (`rtsp://user:pass@192.168.1.100:554/stream1`).
4. **HTTP MJPEG**: Live web streams.

---

## 12. AI Models & Pipeline
- **Detector**: YOLOv8 person detector (`ai/detection/yolo_detector.py`).
- **Tracker**: IoU / SORT tracker maintaining bounded spatial trajectories (`ai/tracking/sort_tracker.py`).
- **Pose**: MediaPipe Pose with 33 anatomical landmarks (`ai/pose/mediapipe_pose.py`).
- **Features**: Velocity vectors, aspect ratio, acceleration, distance metrics (`ai/features/extractor.py`).
- **Activity Recognizer**: Temporal GRU model classifying 7 activities (`ai/activity/`).
- **Digital Twin Engine**: Polygonal spatial containment and distance engine (`ai/digital_twin/state_engine.py`).
- **Risk Engine**: Multi-factor scoring with factor breakdowns (`ai/risk/risk_engine.py`).
- **Predictive Engine**: Forward ray-casting trajectory horizon calculator (`ai/prediction/predictor.py`).

---

## 13. Dataset Preparation
The `ml/datasets/adapter.py` module normalizes kinematic human activity datasets (UCF101, NTU RGB+D, Fall Datasets) into standardized temporal matrices of shape `(N, T=30, D=12)` containing normalized positions, velocities, aspect ratios, and spatial proximity metrics.

---

## 14. Model Training Pipeline
Train reproducible activity recognition and risk models:
```bash
PYTHONPATH=. python ml/train.py
```
Outputs trained weights to `./ml/models/temporal_activity_gru.pt` and `./ml/models/risk_regressor_rf.joblib`.

---

## 15. Evaluation & Benchmarking
Run empirical model evaluation without fabricated metrics:
```bash
PYTHONPATH=. python ml/evaluate.py
```
Calculates test set Accuracy, Precision, Recall, F1-Score, MAE, R2-Score, and Latency (ms/sample).

---

## 16. API Documentation
FastAPI provides automatic interactive Swagger documentation at `/docs` and OpenAPI JSON at `/openapi.json`.
- `POST /api/auth/login`: Authenticate and obtain JWT token.
- `GET /api/cameras`: List registered cameras and statuses.
- `GET /api/persons`: List tracked entities and active states.
- `GET /api/digital-twins`: Retrieve current spatial digital twin state.
- `GET /api/risks`: Query risk events and factor breakdowns.
- `PUT /api/risks/{id}/acknowledge`: Acknowledge risk event.
- `GET /api/predictions`: Query predictive trajectory outputs.
- `GET /api/alerts`: List active system safety alerts.
- `GET /api/system/health`: Component health status.
- `WebSocket /ws/live`, `/ws/alerts`, `/ws/digital-twin`: Real-time telemetry streams.

---

## 17. Database Architecture
Normalized relational database schema managed by SQLAlchemy and Alembic:
- `users`: User credentials, roles, and status.
- `environments`: Monitored facilities and spatial configuration.
- `cameras`: Video stream sources, resolution, and fps.
- `persons`: Ephemeral tracking identities and temporal bounds.
- `person_states`: High-frequency kinematic coordinates, velocity, posture.
- `activity_events`: Detected activities, confidence, and timestamps.
- `digital_twin_states`: Full snapshot of spatial and risk state.
- `risk_events`: Severity, risk score, factor breakdown, status lifecycle.
- `predictions`: Predicted events, horizon seconds, probability.
- `alerts`: Actionable alerts, acknowledge timestamps and user links.
- `zones`: Polygonal spatial boundaries (SAFE, RESTRICTED, HIGH_RISK).
- `monitored_objects`: Spatial hazard stations and danger radii.
- `model_versions`: Model metadata, versions, and validation metrics.

---

## 18. Privacy & Security
- **No Facial Recognition**: Ephemeral IDs only (`P001`, `P002`).
- **Data Minimization**: Video frames are processed in-memory and discarded.
- **RBAC**: Protected endpoints with ADMIN, OPERATOR, and VIEWER roles.
- **Password Security**: Native bcrypt salt and hashing.

---

## 19. Real-World Limitations
- VisionDNA does not claim arbitrary behavioral clairvoyance or mind-reading.
- Predictions are strictly bounded to spatial-temporal trajectory extrapolation and modeled activity classes.
- Camera occlusion, extreme low lighting, or poor lens quality can affect detection accuracy.
- VisionDNA is designed as an operator assistance tool and should not be the sole safety mechanism in life-critical industrial setups.

---

## 20. Future Scope
- **3D Digital Twin**: Expanding 2D top-down maps into 3D Gaussian Splats and multi-camera fused point clouds.
- **Multi-Camera Fusion**: Cross-camera re-identification across overlapping camera fields of view.
- **IoT & Wearables**: Fusion with UWB badges and environmental gas/temperature sensors.
- **Edge Deployment**: Pre-compiled TensorRT engines for NVIDIA Jetson Orin micro-servers.