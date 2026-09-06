# Short-Horizon Risk Prediction Engine

VisionDNA distinguishes between **detection** (what is happening now) and **prediction** (what supported risk or state is likely to happen in the near future).

---

## 1. Predictive Horizon Concept

The prediction engine projects future spatial-temporal trajectories over bounded horizons:
- **Near-term Horizon ($T_{\text{horizon}}$)**: Configurable, typically 5s, 10s, or 30s.
- **Scope Limit**: Explicitly constrained to modeled activities and spatial collisions. The system does **not** claim arbitrary behavioral clairvoyance.

```
Current Trajectory History (t-15 .. t)
                  │
                  ▼
Velocity & Heading Vector Extrapolation (vx, vy, θ)
                  │
                  ▼
Forward Ray-Casting & LineString Geometry
                  │
                  ▼
Intersection with Restricted Zones / Obstacles
                  │
                  ├── Intersects? ──► Calculate Time-to-Entry ($t_{\text{entry}} = d / v$)
                  │                   Calculate Probability ($P \propto 1 / t_{\text{entry}}$)
                  │
                  ▼
Structured Prediction Output
```

---

## 2. Prediction Schema

```json
{
  "person_id": "P001",
  "prediction_type": "restricted_zone_entry",
  "predicted_activity": "approaching_restricted_area",
  "predicted_risk": "HIGH",
  "probability": 0.86,
  "horizon_seconds": 10.0,
  "explanation": "Trajectory projection intersects Restricted Area in approximately 10 seconds based on current heading and velocity (2.8 m/s).",
  "model_version": "Trajectory-Horizon-Predictor-v1.0.0"
}
```

---

## 3. Evaluation & Feedback Loop

- Predictions are logged with a timestamp, prediction horizon, and confidence score.
- As real events occur, outcomes are evaluated (`actual_outcome` and `was_correct`) to compute empirical precision, recall, and false-alarm rates displayed on the Prediction Analytics dashboard.
