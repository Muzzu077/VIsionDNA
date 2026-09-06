# Visual Digital Twin Architecture & State Engine

VisionDNA's Visual Digital Twin is the core state representation of monitored entities and spatial environments. It transforms visual raw inputs into a computational twin model updated with every frame.

---

## 1. Digital State Model

For every monitored person, the digital twin maintains:
```json
{
  "tracking_id": "P001",
  "position": {
    "x": 412.5,
    "y": 238.0
  },
  "activity": "walking",
  "activity_confidence": 0.94,
  "posture": "upright",
  "movement_speed": 1.42,
  "current_zone": "corridor-zone-b",
  "distances_to_objects": {
    "high-voltage-panel-1": 42.8,
    "chemical-storage-rack": 110.2
  },
  "risk_score": 38.5,
  "risk_level": "MEDIUM",
  "recent_events": ["zone_transition: safe -> warning"],
  "predicted_event": {
    "type": "restricted_zone_entry",
    "probability": 0.86,
    "horizon_seconds": 10.2
  }
}
```

---

## 2. Digital Twin State Engine Lifecycle

```
Real-World Video Stream
         │
         ▼
Object & Person Detection (Bounding Boxes)
         │
         ▼
Multi-Object Tracker (Persistent Tracking ID Pxxx)
         │
         ▼
Ground Plane Projection & Feet Contact Localization
         │
         ▼
Spatial Containment & Zone Transition Engine (Point-in-Polygon)
         │
         ▼
Proximity Matrix Calculation (Euclidean Distance to Monitored Objects)
         │
         ▼
Digital Twin State Synthesizer
         │
         ├──► WebSocket Broadcast (/ws/digital-twin)
         ├──► Anomaly & Risk Evaluation Engine
         └──► Historical Analytics Persistence
```

---

## 3. Spatial Modeling (Zones & Objects)

- **Zones**: Defined as 2D polygonal vertices with assigned classification:
  - `SAFE`: Unrestricted pedestrian / work area (Risk Level: 0).
  - `MONITORED`: Operational area requiring standard safety precautions (Risk Level: 20-50).
  - `RESTRICTED`: High-hazard, unauthorized entry prohibited (Risk Level: 60-100).
- **Monitored Objects**: Defined by center coordinates and configurable hazard threshold radii $R_{\text{risk}}$.
- **Point-in-Polygon Testing**: Computed using OpenCV `pointPolygonTest` and Shapely geometry routines for sub-millisecond spatial evaluation.

---

## 4. 2D vs 3D Digital Twin Extensibility

- **MVP Implementation**: Real-time 2D top-down isometric projection mapped from camera homography and pixel coordinates.
- **Extension Points**: Standardized Pydantic schemas allow future expansion into 3D Gaussian Splatting / NeRF scene graphs and multi-camera fused point clouds.
