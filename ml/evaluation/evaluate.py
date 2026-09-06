"""
VisionDNA Model Evaluation Pipeline.

Evaluates:
- Multi-class Activity Recognition (Accuracy, Precision, Recall, F1, Confusion Matrix)
- Risk Prediction Performance (Mean Absolute Error, Root Mean Squared Error, R2 Score)
- Inference Latency and Throughput (FPS, ms per sample)
"""

import os
import json
import time
import joblib
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from ml.datasets.adapter import DatasetAdapter, ACTIVITY_CLASSES
from ml.features.temporal_features import extract_temporal_features
from ml.training.train import TemporalActivityGRU


def evaluate_models(model_dir: str = "./ml/models", num_test_samples: int = 500):
    """Run rigorous evaluation and generate comprehensive benchmark report."""
    print("=" * 60)
    print("  VisionDNA AI Model Evaluation & Benchmarking")
    print("=" * 60)

    adapter = DatasetAdapter(sequence_length=30, feature_dim=12)
    X, y_act, y_risk_score, _ = adapter.generate_synthetic_dataset(num_samples=num_test_samples, seed=101)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = {}

    # 1. Activity Model Evaluation
    gru_path = os.path.join(model_dir, "temporal_activity_gru.pt")
    if os.path.exists(gru_path):
        print("\n[1/2] Evaluating Temporal Activity Recognizer...")
        model = TemporalActivityGRU(input_dim=12, hidden_dim=64, num_classes=len(ACTIVITY_CLASSES), num_layers=2).to(device)
        model.load_state_dict(torch.load(gru_path, map_location=device, weights_only=True))
        model.eval()

        # Benchmark latency
        x_tensor = torch.tensor(X, dtype=torch.float32).to(device)
        start_time = time.monotonic()
        with torch.no_grad():
            logits = model(x_tensor)
            preds = torch.argmax(logits, dim=-1).cpu().numpy()
        elapsed_sec = time.monotonic() - start_time
        latency_ms = (elapsed_sec / len(X)) * 1000.0
        fps = len(X) / max(1e-6, elapsed_sec)

        acc = accuracy_score(y_act, preds)
        prec = precision_score(y_act, preds, average="weighted", zero_division=0)
        rec = recall_score(y_act, preds, average="weighted", zero_division=0)
        f1 = f1_score(y_act, preds, average="weighted", zero_division=0)
        cm = confusion_matrix(y_act, preds).tolist()

        results["activity_recognition"] = {
            "model": "TemporalActivityGRU",
            "test_samples": len(X),
            "accuracy": round(float(acc), 4),
            "precision_weighted": round(float(prec), 4),
            "recall_weighted": round(float(rec), 4),
            "f1_score_weighted": round(float(f1), 4),
            "latency_ms_per_inference": round(latency_ms, 3),
            "throughput_fps": round(fps, 1),
            "confusion_matrix": cm,
            "classes": ACTIVITY_CLASSES,
        }

        print(f"  Accuracy:  {acc * 100:.2f}%")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1-Score:  {f1:.4f}")
        print(f"  Latency:   {latency_ms:.2f} ms / sample ({fps:.1f} FPS)")
    else:
        print("\n[1/2] Activity model weights not found. Run train.py first.")
        results["activity_recognition"] = {"status": "Not evaluated yet"}

    # 2. Risk Model Evaluation
    rf_path = os.path.join(model_dir, "risk_regressor_rf.joblib")
    if os.path.exists(rf_path):
        print("\n[2/2] Evaluating Risk Estimation Model...")
        rf_risk = joblib.load(rf_path)

        X_tab = np.array([extract_temporal_features(seq) for seq in X])
        start_time = time.monotonic()
        risk_preds = rf_risk.predict(X_tab)
        elapsed_sec = time.monotonic() - start_time
        latency_ms = (elapsed_sec / len(X)) * 1000.0

        mae = mean_absolute_error(y_risk_score, risk_preds)
        rmse = np.sqrt(mean_squared_error(y_risk_score, risk_preds))
        r2 = r2_score(y_risk_score, risk_preds)

        results["risk_prediction"] = {
            "model": "RandomForestRiskRegressor",
            "test_samples": len(X),
            "mae": round(float(mae), 4),
            "rmse": round(float(rmse), 4),
            "r2_score": round(float(r2), 4),
            "latency_ms_per_inference": round(latency_ms, 3),
        }

        print(f"  Mean Absolute Error (MAE): {mae:.2f} risk points")
        print(f"  Root Mean Squared Error:   {rmse:.2f}")
        print(f"  R2 Score:                  {r2:.4f}")
        print(f"  Latency:                   {latency_ms:.2f} ms / sample")
    else:
        print("\n[2/2] Risk model weights not found. Run train.py first.")
        results["risk_prediction"] = {"status": "Not evaluated yet"}

    eval_file = os.path.join(model_dir, "evaluation_report.json")
    with open(eval_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nEvaluation report saved to: {eval_file}")
    print("=" * 60)
    return results


if __name__ == "__main__":
    evaluate_models()
