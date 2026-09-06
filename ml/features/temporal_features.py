"""
Feature extraction and temporal processing for ML models.
"""

import numpy as np
from typing import Dict, Any, List


def extract_temporal_features(sequence: np.ndarray) -> np.ndarray:
    """
    Extract summary statistical features over a temporal sequence.
    Input shape: (T, feature_dim)
    Returns 1D feature vector of summary statistics (mean, std, min, max, delta).
    """
    means = np.mean(sequence, axis=0)
    stds = np.std(sequence, axis=0)
    mins = np.min(sequence, axis=0)
    maxs = np.max(sequence, axis=0)
    deltas = sequence[-1] - sequence[0]

    return np.concatenate([means, stds, mins, maxs, deltas])


def normalize_sequence(sequence: np.ndarray) -> np.ndarray:
    """Standardize sequence features to zero mean unit variance."""
    mean = np.mean(sequence, axis=0, keepdims=True)
    std = np.std(sequence, axis=0, keepdims=True) + 1e-6
    return (sequence - mean) / std
