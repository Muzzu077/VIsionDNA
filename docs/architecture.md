# 🧠 VisionDNA System Architecture & AI Pipeline

This document provides a highly detailed breakdown of the VisionDNA core inference cycle. The system operates on a unified streaming pipeline architecture to maintain ultra-low latency while performing high-complexity multidimensional analysis.

## Pipeline Overview

The pipeline strictly processes frames sequentially. It converts unstructured visual data (pixels) into structured, semantic metadata ready for risk evaluation and digital twin visualization.

```text
[Raw Frame] 
    │ 
    ▼ 
[Detector] 
    │ 
    ▼ 
[Tracker] 
    │ 
    ▼ 
[Pose Estimator] 
    │ 
    ▼ 
[Feature Extractor] 
    │ 
    ▼ 
[Activity Recognizer] 
    │ 
    ▼ 
[Digital Twin Engine] 
    │ 
    ▼ 
[Risk Engine] 
    │ 
    ▼ 
[Prediction Engine] 
    │ 
    ▼ 
[WebSocket Egress]
```

---

## Deep-Dive: Stage by Stage

### 1. 📷 Raw Frame Ingestion
**Technology:** OpenCV, GStreamer / FFmpeg  
**Function:** Pulls frames from RTSP/WebRTC streams or direct file processing. Frames are downscaled (e.g., 640x640) and normalized dynamically to match the input requirements of the subsequent neural networks.

### 2. 🎯 Detector (YOLO)
**Technology:** YOLOv10 / TensorRT  
**Function:** Processes the entire frame to define 2D Bounding Boxes around persons and contextual objects (e.g., machinery, vehicles, bags). Confidence thresholds are applied dynamically to eliminate low-probability noise.

### 3. 🔗 Tracker (ByteTrack / SORT)
**Technology:** ByteTrack (default)  
**Function:** Assigns consistent IDs to detected targets across consecutive frames. ByteTrack is chosen for its superior ability to maintain ID coherence during occlusions by considering both high-score and low-score detection boxes.

### 4. 🧍 Pose Estimator (MediaPipe)
**Technology:** MediaPipe Pose / BlazePose  
**Function:** Operates conditionally *inside* the bounding boxes of detected persons. It isolates 33 key 3D landmarks on the human body (joints, eyes, extremities) to extract skeletal posture and limb articulation.

### 5. 🧬 Feature Extractor
**Technology:** Custom PyTorch Encoder  
**Function:** Normalizes the skeletal data and environmental bounding boxes into a standardized latent space. It translates raw pixel coordinates into camera-agnostic spatial vectors, helping abstract the position of the person relative to the physical scene.

### 6. 🏃 Activity Recognizer
**Technology:** Spatio-Temporal Graph Convolutional Networks (ST-GCN) or LSTM  
**Function:** Looks at an aggregated window of frames (e.g., the last 30 frames) of a tracked ID to determine the temporal action. Examples: *walking, running, sitting, falling, reaching.*

### 7. 🌐 Digital Twin Engine
**Technology:** Mathematical Homography & Depth Estimation  
**Function:** Correlates the 2D plane with calibrated camera intrinsic/extrinsic matrices to plot the tracked individuals onto a unified 3D coordinate system. This engine handles cross-camera re-identification (ReID) to unify an individual moving across different camera zones.

### 8. ⚠️ Risk Engine
**Technology:** Rules/Heuristics + ML Anomaly Detection  
**Function:** Synthesizes the Activity & Digital Twin status. 
*   *Is the person (ID=5) intersecting with a predefined Geo-fenced Danger Zone?*
*   *Did the Activity Recognizer flag "fall"?*
Generates instantaneous events/alerts based on contextual hazard calculations.

### 9. 🔮 Prediction Engine
**Technology:** Trajectory Forecasting Models (e.g., Social-LSTM / Kalman Filters)  
**Function:** Takes the historical pathway data of an entity and calculates probable future vectors (t+1, t+2, t+5 seconds). It acts as an early warning system (e.g., predicting a collision course between a forklift and a pedestrian).

### 10. 🔌 WebSocket Egress
**Technology:** FastAPI WebSockets, Redis Pub/Sub  
**Function:** Serializes the final enriched JSON payload (containing Box Coordinates, IDs, Pose Landmarks, Activities, Risk Flags, and Future Vectors). High-frequency state pushes (up to 30 FPS) are broadcast to listening frontend consumers for visual rendering.