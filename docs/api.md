# 📡 VisionDNA API Documentation

The VisionDNA platform uses a dual-protocol pattern: **RESTful HTTP endpoints** for state management, configuration, and historical queries, and **WebSockets** for high-frequency, real-time spatial intelligence streams.

## Base URL
All API requests are prefixed with: `/api/v1`

---

## 🟢 REST Endpoints

### 1. Health & Status
#### `GET /health`
Validates readiness of the API server, database connection, and inference pipeline.
*   **Response (200 OK):**
    ```json
    {
      "status": "healthy",
      "uptime_seconds": 3600,
      "services": {
         "database": "connected",
         "inference_engine": "active"
      }
    }
    ```

### 2. Sessions Management
#### `GET /sessions`
Retrieve a list of active analytics sessions (e.g., active camera streams being analyzed).

#### `POST /sessions`
Initiates a new analytics pipeline on a given stream URL.
*   **Body:**
    ```json
    {
       "stream_url": "rtsp://camera.local/feed1",
       "zone_id": "zone-warehouse-a",
       "enable_pose": true
    }
    ```

### 3. Incident & Risk Reporting
#### `GET /incidents`
Query historically logged incidents, filtered by timestamp, severity, or type.
*   **Query Params:** `?start_time=ISO8601 & type=fall_detected & severity=high`
*   **Response:** List of Incident Objects, encapsulating video snippets and relevant metadata.

---

## ⚡ WebSocket Endpoints

WebSockets provide the real-time telemetry crucial for the Digital Twin visualization.

### `WS /ws/stream/{session_id}`
Connect to receive standard JSON telemetry outputs at model inference frequency (typically 15-30 FPS). 

#### Typical Message Payload:
```json
{
  "timestamp": 1709401203.45,
  "frame_id": 4059,
  "entities": [
    {
      "id": "trk_49",
      "class": "person", 
      "bbox": [105, 30, 210, 480],  // [x_min, y_min, x_max, y_max]
      "activity": "walking",
      "velocity": 1.2, // meters per second
      "pose": {
         "landmarks": [{"x": 0.45, "y": 0.12, "z": -0.1, "visibility": 0.9}, ...]
      },
      "prediction_vector": [
         {"time": "+1s", "x": 115, "y": 490},
         {"time": "+2s", "x": 125, "y": 500}
      ],
      "risk_status": "safe" // or "critical"
    }
  ],
  "global_alerts": []
}
```

#### Event Filters:
Clients can send a configuration message to the socket to filter streams, reducing bandwidth:
```json
{
  "action": "subscribe",
  "filters": {
      "min_confidence": 0.7,
      "include_pose_data": false,
      "only_anomalies": true
  }
}
```