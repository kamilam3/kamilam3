"""One-command reproduction of the complete Burden of Proof submission."""

from pathlib import Path
import pandas as pd

from allocators import BONUS_ALLOCATORS, CORE_ALLOCATORS, EqualWeight, InverseVolatility, MinimumVarianceParam
from backtest import run_walk_forward
from evaluation import (
    allocation_quality, bootstrap_variance_differences, identify_regime, performance_table,
    prediction_diagnostics, regime_table, rolling_panel_state,
    turnover_diagnostics,
)
import figures

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "burden_of_proof_data" / "burden_of_proof_panel.csv"
RESULTS = ROOT / "results"
EVALUATION_START = pd.Timestamp("2023-07-03")
WINDOW = 126


def load_locked_candidate():
    json_path = RESULTS / "top_candidates_evaluation.json"
    csv_path = RESULTS / "calibration_grid_results.csv"
    if json_path.exists():
        import json
        with open(json_path, "r") as f:
            top_candidates = json.load(f)
        if top_candidates:
            candidate = top_candidates[0]
            return {
                "window": int(candidate["window"]),
                "rebalance": int(candidate["rebalance"]),
                "cov": str(candidate["cov"]),
                "ridge": float(candidate["ridge"]),
            }
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        if not df.empty:
            row = df.iloc[0]
            return {
                "window": int(row["window"]),
                "rebalance": int(row["rebalance"]),
                "cov": str(row["cov"]),
                "ridge": float(row["ridge"]),
            }
    return None


def main():
    RESULTS.mkdir(exist_ok=True)
    panel = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()

    locked_candidate = load_locked_candidate()
    if locked_candidate is not None:
        core_allocators = (
            EqualWeight(),
            InverseVolatility(),
            MinimumVarianceParam(
                locked_candidate["cov"], locked_candidate["ridge"]
            ),
        )
        window = locked_candidate["window"]
        rebalance_every = locked_candidate["rebalance"]
        print(
            "Using locked calibration candidate:",
            locked_candidate,
        )
    else:
        core_allocators = CORE_ALLOCATORS
        window = WINDOW
        rebalance_every = None

    result = run_walk_forward(
        panel, core_allocators, EVALUATION_START, window, rebalance_every
    )
    bonus_result = run_walk_forward(
        panel, BONUS_ALLOCATORS, EVALUATION_START, window, rebalance_every
    )

    performance = performance_table(result.returns)
    prediction_detail = prediction_diagnostics(result)
    prediction_summary = prediction_detail.groupby("method").agg(
        mean_predicted_daily_variance=("predicted_variance", "mean"),
        mean_realized_daily_variance=("realized_variance", "mean"),
        mean_gap=("gap", "mean"),
        mean_realized_to_predicted=("ratio", "mean"),
        median_realized_to_predicted=("ratio", "median"),
    )
    prediction_summary["aggregate_realized_to_predicted"] = (
        prediction_summary["mean_realized_daily_variance"]
        / prediction_summary["mean_predicted_daily_variance"]
    )
    prediction_summary["annualized_mean_gap"] = (
        prediction_summary["mean_gap"] * 252
    )
    turnover, turnover_by_asset = turnover_diagnostics(result.weights)
    quality = allocation_quality(result.weights)
    state = rolling_panel_state(panel.loc[EVALUATION_START:])
    regime_start, regime_end = identify_regime(state)
    regime = regime_table(result, prediction_detail, regime_start, regime_end)
    inference, draws = bootstrap_variance_differences(
        result.returns, block_length=10, replications=10_000
    )
    bonus_performance = performance_table(bonus_result.returns)
    bonus_prediction_detail = prediction_diagnostics(bonus_result)
    bonus_prediction_summary = bonus_prediction_detail.groupby("method").agg(
        mean_predicted_daily_variance=("predicted_variance", "mean"),
        mean_realized_daily_variance=("realized_variance", "mean"),
    )
    bonus_prediction_summary["aggregate_realized_to_predicted"] = (
        bonus_prediction_summary.mean_realized_daily_variance
        / bonus_prediction_summary.mean_predicted_daily_variance
    )
    bonus_turnover, _ = turnover_diagnostics(bonus_result.weights)
    bonus_quality = allocation_quality(bonus_result.weights)
    bonus_inference, bonus_draws = bootstrap_variance_differences(
        bonus_result.returns, block_length=10, replications=10_000
    )
    block_sensitivity_rows = []
    for block_length in (5, 10, 21):
        block_inference, _ = bootstrap_variance_differences(
            result.returns, block_length=block_length, replications=10_000,
            seed=20260615,
        )
        block_inference = block_inference.reset_index()
        block_inference.insert(0, "block_length", block_length)
        block_sensitivity_rows.append(block_inference)
    block_sensitivity = pd.concat(block_sensitivity_rows, ignore_index=True)
    frequency_rows = []
    for frequency in (5, 10, 21):
        frequency_result = run_walk_forward(
            panel, CORE_ALLOCATORS, EVALUATION_START, WINDOW,
            rebalance_every=frequency,
        )
        frequency_performance = performance_table(frequency_result.returns)
        frequency_turnover, _ = turnover_diagnostics(frequency_result.weights)
        frequency_inference, _ = bootstrap_variance_differences(
            frequency_result.returns, block_length=10, replications=10_000,
            seed=20260615,
        )
        for method in frequency_performance.index:
            comparison = f"{method} minus equal_weight"
            frequency_rows.append({
                "rebalance_every_trading_days": frequency,
                "method": method,
                "annual_return": frequency_performance.loc[
                    method, "annual_return"
                ],
                "annual_volatility": frequency_performance.loc[
                    method, "annual_volatility"
                ],
                "sharpe_zero_rf": frequency_performance.loc[
                    method, "sharpe_zero_rf"
                ],
                "max_drawdown": frequency_performance.loc[
                    method, "max_drawdown"
                ],
                "mean_one_way_weight_change_per_rebalance":
                    frequency_turnover.loc[method, "mean_one_way_turnover"],
                "approximate_one_way_weight_change_per_year": (
                    frequency_turnover.loc[method, "mean_one_way_turnover"]
                    * 252 / frequency
                ),
                "annual_variance_difference_vs_equal_weight": (
                    0.0 if method == "equal_weight"
                    else frequency_inference.loc[
                        comparison, "annual_variance_difference"
                    ]
                ),
                "simultaneous_ci_low": (
                    0.0 if method == "equal_weight"
                    else frequency_inference.loc[
                        comparison, "simultaneous_ci_low"
                    ]
                ),
                "simultaneous_ci_high": (
                    0.0 if method == "equal_weight"
                    else frequency_inference.loc[
                        comparison, "simultaneous_ci_high"
                    ]
                ),
                "familywise_p_value": (
                    1.0 if method == "equal_weight"
                    else frequency_inference.loc[
                        comparison, "familywise_p_value"
                    ]
                ),
            })
    frequency_sensitivity = pd.DataFrame(frequency_rows)
    sensitivity_rows = []
    for alternate_start in (pd.Timestamp("2023-01-02"), pd.Timestamp("2024-01-02")):
        alternate = run_walk_forward(panel, CORE_ALLOCATORS, alternate_start, WINDOW)
        alternate_performance = performance_table(alternate.returns)
        alternate_inference, _ = bootstrap_variance_differences(
            alternate.returns, replications=2000, seed=20260615
        )
        for method in alternate_performance.index:
            comparison = f"{method} minus equal_weight"
            significance = (
                False if method == "equal_weight"
                else not (
                    alternate_inference.loc[comparison, "simultaneous_ci_low"] <= 0
                    <= alternate_inference.loc[comparison, "simultaneous_ci_high"]
                )
            )
            sensitivity_rows.append({
                "evaluation_start": alternate_start,
                "method": method,
                "annual_volatility": alternate_performance.loc[
                    method, "annual_volatility"
                ],
                "variance_difference_vs_equal_weight": (
                    0.0 if method == "equal_weight"
                    else alternate_inference.loc[
                        comparison, "annual_variance_difference"
                    ]
                ),
                "simultaneously_significant": significance,
            })
    sensitivity = pd.DataFrame(sensitivity_rows)

    performance.to_csv(RESULTS / "performance.csv")
    result.returns.to_csv(RESULTS / "portfolio_returns.csv")
    result.predictions.to_csv(RESULTS / "predicted_variance.csv", index=False)
    prediction_detail.to_csv(RESULTS / "prediction_detail.csv", index=False)
    prediction_summary.to_csv(RESULTS / "prediction_summary.csv")
    turnover.to_csv(RESULTS / "weight_stability.csv")
    weight_stability = pd.read_csv(RESULTS / "weight_stability.csv", index_col=0)
    print("\nweight_stability.csv\n", weight_stability.to_string(float_format=lambda x: f"{x:.4f}"))
    quality.to_csv(RESULTS / "allocation_quality.csv")
    turnover_by_asset.to_csv(RESULTS / "weight_stability_by_asset.csv", index=False)
    state.to_csv(RESULTS / "panel_state.csv")
    regime.to_csv(RESULTS / "regime.csv")
    inference.to_csv(RESULTS / "inference.csv")
    block_sensitivity.to_csv(RESULTS / "block_length_sensitivity.csv", index=False)
    frequency_sensitivity.to_csv(
        RESULTS / "rebalance_frequency_sensitivity.csv", index=False
    )
    sensitivity.to_csv(RESULTS / "split_sensitivity.csv", index=False)
    draws.to_csv(RESULTS / "bootstrap_draws.csv", index=False)
    bonus_performance.to_csv(RESULTS / "bonus_performance.csv")
    bonus_prediction_detail.to_csv(
        RESULTS / "bonus_prediction_detail.csv", index=False
    )
    bonus_prediction_summary.to_csv(RESULTS / "bonus_prediction_summary.csv")
    bonus_turnover.to_csv(RESULTS / "bonus_weight_stability.csv")
    bonus_quality.to_csv(RESULTS / "bonus_allocation_quality.csv")
    bonus_inference.to_csv(RESULTS / "bonus_inference.csv")
    bonus_draws.to_csv(RESULTS / "bonus_bootstrap_draws.csv", index=False)
    bonus_result.weights["minimum_variance_oas"].to_csv(
        RESULTS / "weights_minimum_variance_oas.csv"
    )
    for name, frame in result.weights.items():
        frame.to_csv(RESULTS / f"weights_{name}.csv")

    # Print selected CSV outputs for quick inspection
    csvs_to_show = [
        "weight_stability.csv",
        "prediction_summary.csv",
        "inference.csv",
        "block_length_sensitivity.csv",
        "rebalance_frequency_sensitivity.csv",
        "split_sensitivity.csv",
    ]
    for fname in csvs_to_show:
        path = RESULTS / fname
        if path.exists():
            try:
                df_print = pd.read_csv(path)
                print(f"\n{fname}\n", df_print.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
            except Exception as e:
                print(f"Could not read {fname}:", e)

    # Generate figures used by the report (PNG files in results/figures/)
    try:
        figures.make_all(panel, result, inference, RESULTS)
    except Exception as e:
        print("Warning: figure generation failed:", e)

    print(f"Evaluation: {result.returns.index.min().date()} to "
          f"{result.returns.index.max().date()} ({len(result.returns)} days)")
    print(f"Stress regime: {regime_start.date()} to {regime_end.date()}")
    print("\nPerformance\n", performance.to_string(float_format=lambda x: f"{x:.4f}"))
    print("\nPrediction diagnostics\n",
          prediction_summary.to_string(float_format=lambda x: f"{x:.4f}"))
    print("\nWeight stability\n", turnover.to_string(float_format=lambda x: f"{x:.4f}"))
    print("\nStress regime\n", regime.to_string(float_format=lambda x: f"{x:.4f}"))
    print("\nSimultaneous inference\n",
          inference.to_string(float_format=lambda x: f"{x:.6f}"))


if __name__ == "__main__":
    main()
