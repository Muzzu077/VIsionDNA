# Multi-Factor Risk Engine & Anomaly Detection

VisionDNA calculates risk as an aggregate multi-factor scoring function with full factor explainability.

---

## 1. Multi-Factor Risk Formulation

$$\text{Risk Score} = \min\left(100, \sum_{i} w_i \cdot S_i\right)$$

Where factors and default configurable weights are:

| Factor | Weight ($w_i$) | Description | Base Range ($S_i$) |
| :--- | :--- | :--- | :--- |
| **Activity Risk** | 0.25 | Inferred posture & kinematic behavior (e.g. falling=100, running=70, walking=20, standing=10) | 0 – 100 |
| **Zone Risk** | 0.20 | Spatial presence in safe vs. restricted zones | 0 – 100 |
| **Proximity Risk** | 0.20 | Proximity to hazardous machinery or equipment | 0 – 100 |
| **Movement Risk** | 0.15 | Sudden speed spike, erratic acceleration | 0 – 100 |
| **Behavioral Risk**| 0.10 | Historical pattern variance, abnormal trajectory | 0 – 100 |
| **Anomaly Score** | 0.10 | Output from rule detector / statistical isolation model | 0 – 100 |

---

## 2. Risk Level Classifications

- `0 – 30`: **LOW** (Normal baseline activity)
- `31 – 60`: **MEDIUM** (Elevated activity or caution zone)
- `61 – 80`: **HIGH** (Dangerous proximity, rapid approach to restricted area)
- `81 – 100`: **CRITICAL** (Fall detected, active restricted zone breach, severe collision risk)

---

## 3. Explainability Architecture

Every risk evaluation returns structured factor contributions:

```json
{
  "person_id": "P001",
  "score": 82.5,
  "level": "HIGH",
  "explanation": "Person P001 risk is HIGH. Top factor: In restricted zone +20.0, along with Dangerous proximity to High Voltage Panel +20.0",
  "factors": [
    {
      "type": "Zone",
      "score": 20.0,
      "description": "In restricted zone 'Server Room'"
    },
    {
      "type": "Proximity",
      "score": 20.0,
      "description": "Person P001 is dangerously close (12.4 units) to High Voltage Panel"
    },
    {
      "type": "Activity",
      "score": 17.5,
      "description": "High-risk activity (running)"
    },
    {
      "type": "Anomaly",
      "score": 10.0,
      "description": "Restricted zone entry anomaly detected"
    }
  ]
}
```

---

## 4. Anomaly Detection Engine

1. **Rule-Based Detectors**:
   - `restricted_zone_entry`: Unauthorized crossing into restricted polygons.
   - `dangerous_proximity`: Entity within configured hazard radius $R_{\text{risk}}$ of monitored equipment.
   - `prolonged_inactivity`: Static posture in monitored zones exceeding threshold time (e.g. potential worker collapse / unconsciousness).
   - `crowd_density`: Excessive entity count in high-risk zones.
2. **Statistical / ML Detectors**:
   - Baseline kinematic distribution profiling.
   - Isolation Forest anomaly detection scoring.
