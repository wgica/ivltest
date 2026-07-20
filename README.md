# IVL League Prediction (ivltest)

Monte Carlo simulator for predicting final standings of the IVL league. It uses a Poisson-based round model to simulate best-of-3 matches for the remaining schedule, aggregates many trials, and outputs probability distributions and a visual HTML report.

## Features

- Precompute per-match outcome distributions (based on team stats)
- Fast Monte Carlo simulation using Numba (ivl_merged.py)
- Generates a self-contained HTML report (ivl_prediction_report.html)
- Simple, older pure-Python variant available (ivl.py)

## Requirements

- Python 3.8+
- numpy
- numba

Optional / notes:
- predict_round.py imports `ti_math.eval_ti` to compute factorials; the repository currently does not include `ti_math.py`. If you don't have that module, replace `eval_ti(str(k)+"!")` with `math.factorial(k)` in `predict_round.py` or provide `ti_math.py` that exposes `eval_ti`.

## Installation

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
.\.venv\Scripts\activate # Windows
```

2. Install dependencies:

```bash
pip install numpy numba
```

## Files of interest

- `ivl_merged.py` — main CLI: reads `stats.txt`, `remaining_matches.txt`, prompts (or loads) current standings, runs Monte Carlo, writes `ivl_prediction_report.html`.
- `ivl.py` — compact/older script version (pure Python, smaller simulation flow).
- `predict_bo3.py`, `predict_round.py` — probability model helpers.
- `stats.txt` — team statistics used by the model.
- `remaining_matches.txt` — schedule of remaining matches (comment lines ignored).
- `now_score.json` — saved/current standings (created/updated by `ivl_merged.py`).
- `ivl_prediction_report.html` — example generated report (committed as an example output).

## Quick start

Run the main simulator (default 100k simulations):

```bash
python ivl_merged.py
```

Run with no interactive prompts (use saved `now_score.json` or defaults):

```bash
python ivl_merged.py --no-input
```

Choose simulation size (100k/1M/10M):

```bash
python ivl_merged.py --sim 1000000
```

After a run you will see printed summaries and an HTML report saved as `ivl_prediction_report.html`.

Notes on performance: large values (1,000,000 or 10,000,000) may take considerable time; Numba accelerates the inner loop but the total runtime depends on CPU.

## Troubleshooting

- Missing ti_math: If you get an ImportError for `ti_math`, either add a `ti_math.py` implementing `eval_ti` or edit `predict_round.py` to use `math.factorial(k)` instead of `eval_ti(str(k)+"!")`.
- Encoding: files are read/written with UTF-8. If your terminal locale causes problems with the Chinese output in `ivl_merged.py`, set LANG/LC_ALL or run in an environment that supports UTF-8.

## Contributing

Feel free to open issues or PRs. Useful improvements:
- Add a real `ti_math` helper or remove the dependency by using math.factorial.
- Add a small README badge and CI to run a smoke test.
- Add unit tests for sim_bo3 and get_prob.

## License

No license file is included. Add a LICENSE if you want to clarify reuse terms.
