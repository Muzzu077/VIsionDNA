# VisionDNA AI Pipeline Architecture

VisionDNA implements an end-to-end, real-time computer vision and temporal machine learning pipeline designed for risk prediction and proactive incident prevention.

```
                    ┌─────────────────────────┐
                    │ Camera / Video Ingest   │
                    └────────────┬────────────┘
                                 │ (BGR Frames @ Target FPS)
                                 ▼
                    ┌─────────────────────────┐
                    │ Object & Person Detect  │  (YOLOv8 / YOLO-Pose)
                    └────────────┬────────────┘
                                 │ Detections [BoundingBox, Conf]
                                 ▼
                    ┌─────────────────────────┐
                    │ Multi-Object Tracker    │  (ByteTrack / SORT IoU)
                    └────────────┬────────────┘
                                 │ Persistent Tracks (P001, P002...)
                    ┌────────────┴────────────┐
                    ▼                         ▼
         ┌─────────────────────┐   ┌─────────────────────┐
         │ 33-Keypoint Pose    │   │ Spatial Context     │
         │ MediaPipe / YOLO    │   │ Zones & Objects     │
         └──────────┬──────────┘   └──────────┬──────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Feature Extraction      │  (Position, Velocity, Aspect Ratio,
                    └────────────┬────────────┘   Heading, Temporal Variance)
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Activity Recognition    │  (Temporal GRU / Heuristic)
                    └────────────┬────────────┘   [Standing, Walking, Running,
                                 │                 Sitting, Bending, Falling]
                                 ▼
                    ┌─────────────────────────┐
                    │ Visual Digital Twin     │  (State Engine + Spatial Projection)
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
         ┌─────────────────────┐   ┌─────────────────────┐
         │ Anomaly Detection   │   │ Predictive Engine   │
         │ Rule + Statistical  │   │ Trajectory Horizon  │
         └──────────┬──────────┘   └──────────┬──────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Multi-Factor Risk Engine│  (Normalized Score 0-100 & Explainability)
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Alert & Real-time WS    │  (Broadcast to Dashboard & Operators)
                    └─────────────────────────┘
```

---

## 1. Object Detection (`ai/detection/`)
- **Engine**: Ultralytics YOLOv8 / Pretrained Detectors with CPU/GPU graceful fallback.
- **Classes**: Person (class 0) and contextual objects (machinery, vehicles, hazard stations).
- **Output**: Bounding boxes `(x, y, w, h)`, confidence scores, spatial centers.
- **Performance**: Sub-15ms inference latency on modern GPUs with configurable frame skip.

## 2. Multi-Object Tracking (`ai/tracking/`)
- **Engine**: IoU / SORT tracker assigning persistent IDs (`P001`, `P002`, `P003`).
- **State Buffer**: Maintains bounded historical trajectories (last 30-300 frames) to prevent memory leakage while retaining temporal context.
- **Metrics Tracked**: Center coordinates, velocity history, heading angle, duration of tracking.

## 3. Pose Estimation (`ai/pose/`)
- **Engine**: MediaPipe Pose / YOLO-Pose.
- **Keypoints (33 standard landmarks)**: Nose, shoulders, elbows, wrists, hips, knees, ankles.
- **Derived Metrics**: Center-of-mass vertical displacement, torso inclination angle, joint velocities, ground-plane contact points (feet coordinates).

## 4. Feature Extraction (`ai/features/`)
- **Kinematic Features**:
  - Moving-average velocity vector: $\vec{v} = (\Delta x / \Delta t, \Delta y / \Delta t)$
  - Acceleration & direction angle: $\theta = \text{atan2}(v_y, v_x)$
  - Bounding box aspect ratio ($w/h$) and area rate of change
  - Posture classification (Upright, Bending/Sitting, Lying/Fallen)
  - Distance to nearest restricted zone boundary and monitored hazardous equipment

## 5. Activity Recognition (`ai/activity/`)
- **Model**: Temporal Recurrent Neural Network (PyTorch GRU) operating over sliding temporal windows ($T=30$ frames).
- **Activity Vocabulary**:
  - `standing`
  - `walking`
  - `running`
  - `sitting`
  - `bending`
  - `lying_down`
  - `falling`
- **Output**: Multi-class softmax distribution + confidence score + temporal smoothing filter.

## 6. Real-Time Performance & Edge Deployment
- **Asynchronous Execution**: Decoupled frame ingestion, inference queue, and WebSocket broadcast loops.
- **Target Latency**: $<100\text{ms}$ end-to-end latency at 10-30 FPS.
- **Deployability**: ONNX Runtime and TensorRT ready for NVIDIA Jetson / Edge servers.
