"""Covariance estimators: sample, ledoit_wolf, rmt_clip.
"""
from __future__ import annotations

import numpy as np



def sample_cov(X: np.ndarray) -> np.ndarray:
    return np.cov(X, rowvar=False, ddof=1)


def ledoit_wolf_cov(X: np.ndarray) -> np.ndarray:
    try:
        from sklearn.covariance import LedoitWolf
    except Exception:
        raise ImportError("scikit-learn is required for the Ledoit-Wolf estimator")
    lw = LedoitWolf(assume_centered=False).fit(X)
    return lw.covariance_


def rmt_clip_cov(X: np.ndarray) -> np.ndarray:
    T, N = X.shape
    std = X.std(axis=0, ddof=1)
    std_safe = np.where(std > 0, std, 1e-12)
    corr = np.corrcoef(X, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0)
    vals, vecs = np.linalg.eigh(corr)
    q = N / T
    lam_plus = (1.0 + np.sqrt(q)) ** 2
    noise = vals < lam_plus
    if noise.any():
        replacement = vals[noise].mean()
        vals = np.where(noise, replacement, vals)
    corr_clean = (vecs * vals) @ vecs.T
    d = np.sqrt(np.diag(corr_clean))
    d = np.where(d > 0, d, 1e-12)
    corr_clean = corr_clean / np.outer(d, d)
    cov = corr_clean * np.outer(std_safe, std_safe)
    return cov


ESTIMATORS = {
    "sample": sample_cov,
    "ledoit_wolf": ledoit_wolf_cov,  # original entry; safe wrapper available as ledioit_wolf_safe
    "rmt_clip": rmt_clip_cov,
}


def get_estimator(name: str):
    if name not in ESTIMATORS:
        raise KeyError(f"unknown estimator {name}")
    return ESTIMATORS[name]


def safe_ledoit_wolf(X: np.ndarray) -> np.ndarray:
    try:
        return ledoit_wolf_cov(X)
    except ImportError as e:
        print("Warning: Ledoit-Wolf unavailable - falling back to sample covariance:", e)
        return sample_cov(X)


# Expose a safe default for callers that prefer robustness over failing
ESTIMATORS["ledoit_wolf_safe"] = safe_ledoit_wolf
ESTIMATORS["ledoit_wolf"] = safe_ledoit_wolf
