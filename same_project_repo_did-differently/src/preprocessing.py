"""
Module: preprocessing.py
Handles image preprocessing for facial emotion recognition models.
Includes resizing, grayscale conversion, normalization, and tensor shape formatting.
"""

import cv2
import numpy as np
from typing import Tuple, Union


def preprocess_face_for_model(
    face_img: np.ndarray,
    target_size: Tuple[int, int] = (64, 64),
    normalize_type: str = "raw_float32",
) -> np.ndarray:
    """
    Preprocess a cropped face image to match the neural network's expected input.

    Args:
        face_img: Cropped face ROI (numpy ndarray, BGR or Grayscale)
        target_size: Desired (width, height) tuple. Default: (64, 64) for FERPlus ONNX
        normalize_type:
            - "raw_float32": Cast to float32 (values 0.0 - 255.0) as expected by FERPlus ONNX
            - "zero_to_one": Scale pixel values to range [0.0, 1.0]
            - "minus_one_to_one": Scale pixel values to range [-1.0, 1.0]

    Returns:
        Preprocessed numpy array of shape (1, 1, height, width) with float32 dtype
    """
    if face_img is None or face_img.size == 0:
        raise ValueError("Cannot preprocess an empty face image.")

    # 1. Convert to Grayscale if 3-channel BGR
    if len(face_img.shape) == 3:
        if face_img.shape[2] == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        elif face_img.shape[2] == 4:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGRA2GRAY)
        else:
            gray = face_img[:, :, 0]
    else:
        gray = face_img

    # 2. Resize to model's expected input dimensions
    target_w, target_h = target_size
    h_curr, w_curr = gray.shape[:2]

    # Select interpolation based on downsampling vs upsampling
    if target_w < w_curr or target_h < h_curr:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_LINEAR

    resized = cv2.resize(gray, (target_w, target_h), interpolation=interpolation)

    # 3. Normalization
    img_float = resized.astype(np.float32)

    if normalize_type == "raw_float32":
        normalized = img_float
    elif normalize_type == "zero_to_one":
        normalized = img_float / 255.0
    elif normalize_type == "minus_one_to_one":
        normalized = (img_float / 127.5) - 1.0
    else:
        normalized = img_float

    # 4. Format tensor dimensions for ONNX / CNN: (Batch, Channel, Height, Width) -> (1, 1, H, W)
    tensor = np.expand_dims(normalized, axis=0)  # (1, H, W)
    tensor = np.expand_dims(tensor, axis=0)      # (1, 1, H, W)

    return tensor


def compute_softmax(logits: np.ndarray) -> np.ndarray:
    """
    Computes numerically stable softmax probabilities from raw model logits.
    """
    flat = logits.flatten()
    shifted = flat - np.max(flat)
    exp_scores = np.exp(shifted)
    probs = exp_scores / np.sum(exp_scores)
    return probs
