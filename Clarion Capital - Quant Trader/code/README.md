# The Burden of Proof

Reproducible walk-forward comparison of equal-weight, inverse-volatility, and
long-only minimum-variance allocations on the supplied strategy panel.

## Quick start

From this directory, create and activate a virtual environment, install the
requirements, and run the analysis:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_analysis.py
```

For a packaged install, the repository also supports:

```bash
pip install -e .
burden-of-proof
```

The script reads the panel from `burden_of_proof_data/burden_of_proof_panel.csv`
and writes the generated tables, daily portfolio returns, weights, variance
predictions, bootstrap draws, and figures to `results/`.

## What the repository actually does

- The backtest starts on 2023-07-03 and runs through 2025-06-20.
- The default implementation uses a 126-day trailing estimation window.
- By default, weights are refreshed on the first observed business day of each
  month.
- The core methods are equal-weight, inverse-volatility, and long-only
  minimum variance.
- A bonus minimum-variance allocator using OAS covariance shrinkage is also
  evaluated and written to the bonus output files.

## Design summary

- Primary criterion: lowest realized annualized variance over the evaluation
  period. Return, Sharpe ratio, and drawdown are reported as descriptive
  secondary outcomes.
- Inference: paired 10-day moving-block bootstrap with 10,000 resamples and
  simultaneous 95% confidence intervals for the relevant method-vs-equal-weight
  comparisons.
- Minimum variance: convex long-only simplex optimization solved by projected
  gradient descent. The implementation uses covariance estimates plus a small
  numerical ridge for numerical stability.
- Missing-data rule: an asset must have a return on the rebalance date and a
  complete trailing estimation window to be eligible for the next allocation.

## Notes on calibration and locking

If the files `results/top_candidates_evaluation.json` or
`results/calibration_grid_results.csv` already exist, the analysis script uses
that stored candidate to lock the minimum-variance configuration for the main
run. In the current repository state, that means the script uses the locked
candidate with a 126-day window, 21 trading-day rebalance cadence, the
Ledoit-Wolf covariance estimator, and a $1 \times 10^{-6}$ ridge.

## Repository structure

- `allocators.py`: allocation rules and covariance estimates; adding another allocator is as simple as implementing `allocate()` and adding it to the allocator tuple
- `backtest.py`: strict no-lookahead walk-forward engine
- `evaluation.py`: performance metrics, diagnostics, regime analysis, and
  inference
- `run_analysis.py`: one-command orchestration
- `tune_and_evaluate.py`: grid-search calibration and candidate evaluation
- `final_assignment.ipynb`: narrative companion notebook

No expected-return estimates, leverage, short positions, transaction-cost
assumptions, or external data are used.
