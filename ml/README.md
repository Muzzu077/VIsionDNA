# 🤖 VisionDNA Machine Learning Pipeline

> **Notice:** This document is a stub for the ML pipeline. It provides a blueprint for the internal lifecycle of model research, dataset management, training, and deployment within VisionDNA.

This directory (`/ml`) serves as the nexus for custom AI model training. While VisionDNA leverages powerful foundation models (like YOLO and MediaPipe) out-of-the-box, fine-tuning for specific enterprise environments constitutes a required workflow. 

---

## 1. 🗂 Datasets
**Location:** `/ml/datasets` *(Not tracked by git due to size)*

Data is organized using a standardized taxonomy for Object Detection and Pose Estimation tasks.

### Structure:
```text
/datasets
  ├── /raw                  # Unprocessed videos and images
  ├── /annotations          # Ground-truth XML/JSON/YOLO formatted labels
  └── /processed            # Balanced, tokenized, and resized sets ready for loaders
      ├── /train
      ├── /val
      └── /test
```
**Labeling Tool:** We recommend utilizing *Roboflow* or *CVAT* for generating annotation sets, exporting them directly into YOLO PyTorch `.txt` formats.

---

## 2. 🧹 Preprocessing
**Script:** `scripts/preprocess_pipeline.py` (To Be Implemented)

**Routine tasks involve:**
*   **Frame Extraction:** Converting raw footage into discrete imagery.
*   **Data Augmentation:** Utilizing `albumentations` for variations in lighting, rotation, noise, and occlusion. This ensures generalization across different warehouse or retail lighting conditions.
*   **Normalization:** Ensuring input tensors map strictly efficiently to `[0, 1]` or `-1 to 1`.

---

## 3. 🏋️ Training Loop
**Environment:** Requires PyTorch, CUDA, and CuDNN.

We plan to construct extensible PyTorch Lightning modules to standardize training sweeps.

*   `train_detector.py`: Fine-tunes the base YOLOv10 weights on our custom domain dataset.
*   `train_action.py`: Trains the Spatio-Temporal Graph Convolutional Network (ST-GCN) on synthesized skeleton sequences.

hyperparameter sweeps will be managed using **Weights & Biases (W&B)** integration.

---

## 4. 📈 Evaluation
**Metrics tracked:**
*   **mAP50-95:** Mean Average Precision (Detection).
*   **MOTA / IDF1:** Multi-Object Tracking Accuracy (Tracking).
*   **F1-Score / Confusion Matrices:** Activity recognition classifications.

Scripts in `/scripts/eval.py` will generate automated benchmark reports before any model is approved for export.

---

## 5. 🚀 Export & Optimization
To satisfy VisionDNA's ultra-low latency requirements, trained `.pt` or `.pth` weights are strictly prohibited in the production environment. 

All finalized models must be compiled:
1. Export to ONNX (`.onnx`).
2. Optimize with NVIDIA TensorRT (`.engine`), quantifying models implicitly to INT8 or FP16 for maximum runtime throughput on Edge GPUs.

*Documentation mapping out specific hyperparameter guidelines and training methodologies will be expanded in future releases.*