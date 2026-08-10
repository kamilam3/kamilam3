"""Strict walk-forward portfolio backtest."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    returns: pd.DataFrame
    weights: dict[str, pd.DataFrame]
    predictions: pd.DataFrame
    rebalance_periods: pd.DataFrame


def run_walk_forward(
    returns: pd.DataFrame,
    allocators,
    evaluation_start: pd.Timestamp,
    window: int = 126,
    rebalance_every=None,
) -> BacktestResult:
    """Run a no-lookahead backtest.

    By default weights are refreshed on the first observed day of each month.
    If ``rebalance_every`` is supplied, they are refreshed every N observed
    trading days, starting on the evaluation boundary.
    """
    evaluation = returns.loc[evaluation_start:]
    if rebalance_every is None:
        month = evaluation.index.to_period("M")
        rebalance_dates = evaluation.groupby(month).apply(lambda x: x.index[0])
    else:
        if rebalance_every < 1:
            raise ValueError("rebalance_every must be a positive integer")
        rebalance_dates = pd.Series(
            evaluation.index[::rebalance_every],
            index=range(len(evaluation.index[::rebalance_every])),
        )

    portfolio_returns = {
        allocator.name: pd.Series(index=evaluation.index, dtype=float)
        for allocator in allocators
    }
    weight_records = {allocator.name: [] for allocator in allocators}
    prediction_records = []
    periods = []

    all_columns = returns.columns
    for position, rebalance_date in enumerate(rebalance_dates):
        next_date = (rebalance_dates.iloc[position + 1]
                     if position + 1 < len(rebalance_dates) else None)
        holding_dates = evaluation.loc[
            rebalance_date: (next_date - pd.Timedelta(days=1)
                             if next_date is not None else evaluation.index[-1])
        ].index
        prior = returns.loc[returns.index < rebalance_date].tail(window)
        # An existing stream must have a return on the rebalance date. A full
        # estimation window avoids silently changing information quality.
        available = evaluation.loc[rebalance_date].notna()
        eligible = list(all_columns[available & prior.notna().all(axis=0)])
        if not eligible:
            raise RuntimeError(f"No eligible strategies on {rebalance_date}")
        history = prior[eligible]
        periods.append({
            "rebalance_date": rebalance_date,
            "holding_end": holding_dates[-1],
            "n_assets": len(eligible),
        })

        for allocator in allocators:
            allocation = allocator.allocate(history)
            full_weights = pd.Series(0.0, index=all_columns, name=rebalance_date)
            full_weights.loc[eligible] = allocation.weights
            weight_records[allocator.name].append(full_weights)
            prediction_records.append({
                "date": rebalance_date,
                "method": allocator.name,
                "predicted_daily_variance": allocation.predicted_daily_variance,
                **allocation.diagnostics,
            })
            holding = evaluation.loc[holding_dates, eligible]
            if holding.isna().any().any():
                raise RuntimeError("A strategy disappeared during a holding month")
            portfolio_returns[allocator.name].loc[holding_dates] = (
                holding @ allocation.weights
            )

    return BacktestResult(
        returns=pd.DataFrame(portfolio_returns),
        weights={
            name: pd.DataFrame(rows) for name, rows in weight_records.items()
        },
        predictions=pd.DataFrame(prediction_records),
        rebalance_periods=pd.DataFrame(periods),
    )
