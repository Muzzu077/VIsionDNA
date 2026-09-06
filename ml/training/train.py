"""
VisionDNA Model Training Pipeline.

Trains:
1. PyTorch Temporal GRU/LSTM for Human Activity Recognition (7 classes)
2. RandomForest / GradientBoosting Regressor & Classifier for Risk Scoring
"""

import os
import json
import joblib
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score

from ml.datasets.adapter import DatasetAdapter, ACTIVITY_CLASSES, RISK_CLASSES
from ml.features.temporal_features import extract_temporal_features


class TemporalActivityGRU(nn.Module):
    """Recurrent neural network for multi-timestep human activity recognition."""

    def __init__(self, input_dim: int = 12, hidden_dim: int = 64, num_classes: int = 7, num_layers: int = 2):
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, num_classes),
        )

    def forward(self, x):
        # x: (batch_size, seq_len, input_dim)
        out, _ = self.gru(x)
        # Take final timestep output
        last_step = out[:, -1, :]
        return self.fc(last_step)


def train_models(output_dir: str = "./ml/models", epochs: int = 25, batch_size: int = 32):
    """Execute complete reproducible training pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 60)
    print("  VisionDNA AI / ML Training Pipeline")
    print("=" * 60)

    # 1. Dataset Generation & Splitting
    print("\n[1/4] Loading and preparing temporal dataset...")
    adapter = DatasetAdapter(sequence_length=30, feature_dim=12)
    X, y_act, y_risk_score, y_risk_cls = adapter.generate_synthetic_dataset(num_samples=1400, seed=42)

    X_train, X_test, y_act_train, y_act_test, y_rscore_train, y_rscore_test = train_test_split(
        X, y_act, y_risk_score, test_size=0.2, random_state=42, stratify=y_act
    )

    print(f"  Training set size: {X_train.shape[0]} sequences")
    print(f"  Testing set size:  {X_test.shape[0]} sequences")
    print(f"  Sequence shape:    {X_train.shape[1:]} (T=30, D=12)")

    # 2. Train PyTorch GRU for Activity Recognition
    print("\n[2/4] Training Temporal GRU Activity Recognizer...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Using compute device: {device}")

    model = TemporalActivityGRU(input_dim=12, hidden_dim=64, num_classes=len(ACTIVITY_CLASSES), num_layers=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_act_train, dtype=torch.long))
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * batch_x.size(0)

        if epoch % 5 == 0 or epoch == epochs:
            avg_loss = total_loss / len(train_dataset)
            print(f"  Epoch {epoch:02d}/{epochs:02d} - Loss: {avg_loss:.4f}")

    # Evaluate Activity Model
    model.eval()
    with torch.no_grad():
        test_x_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
        test_logits = model(test_x_tensor)
        preds = torch.argmax(test_logits, dim=-1).cpu().numpy()
        act_acc = float(accuracy_score(y_act_test, preds))
        act_f1 = float(f1_score(y_act_test, preds, average="weighted"))

    print(f"  -> Activity Recognizer Accuracy: {act_acc * 100:.2f}% | F1: {act_f1:.4f}")

    # Save PyTorch Model
    gru_path = os.path.join(output_dir, "temporal_activity_gru.pt")
    torch.save(model.state_dict(), gru_path)
    print(f"  Saved weights to: {gru_path}")

    # 3. Train Tabular Feature Random Forest for Risk Estimation
    print("\n[3/4] Training Multi-Factor Random Forest Risk Regressor...")
    # Extract tabular summary features per sequence
    X_train_tab = np.array([extract_temporal_features(seq) for seq in X_train])
    X_test_tab = np.array([extract_temporal_features(seq) for seq in X_test])

    rf_risk = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    rf_risk.fit(X_train_tab, y_rscore_train)

    rf_preds = rf_risk.predict(X_test_tab)
    mse = float(mean_squared_error(y_rscore_test, rf_preds))
    r2 = float(r2_score(y_rscore_test, rf_preds))

    print(f"  -> Risk Regressor MSE: {mse:.4f} | R2 Score: {r2:.4f}")

    rf_path = os.path.join(output_dir, "risk_regressor_rf.joblib")
    joblib.dump(rf_risk, rf_path)
    print(f"  Saved risk model to: {rf_path}")

    # 4. Save Metrics Metadata
    print("\n[4/4] Writing model metrics report...")
    metrics = {
        "activity_model": {
            "name": "TemporalActivityGRU",
            "version": "1.0.0",
            "classes": ACTIVITY_CLASSES,
            "test_accuracy": round(act_acc, 4),
            "test_f1_weighted": round(act_f1, 4),
            "parameters": sum(p.numel() for p in model.parameters()),
            "input_shape": [1, 30, 12],
        },
        "risk_model": {
            "name": "RandomForestRiskRegressor",
            "version": "1.0.0",
            "test_mse": round(mse, 4),
            "test_r2": round(r2, 4),
            "feature_dim": X_train_tab.shape[1],
        },
    }

    metrics_file = os.path.join(output_dir, "training_metrics.json")
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"  Metrics written to: {metrics_file}")
    print("=" * 60)
    print("  Training Completed Successfully!")
    print("=" * 60)
    return metrics


if __name__ == "__main__":
    train_models()
