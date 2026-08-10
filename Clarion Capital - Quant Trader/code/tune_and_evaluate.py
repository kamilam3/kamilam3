"""Grid search on calibration and locked-in evaluation for top candidates."""
from pathlib import Path
import itertools
import pandas as pd
import numpy as np
import json
import math

from backtest import run_walk_forward
from evaluation import performance_table, bootstrap_variance_differences, prediction_diagnostics
from allocators import Allocation, EqualWeight, InverseVolatility, MinimumVarianceParam
from cov_estimators import get_estimator

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "burden_of_proof_data" / "burden_of_proof_panel.csv"
RESULTS = ROOT / "results"

# Pre-registered evaluation boundary in this code base
from run_analysis import EVALUATION_START

# Grid
WINDOWS = [63, 126, 252]
REBALANCES = [5, 10, 21]
COVS = ["sample", "oas", "ledoit_wolf", "rmt_clip"]
RIDGES = [1e-12, 1e-10, 1e-8, 1e-6]
BLOCKS = [5, 10, 21]

# Note: oas is implemented in allocators as oas_covariance(history) returning (cov, shrinkage).
# For ledoit_wolf and rmt_clip we use get_estimator.

def run_grid():
    panel = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
    calib_end = pd.to_datetime(EVALUATION_START) - pd.Timedelta(days=1)
    calib = panel.loc[:calib_end]

    rows = []
    combos = list(itertools.product(WINDOWS, REBALANCES, COVS, RIDGES))
    print(f"Running {len(combos)} candidates on calibration segment...")
    for (window, rebalance, cov, ridge) in combos:
        # need at least window+1 rows
        if len(calib) < window + 5:
            continue
        eval_start = calib.index[window]
        allocators = (EqualWeight(), InverseVolatility(), MinimumVarianceParam(cov, ridge))
        try:
            res = run_walk_forward(calib, allocators, eval_start, window, rebalance)
        except Exception as e:
            print("candidate failed", (window, rebalance, cov, ridge), e)
            continue
        perf = performance_table(res.returns)
        # pick min-variance row
        mv_vol = perf.loc['minimum_variance', 'annual_volatility'] if 'minimum_variance' in perf.index else None
        # turnover
        turnovers, _ = None, None
        try:
            from evaluation import turnover_diagnostics
            turnovers, by_asset = turnover_diagnostics(res.weights)
        except Exception:
            turnovers = None
        rows.append({
            'window': window, 'rebalance': rebalance, 'cov': cov, 'ridge': ridge,
            'mv_ann_vol': mv_vol,
            'mean_turnover': turnovers.loc['minimum_variance','mean_one_way_turnover'] if turnovers is not None and 'minimum_variance' in turnovers.index else None,
        })
    df = pd.DataFrame(rows)
    df = df.sort_values('mv_ann_vol')
    df.to_csv(RESULTS / 'calibration_grid_results.csv', index=False)
    print('Saved calibration_grid_results.csv')
    return df


def evaluate_candidates(df, topk=2):
    panel = pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()
    # pick topk
    picks = df.head(topk)
    eval_rows = []
    for _, row in picks.iterrows():
        window = int(row['window']); rebalance = int(row['rebalance']); cov = str(row['cov']); ridge = float(row['ridge'])
        allocators = (EqualWeight(), InverseVolatility(), MinimumVarianceParam(cov, ridge))
        res = run_walk_forward(panel, allocators, pd.to_datetime(EVALUATION_START), window, rebalance)
        perf = performance_table(res.returns)
        pred_detail = prediction_diagnostics(res)
        # bootstrap sensitivity for blocks
        block_rows = []
        for block in BLOCKS:
            inf, draws = bootstrap_variance_differences(res.returns, block_length=block, replications=2000)
            # capture min-variance comparison row
            try:
                comp = inf.loc['minimum_variance minus equal_weight']
                block_rows.append({'block': block, 'annual_variance_difference': comp.annual_variance_difference,
                                   'ci_low': comp.simultaneous_ci_low, 'ci_high': comp.simultaneous_ci_high,
                                   'fw_p': comp.familywise_p_value})
            except Exception:
                pass
        eval_rows.append({'window': window, 'rebalance': rebalance, 'cov': cov, 'ridge': ridge,
                          'performance': perf.to_dict(), 'prediction_summary': pred_detail.to_dict(),
                          'block_sensitivity': block_rows})
    # save
    with open(RESULTS / 'top_candidates_evaluation.json', 'w') as f:
        json.dump(eval_rows, f, default=str)
    print('Saved top_candidates_evaluation.json')
    return eval_rows


if __name__ == '__main__':
    df = run_grid()
    evaluate_candidates(df, topk=2)
