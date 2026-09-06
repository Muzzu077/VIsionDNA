"""
VisionDNA Model Export & Optimization Pipeline.

Exports trained models to:
- PyTorch TorchScript format (.pt)
- Open Neural Network Exchange (ONNX) format (.onnx) for low-latency Edge inference
"""

import os
import torch
from ml.training.train import TemporalActivityGRU


def export_models(model_dir: str = "./ml/models"):
    """Export PyTorch models to TorchScript and ONNX formats."""
    print("=" * 60)
    print("  VisionDNA Model Export Pipeline")
    print("=" * 60)

    gru_weights = os.path.join(model_dir, "temporal_activity_gru.pt")
    if not os.path.exists(gru_weights):
        print(f"Model weights not found at {gru_weights}. Run train.py first.")
        return

    # Load model
    model = TemporalActivityGRU(input_dim=12, hidden_dim=64, num_classes=7, num_layers=2)
    model.load_state_dict(torch.load(gru_weights, map_location="cpu", weights_only=True))
    model.eval()

    dummy_input = torch.randn(1, 30, 12, dtype=torch.float32)

    # 1. Export to TorchScript
    ts_path = os.path.join(model_dir, "temporal_activity_gru_torchscript.pt")
    traced_model = torch.jit.trace(model, dummy_input)
    traced_model.save(ts_path)
    print(f"[1/2] Successfully exported TorchScript model to: {ts_path}")

    # 2. Export to ONNX
    onnx_path = os.path.join(model_dir, "temporal_activity_gru.onnx")
    try:
        torch.onnx.export(
            model,
            dummy_input,
            onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["sequence_features"],
            output_names=["activity_logits"],
            dynamic_axes={
                "sequence_features": {0: "batch_size", 1: "sequence_length"},
                "activity_logits": {0: "batch_size"},
            },
        )
        print(f"[2/2] Successfully exported ONNX model to: {onnx_path}")
    except Exception as exc:
        print(f"[2/2] Note: ONNX export skipped: {exc}")

    print("=" * 60)
    print("  Export Completed!")
    print("=" * 60)


if __name__ == "__main__":
    export_models()
