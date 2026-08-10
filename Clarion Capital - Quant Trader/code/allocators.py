"""Long-only portfolio allocation rules used in the bake-off."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

from cov_estimators import get_estimator


def _project_simplex(values: np.ndarray) -> np.ndarray:
    """Euclidean projection onto {w >= 0, sum(w) = 1}."""
    sorted_values = np.sort(values)[::-1]
    cumulative = np.cumsum(sorted_values)
    rho = np.nonzero(sorted_values * np.arange(1, len(values) + 1) >
                     (cumulative - 1.0))[0][-1]
    theta = (cumulative[rho] - 1.0) / (rho + 1.0)
    return np.maximum(values - theta, 0.0)


def sample_covariance(history: pd.DataFrame) -> np.ndarray:
    """Sample covariance with a tiny numerical ridge (not shrinkage)."""
    cov = history.cov().to_numpy()
    scale = np.trace(cov) / len(cov)
    return cov + np.eye(len(cov)) * max(scale * 1e-8, 1e-14)


def oas_covariance(history: pd.DataFrame) -> tuple[np.ndarray, float]:
    """Oracle-approximating shrinkage toward a scaled identity matrix.

    OAS reduces noisy sample eigenvalue dispersion. The intensity is estimated
    analytically from each trailing window, so there is no tuned hyperparameter.
    """
    values = history.to_numpy()
    centered = values - values.mean(axis=0)
    n_observations, n_assets = centered.shape
    empirical = centered.T @ centered / n_observations
    mean_variance = np.trace(empirical) / n_assets
    alpha = np.mean(empirical ** 2)
    denominator = (n_observations + 1.0) * (
        alpha - (mean_variance ** 2) / n_assets
    )
    if denominator <= 0:
        shrinkage = 1.0
    else:
        shrinkage = min((alpha + mean_variance ** 2) / denominator, 1.0)
    covariance = (
        (1.0 - shrinkage) * empirical
        + shrinkage * mean_variance * np.eye(n_assets)
    )
    return covariance, float(shrinkage)


@dataclass
class Allocation:
    weights: pd.Series
    predicted_daily_variance: float
    diagnostics: dict = field(default_factory=dict)


class Allocator(ABC):
    """Common interface for a long-only allocation rule."""

    name: str = "allocator"

    @abstractmethod
    def allocate(self, history: pd.DataFrame) -> Allocation:
        """Return portfolio weights and a variance prediction for the history."""


class EqualWeight(Allocator):
    name = "equal_weight"

    def allocate(self, history: pd.DataFrame) -> Allocation:
        n_assets = history.shape[1]
        weights = np.repeat(1.0 / n_assets, n_assets)
        cov = sample_covariance(history)
        return Allocation(pd.Series(weights, index=history.columns),
                          float(weights @ cov @ weights))


class InverseVolatility(Allocator):
    name = "inverse_volatility"

    def allocate(self, history: pd.DataFrame) -> Allocation:
        vol = history.std(ddof=1).to_numpy()
        inverse = 1.0 / np.maximum(vol, 1e-12)
        weights = inverse / inverse.sum()
        cov = sample_covariance(history)
        return Allocation(pd.Series(weights, index=history.columns),
                          float(weights @ cov @ weights))


class MinimumVariance(Allocator):
    name = "minimum_variance"

    def allocate(self, history: pd.DataFrame) -> Allocation:
        cov = sample_covariance(history)
        return self._solve(history, cov, {"shrinkage": 0.0})

    def _solve(self, history, cov, diagnostics) -> Allocation:
        n_assets = len(cov)
        weights = np.repeat(1.0 / n_assets, n_assets)
        # Projected gradient descent solves the convex long-only problem without
        # requiring a covariance inverse. The ridge only protects arithmetic.
        lipschitz = max(2.0 * np.linalg.eigvalsh(cov).max(), 1e-12)
        step = 1.0 / lipschitz
        for _ in range(10_000):
            updated = _project_simplex(weights - step * (2.0 * cov @ weights))
            if np.max(np.abs(updated - weights)) < 1e-12:
                weights = updated
                break
            weights = updated
        diagnostics = {
            **diagnostics,
            "covariance_condition_number": float(np.linalg.cond(cov)),
            "max_weight": float(weights.max()),
            "effective_n": float(1.0 / np.sum(weights ** 2)),
        }
        return Allocation(
            pd.Series(weights, index=history.columns),
            float(weights @ cov @ weights),
            diagnostics,
        )


class MinimumVarianceParam(MinimumVariance):
    """Long-only minimum-variance with a tunable covariance estimator and ridge."""

    name = "minimum_variance"

    def __init__(self, cov_name: str = "sample", ridge: float = 0.0):
        self.cov_name = cov_name
        self.ridge = ridge

    def allocate(self, history: pd.DataFrame) -> Allocation:
        cov, shrinkage = self._build_covariance(history)
        diagnostics = {"shrinkage": float(shrinkage) if shrinkage is not None else None}
        return self._solve(history, cov, diagnostics)

    def _build_covariance(self, history: pd.DataFrame):
        if self.cov_name == "sample":
            cov = history.cov().to_numpy()
            return cov + np.eye(len(cov)) * self.ridge, 0.0
        if self.cov_name == "oas":
            cov, shrinkage = oas_covariance(history)
            return cov + np.eye(len(cov)) * self.ridge, shrinkage
        estimator = get_estimator(self.cov_name)
        cov = estimator(history.to_numpy())
        return cov + np.eye(len(cov)) * self.ridge, None


class MinimumVarianceOAS(MinimumVariance):
    """Bonus: long-only minimum variance using OAS covariance shrinkage."""

    name = "minimum_variance_oas"

    def allocate(self, history: pd.DataFrame) -> Allocation:
        cov, shrinkage = oas_covariance(history)
        return self._solve(history, cov, {"shrinkage": shrinkage})


CORE_ALLOCATORS = (EqualWeight(), InverseVolatility(), MinimumVariance())
BONUS_ALLOCATORS = CORE_ALLOCATORS + (MinimumVarianceOAS(),)
