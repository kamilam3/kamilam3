"""Figure generation adapted for the `code` pipeline.
Writes PNGs into the provided results/figures/ directory.
"""
from pathlib import Path
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from evaluation import (
    prediction_diagnostics, rolling_panel_state, turnover_diagnostics,
)

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})

LABELS = {
    "equal_weight": "Equal-weight",
    "inverse_volatility": "Inverse-vol",
    "minimum_variance": "Min-variance",
    "minimum_variance_oas": "Min-variance-OAS",
}

COLORS = {k: c for k, c in zip(LABELS.keys(), ["#1b6ca8", "#e08e0b", "#c1272d", "#2a9d8f"]) }


def _ensure_dir(d):
    Path(d).mkdir(parents=True, exist_ok=True)


def _shade_regime(ax, results_dir):
    # try to read regime window from panel_state if available
    pass


def fig_regime(panel: pd.DataFrame, out_dir: Path):
    state = rolling_panel_state(panel)
    fig, ax1 = plt.subplots(figsize=(7.2, 2.8))
    ax1.plot(state.index, state['average_correlation'].values, color="#c1272d", lw=1.1,
             label="avg pairwise corr (63d)")
    ax1.set_ylabel("avg pairwise corr", color="#c1272d")
    ax2 = ax1.twinx()
    ax2.plot(state.index, state['average_annualized_volatility'].values, color="#1b6ca8", lw=1.1,
             label="avg vol (63d, ann.)")
    ax2.set_ylabel("avg ann. vol", color="#1b6ca8")
    ax2.grid(False)
    ax1.axvline(state.index[0], color="black", ls="--", lw=0.9)
    ax1.set_title("Panel regime diagnostic (dashed = calibration/evaluation split)")
    fig.tight_layout()
    fig.savefig(out_dir / "regime.png")
    plt.close(fig)


def fig_cumulative(result, out_dir: Path):
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    returns = result.returns
    for name in returns.columns:
        curve = (1 + returns[name]).cumprod()
        ax.plot(curve.index, curve.values, lw=1.3, label=LABELS.get(name, name), color=COLORS.get(name))
    ax.set_title("Cumulative growth of 1 unit (evaluation segment)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "cumulative.png")
    plt.close(fig)


def fig_realized_vs_predicted(result, out_dir: Path):
    detail = prediction_diagnostics(result)
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    for m in detail['method'].unique():
        sub = detail[detail.method == m].dropna()
        x = pd.to_datetime(sub.date)
        y = np.sqrt(sub.realized_variance * 252) / np.sqrt(sub.predicted_variance * 252)
        ax.plot(x, y, lw=1.8, marker="o", ms=3.5, label=LABELS.get(m, m), color=COLORS.get(m))
    ax.axhline(1.0, color="black", lw=0.9, ls="--")
    ymin, ymax = detail.dropna(subset=['realized_variance', 'predicted_variance']).pipe(
        lambda df: (np.sqrt(df.realized_variance * 252) / np.sqrt(df.predicted_variance * 252)).agg(['min','max'])
    )
    margin = max(0.02, (ymax - ymin) * 0.1)
    ax.set_ylim(max(0.9, ymin - margin), ymax + margin)
    ax.set_title("Realised / predicted volatility per rebalance (>1 = under-predicted risk)")
    ax.set_xlabel("Rebalance date")
    ax.set_ylabel("Realized / predicted vol")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "realized_vs_predicted.png")
    plt.close(fig)


def fig_turnover(result, out_dir: Path):
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    for name, frame in result.weights.items():
        changes = frame.diff().iloc[1:]
        one_way = 0.5 * changes.abs().sum(axis=1)
        ax.plot(one_way.index, one_way.values, lw=1.2, marker="o", ms=2.5, label=LABELS.get(name, name), color=COLORS.get(name))
    ax.set_title("Rebalance-to-rebalance turnover (weight instability)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "turnover.png")
    plt.close(fig)


def fig_weight_dispersion(result, out_dir: Path):
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    names = list(result.weights.keys())
    cols = result.weights[names[0]].columns
    width = 0.27
    x = np.arange(len(cols))
    for i, name in enumerate(names):
        disp = result.weights[name].std(axis=0).reindex(cols)
        ax.bar(x + (i - 1) * width, disp.values, width=width, label=LABELS.get(name, name), color=COLORS.get(name))
    ax.set_xticks(x)
    ax.set_xticklabels([c for c in cols], fontsize=6, rotation=90)
    ax.set_title("Per-stream weight volatility (std across rebalances)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "weight_dispersion.png")
    plt.close(fig)


def fig_minvar_weights(result, out_dir: Path):
    # expects result for min-variance method
    W = result.weights['minimum_variance'].fillna(0.0)
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    im = ax.imshow(W.T.values, aspect="auto", cmap="magma",
                   extent=[0, len(W.index), len(W.columns), 0], vmin=0, vmax=min(1.0, W.values.max()))
    ax.set_yticks(np.arange(len(W.columns)) + 0.5)
    ax.set_yticklabels([c for c in W.columns], fontsize=5)
    ax.set_xticks(np.linspace(0, len(W.index) - 1, 6))
    ax.set_xticklabels([str(d.date()) for d in W.index[np.linspace(0, len(W.index) - 1, 6).astype(int)]], fontsize=6, rotation=30)
    ax.set_title("Minimum-variance: target weights over time (rebalances)")
    fig.colorbar(im, ax=ax, fraction=0.025)
    fig.tight_layout()
    fig.savefig(out_dir / "minvar_weights.png")
    plt.close(fig)


def fig_bootstrap(inference, out_dir: Path):
    # inference: DataFrame or dict-like with sharpe/bootstrap results
    # Here expect inference as DataFrame with comparison index like in code
    # For a simple visualization, plot familywise CI for variance comparisons if available
    try:
        fig, ax = plt.subplots(figsize=(7.2, 2.4))
        # inference expected to be DataFrame with columns 'annual_variance_difference','simultaneous_ci_low','simultaneous_ci_high'
        comps = inference.reset_index()
        y = np.arange(len(comps))
        gaps = comps['annual_variance_difference'].values
        lo = comps['simultaneous_ci_low'].values
        hi = comps['simultaneous_ci_high'].values
        ax.errorbar(gaps, y, xerr=[gaps - lo, hi - gaps], fmt='o', color='#c1272d', capsize=4)
        ax.axvline(0.0, color='black', lw=0.9, ls='--')
        ax.set_yticks(y)
        ax.set_yticklabels(comps['comparison'].values)
        ax.set_title('Annual variance gap vs EqualWeight with simultaneous 95% CI')
        fig.tight_layout()
        fig.savefig(out_dir / 'bootstrap_variance.png')
        plt.close(fig)
    except Exception:
        pass


def make_all(panel, result, inference, out_dir_base):
    out_dir = Path(out_dir_base) / 'figures'
    _ensure_dir(out_dir)
    fig_regime(panel, out_dir)
    fig_cumulative(result, out_dir)
    fig_realized_vs_predicted(result, out_dir)
    fig_turnover(result, out_dir)
    fig_weight_dispersion(result, out_dir)
    try:
        fig_minvar_weights(result, out_dir)
    except Exception:
        pass
    try:
        fig_bootstrap(inference, out_dir)
    except Exception:
        pass
