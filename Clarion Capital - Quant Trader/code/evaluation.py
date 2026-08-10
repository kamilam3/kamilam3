"""Performance, diagnostics, regime analysis, and paired inference."""

import numpy as np
import pandas as pd

ANNUALIZATION = 252


def max_drawdown(returns: pd.Series) -> float:
    wealth = (1.0 + returns).cumprod()
    return float((wealth / wealth.cummax() - 1.0).min())


def performance_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method in returns:
        series = returns[method]
        annual_return = (1.0 + series).prod() ** (ANNUALIZATION / len(series)) - 1.0
        annual_vol = series.std(ddof=1) * np.sqrt(ANNUALIZATION)
        rows.append({
            "method": method,
            "annual_return": annual_return,
            "annual_volatility": annual_vol,
            "sharpe_zero_rf": annual_return / annual_vol,
            "max_drawdown": max_drawdown(series),
        })
    return pd.DataFrame(rows).set_index("method")


def prediction_diagnostics(result) -> pd.DataFrame:
    records = []
    periods = result.rebalance_periods
    for row in result.predictions.itertuples(index=False):
        period = periods.loc[periods.rebalance_date == row.date].iloc[0]
        realized = result.returns.loc[row.date:period.holding_end, row.method].var(ddof=1)
        record = {
            "date": row.date,
            "method": row.method,
            "predicted_variance": row.predicted_daily_variance,
            "realized_variance": realized,
            "gap": realized - row.predicted_daily_variance,
            "ratio": realized / row.predicted_daily_variance,
        }
        for field in (
            "covariance_condition_number", "shrinkage", "max_weight",
            "effective_n",
        ):
            if hasattr(row, field):
                record[field] = getattr(row, field)
        records.append(record)
    detail = pd.DataFrame(records)
    return detail


def turnover_diagnostics(weights: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    summaries, by_asset = [], []
    for method, frame in weights.items():
        changes = frame.diff().iloc[1:]
        one_way = 0.5 * changes.abs().sum(axis=1)
        summaries.append({
            "method": method,
            "mean_one_way_turnover": one_way.mean(),
            "median_one_way_turnover": one_way.median(),
            "max_one_way_turnover": one_way.max(),
        })
        average_asset_change = changes.abs().mean().sort_values(ascending=False)
        for asset, value in average_asset_change.items():
            by_asset.append({
                "method": method, "asset": asset, "mean_abs_weight_change": value
            })
    return (pd.DataFrame(summaries).set_index("method"),
            pd.DataFrame(by_asset))


def allocation_quality(weights: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize concentration independently of transaction-cost assumptions."""
    rows = []
    for method, frame in weights.items():
        herfindahl = frame.pow(2).sum(axis=1)
        rows.append({
            "method": method,
            "mean_effective_n": (1.0 / herfindahl).mean(),
            "mean_max_weight": frame.max(axis=1).mean(),
            "maximum_weight": frame.max(axis=1).max(),
            "mean_zero_weight_fraction": (frame <= 1e-10).mean(axis=1).mean(),
        })
    return pd.DataFrame(rows).set_index("method")


def rolling_panel_state(panel: pd.DataFrame, window: int = 63) -> pd.DataFrame:
    records = []
    for end in range(window, len(panel) + 1):
        sample = panel.iloc[end-window:end].dropna(axis=1)
        corr = sample.corr().to_numpy()
        upper = corr[np.triu_indices_from(corr, 1)]
        records.append({
            "date": panel.index[end - 1],
            "average_correlation": np.nanmean(upper),
            "average_annualized_volatility":
                sample.std(ddof=1).mean() * np.sqrt(ANNUALIZATION),
        })
    state = pd.DataFrame(records).set_index("date")
    state["joint_stress_score"] = (
        (state.average_correlation - state.average_correlation.median())
        / state.average_correlation.std(ddof=1)
        + (state.average_annualized_volatility -
           state.average_annualized_volatility.median())
        / state.average_annualized_volatility.std(ddof=1)
    )
    return state


def identify_regime(state: pd.DataFrame, duration: int = 63) -> tuple[pd.Timestamp, pd.Timestamp]:
    score = state["joint_stress_score"].rolling(duration).mean()
    end = score.idxmax()
    start_position = state.index.get_loc(end) - duration + 1
    return state.index[max(start_position, 0)], end


def regime_table(result, prediction_detail, start, end) -> pd.DataFrame:
    rows = []
    for method in result.returns:
        subset = result.returns.loc[start:end, method]
        predictions = prediction_detail[
            (prediction_detail.method == method)
            & (prediction_detail.date >= start)
            & (prediction_detail.date <= end)
        ]
        weight_frame = result.weights[method]
        within = weight_frame.loc[(weight_frame.index >= start) & (weight_frame.index <= end)]
        movement = 0.5 * within.diff().abs().sum(axis=1).mean()
        rows.append({
            "method": method,
            "regime_return": (1 + subset).prod() - 1,
            "regime_max_drawdown": max_drawdown(subset),
            "realized_ann_variance": subset.var(ddof=1) * ANNUALIZATION,
            "predicted_ann_variance": predictions.predicted_variance.mean() * ANNUALIZATION,
            "realized_to_predicted": predictions.ratio.mean(),
            "mean_one_way_turnover": movement,
        })
    return pd.DataFrame(rows).set_index("method")


def _moving_block_indices(n: int, block_length: int, rng) -> np.ndarray:
    starts = rng.integers(0, n - block_length + 1,
                          size=int(np.ceil(n / block_length)))
    return np.concatenate([np.arange(s, s + block_length) for s in starts])[:n]


def bootstrap_variance_differences(
    returns: pd.DataFrame,
    benchmark: str = "equal_weight",
    block_length: int = 10,
    replications: int = 5000,
    seed: int = 20260615,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Paired MBB and max-|t| simultaneous CIs versus the benchmark."""
    alternatives = [column for column in returns if column != benchmark]
    observed = np.array([
        ANNUALIZATION * (returns[name].var(ddof=1) -
                         returns[benchmark].var(ddof=1))
        for name in alternatives
    ])
    rng = np.random.default_rng(seed)
    boot = np.empty((replications, len(alternatives)))
    values = returns.to_numpy()
    columns = list(returns.columns)
    bench_pos = columns.index(benchmark)
    alt_positions = [columns.index(name) for name in alternatives]
    for draw in range(replications):
        sample = values[_moving_block_indices(len(values), block_length, rng)]
        boot[draw] = [
            ANNUALIZATION * (np.var(sample[:, pos], ddof=1) -
                             np.var(sample[:, bench_pos], ddof=1))
            for pos in alt_positions
        ]
    centered = boot - observed
    standard_error = centered.std(axis=0, ddof=1)
    max_stat = np.max(np.abs(centered / standard_error), axis=1)
    critical = np.quantile(max_stat, 0.95)
    summary = pd.DataFrame({
        "comparison": [f"{name} minus {benchmark}" for name in alternatives],
        "annual_variance_difference": observed,
        "simultaneous_ci_low": observed - critical * standard_error,
        "simultaneous_ci_high": observed + critical * standard_error,
        "familywise_p_value": [
            np.mean(max_stat >= abs(observed[i] / standard_error[i]))
            for i in range(len(alternatives))
        ],
    }).set_index("comparison")
    draws = pd.DataFrame(boot, columns=alternatives)
    return summary, draws
