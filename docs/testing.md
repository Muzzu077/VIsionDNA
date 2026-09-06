# Test Suite & Quality Assurance Guide

VisionDNA includes automated test suites covering authentication, REST APIs, database models, computer vision components, anomaly detection, risk assessment, trajectory prediction, and complete end-to-end pipelines.

---

## 1. Running Backend Tests

Run all unit and integration tests using pytest:

```bash
cd backend
./venv/bin/pytest -v tests/
```

### Test Suite Structure:
| Test File | Scope | Description |
| :--- | :--- | :--- |
| `test_auth.py` | API & Security | JWT login, password verification, registration, RBAC role permissions |
| `test_api_cameras.py` | API & Video | Camera CRUD, stream lifecycle (start/stop), connectivity checks |
| `test_api_zones.py` | API & Spatial | Polygonal zone creation, editing, deletion |
| `test_api_digital_twin.py` | API & State | Digital twin state listing, historical telemetry per person |
| `test_api_risks_alerts.py` | API & Lifecycle | Risk events, acknowledgement lifecycle, alert notifications |
| `test_api_system.py` | API & Observability | Health checks, system metrics, hardware monitoring |
| `test_ai_detection_tracking.py` | AI / CV | YOLO detector interface, IoU / SORT tracker, ID persistence |
| `test_ai_features_activity.py` | AI / ML | Kinematic feature extraction, heuristic activity classification |
| `test_ai_anomaly_risk.py` | AI / Risk | Rule-based anomaly detection, multi-factor risk engine with explanations |
| `test_ai_prediction.py` | AI / Predictive | Trajectory extrapolation, restricted zone polygon intersection, probability |
| `test_pipeline_e2e.py` | End-to-End | Full pipeline test (Frame Ingest -> Detect -> Track -> Activity -> Twin -> Risk -> Prediction -> Alert) |

---

## 2. Running Frontend Build & Verification

```bash
cd frontend
npm run build
```

---

## 3. Running ML Training & Evaluation Pipeline

```bash
PYTHONPATH=. ./backend/venv/bin/python ml/train.py
PYTHONPATH=. ./backend/venv/bin/python ml/evaluate.py
PYTHONPATH=. ./backend/venv/bin/python ml/export_model.py
```
