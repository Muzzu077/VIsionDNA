# VisionDNA: AI-Based Visual Digital Twin for Predictive Human Activity and Risk Analysis

VisionDNA is a state-of-the-art AI computer vision and biomechanical analysis system that maintains a real-time synchronized **Visual Digital Twin** of detected individuals, classifies human activity, forecasts future spatial trajectories and state transitions, and conducts multi-condition autonomous safety risk evaluations.

---

## 🌐 Quick Access: Next-Gen Web Dashboard

The interactive cyber-futuristic operations command center runs live at:

👉 **[http://localhost:8501](http://localhost:8501)**

---

## 🎨 UI/UX & Visual Design Overhaul

- **Cyber-Futuristic Glassmorphism Command Center**: Dark obsidian backdrop (`#060911`), glowing neon cyan and azure accents, translucent glass cards with dynamic glowing status indicators.
- **Top Mission Control KPI HUD**: Real-time tracked subject count, composite risk meter with severity thresholds, dominant biomechanical motion state with iconography, and pipeline frame rate & latency metrics.
- **Multi-Tab Operational Navigation**:
  1. **🖥️ Operations Matrix**: Side-by-side Live AI Perception Feed and 2D Holographic Digital Twin Blueprint Viewport with live telemetry table and next-state probability forecasts.
  2. **📊 Entity Telemetry**: Deep biomechanical breakdown for each subject (Spine inclination angle, knee/hip flexion, velocity gauge, movement vectors).
  3. **🔮 AI Predictions**: Markovian transition probability matrices, trajectory trend analysis, and projected future coordinates ($T+1.0\text{s}$).
  4. **🛡️ Safety & Incident Log**: Real-time security and hazard audit trail with severity filtering and danger zone rule managers.
  5. **🎮 Scenario Simulator**: Interactive synthetic scenario injection bench (Normal stroll, zone approach, critical fall alarm, collision proximity).
- **Holographic 2D Digital Twin Blueprint Canvas**: Sci-Fi radar range rings, concentric crosshairs, glowing skeleton avatar with joint callout flags, trajectory projection reticles, and glassmorphic telemetry cards.
- **Tactical CV Overlays**: Corner-bracket reticles, multi-color glowing neon skeleton limbs, fading alpha trajectory trails, and caution perimeter zone boundaries.

---

## 🚀 Key Modules & Architecture

1. **Visual Acquisition (`src/camera.py`)**:
   - Live webcams (with Windows DirectShow support), video files, and stylized holographic synthetic stream simulator.
2. **Unified Detection & Pose (`src/detector.py`)**:
   - Single-pass YOLOv8-Pose engine extracting bounding boxes and 17 full-body keypoints simultaneously on CPU.
3. **Persistent Tracking (`src/tracker.py`)**:
   - Jitter deadband filtering, persistent IDs, fading velocity trails, and tactical track badges.
4. **Biomechanical Activity Classifier (`src/activity.py`)**:
   - High-precision classifier: `Standing`, `Walking`, `Sitting`, `Running`, `Bending`, and `Falling`.
5. **Holographic Digital Twin Core (`src/digital_twin.py`)**:
   - Real-time digital replica synchronized with physical position, biomechanical posture, and risk scores.
6. **Predictive Analytics (`src/prediction.py`)**:
   - Markovian transition modeling and velocity vector extrapolation for path forecasting.
7. **Risk Engine (`src/risk_engine.py`)**:
   - Composite 0–100 risk scoring assessing falls, restricted danger zones, collision proximity, and abnormal speed.

---

## 💻 Running the System

### 1. Launch Next-Gen Web Dashboard (Streamlit)
```bash
streamlit run dashboard/dashboard.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

### 2. Launch Standalone Desktop Operations Center (OpenCV)
```bash
python app.py
```

#### ⌨️ Desktop App Hotkeys:
| Key | Action |
|---|---|
| `[TAB]` or `[M]` | Cycle View Mode: **Split Dual-View** ➔ **Perception Only** ➔ **Digital Twin** ➔ **PiP** |
| `[S]` | Toggle Biomechanical Skeleton Overlay |
| `[Z]` | Toggle Restricted Danger Zones |
| `[H]` | Toggle Sci-Fi Top HUD Banner |
| `[Q]` or `[ESC]` | Clean Shutdown |

---

### 3. Run Automated System Tests
```bash
python tests/test_camera.py -1 5
python tests/test_detection.py -1 5
python tests/test_pose.py -1 5
```
