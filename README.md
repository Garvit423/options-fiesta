# Options Fiesta

> A Django-based NIFTY options analytics dashboard for implied-volatility
> inversion, Black–Scholes Greeks, historical volatility visualization, and
> multi-leg strategy research.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-0C4B33?logo=django&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Vectorized%20Math-4D77CF?logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Time--Series%20Pipeline-150458?logo=pandas&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-Brent%20Root%20Solver-8CAAE6?logo=scipy&logoColor=white)

## Thirty-second overview

Options Fiesta turns minute-level NIFTY spot and option-chain CSV data into a
browser-based quantitative-analysis workflow:

1. **Discover contracts** from strike/right/expiry filenames.
2. **Synchronize option and underlying observations** by timestamp with Pandas.
3. **Infer implied volatility** by numerically inverting Black–Scholes using
   SciPy's bracketed Brent solver.
4. **Compute Delta, Gamma, Theta, Vega, and Rho** from analytical formulas.
5. **Serve JSON analytics endpoints** through Django with server-side caching.
6. **Render interactive Plotly charts**, including Greek histories and a
   strike-versus-time implied-volatility surface.
7. **Research long straddle and long call butterfly strategies** in reproducible
   notebooks using the same repository-level market data.

The project separates raw market data, the Django application, and quantitative
research notebooks. No analytics path depends on where the server or Jupyter
process was launched.

---

## What the dashboard provides

### Implied-volatility inversion

For a market premium \(P_{mkt}\), the backend solves:

\[
BS(S,K,T,r,\sigma,\text{right})-P_{mkt}=0
\]

using `scipy.optimize.brentq` on a bounded volatility interval. Brent's method
was selected because it combines the reliability of a bracketed solver with
faster convergence than plain bisection and does not require a Vega-based
initial step like Newton–Raphson.

### Analytical Greeks

After IV is recovered, the engine evaluates:

- **Delta** — first-order sensitivity to the underlying price;
- **Gamma** — curvature of option value with respect to the underlying;
- **Theta** — time decay, reported per calendar day;
- **Vega** — sensitivity to a one-percentage-point volatility move;
- **Rho** — sensitivity to a one-percentage-point interest-rate move.

### Historical volatility visualization

The dashboard exposes option IV through time across available strikes. Because
the bundled dataset contains one expiry (`2023-12-28`), the 3D display is best
interpreted as a **historical strike × observation-time × IV surface**. A
standard strike × maturity × IV surface requires multiple expiries observed at
the same valuation timestamp.

### Strategy research

The notebooks contain historical research for:

- **Long ATM straddle:** `+1 Call(K) +1 Put(K)`;
- **Long call butterfly:** `+1 Call(K-d) -2 Call(K) +1 Call(K+d)`.

They cover signal generation, contract selection, position sizing, trade logs,
equity curves, Sharpe-ratio calculation, and drawdown analysis. The current web
adapter displays exported notebook summaries and charts; the notebook-to-engine
promotion is intentionally kept visible rather than presenting saved research
output as a live execution service.

---

## Architecture

```text
                    ┌─────────────────────────────┐
                    │ Minute-level CSV market data│
                    │ spot + individual contracts │
                    └──────────────┬──────────────┘
                                   │
                         contract discovery
                         timestamp alignment
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
       ┌─────────▼─────────┐               ┌─────────▼─────────┐
       │ Django analytics  │               │ Research notebooks │
       │ IV + Greeks APIs  │               │ strategy backtests │
       └─────────┬─────────┘               └─────────┬─────────┘
                 │                                   │
           cached JSON                         P&L / risk metrics
                 │                                   │
       ┌─────────▼───────────────────────────────────▼─────────┐
       │          Browser dashboard and research output        │
       │          Plotly surfaces, histories, equity curves    │
       └───────────────────────────────────────────────────────┘
```

### Design choices

- **Data outside application code:** CSVs live under `data/`, not inside the
  Django package.
- **Single source of truth for paths:** `backend/options_dashboard/settings.py`
  owns all data locations.
- **Working-directory independence:** both Django and Jupyter use absolute
  `pathlib.Path` objects derived from the repository root.
- **CSV-oriented research pipeline:** sequential market data is read directly
  with Pandas; SQLite is reserved for Django framework state.
- **Cached expensive calculations:** repeated Greek requests are cached by the
  Django cache layer.
- **Separated pricing formulas:** request orchestration and timestamp alignment
  remain in `views.py`, while Black–Scholes and Greek formulas live in dedicated
  `iv.py` and `greeks.py` modules.

---

## Repository structure

```text
options-fiesta/
├── data/
│   ├── README.md
│   ├── spot/
│   │   └── nifty_underlying.csv
│   └── options/
│       └── NIFTY/
│           └── 2023-12-28/
│           ├── 19800_call_2023-12-28.csv
│           ├── 19800_put_2023-12-28.csv
│           └── ...
│
├── backend/
│   ├── manage.py
│   ├── options_dashboard/
│   │   ├── settings.py          # environment and centralized data paths
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── dashboard/
│       ├── views.py             # HTTP/API orchestration
│       ├── utils.py             # contract discovery and data locations
│       ├── iv.py                # Black–Scholes pricing + IV inversion
│       ├── greeks.py            # analytical option sensitivities
│       ├── backtest.py          # dashboard adapter for research output
│       ├── urls.py
│       ├── templates/dashboard/index.html
│       └── static/dashboard/images/
│
├── notebooks/
│   ├── straddle_backtest.ipynb
│   └── butterfly_backtest.ipynb
│
├── .env.example
├── .gitignore
├── PATH_MIGRATION.md
├── requirements.txt
└── README.md
```

---

## API surface

| Endpoint | Purpose | Main inputs |
|---|---|---|
| `GET /api/greeks/` | Historical Greek series by contract | `r` |
| `GET /api/ivs/` | IV points across strikes | `spot`, `r` |
| `GET /api/iv/` | Historical IV series for available contracts | `r` |
| `GET /api/backtest/` | Display a saved strategy research result | `strategy=straddle|butterfly` |

Example:

```bash
curl "http://127.0.0.1:8000/api/iv/?r=0.07"
```

The dashboard is available at `/`.

---

## Run locally

### 1. Clone and create an environment

```bash
git clone https://github.com/Garvit423/options-fiesta.git
cd options-fiesta

python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure local settings

```bash
cp .env.example .env
```

The default configuration already points to the bundled `data/` directory.

### 4. Initialize and run Django

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

### 5. Open the research notebooks

Install Jupyter if it is not already available, then launch it from the
repository root:

```bash
pip install jupyterlab
jupyter lab notebooks/
```

Each notebook locates the repository automatically, so it can also be opened
from an IDE without editing relative paths.

---

## Data assumptions

The bundled study data contains:

- minute-level NIFTY OHLC observations;
- 46 option-contract CSVs;
- strikes from 19,800 to 22,000 in 100-point intervals;
- calls and puts for the 28 December 2023 expiry;
- OHLC premium, volume, and open-interest fields.

The analytics merge the option and underlying series on rounded minute
timestamps. Option close is treated as the observed premium for IV inversion.

---

## Important modelling limitations

This is a quantitative research project, not a production exchange gateway.
The interpretation of results should account for:

1. **European Black–Scholes assumptions:** constant rates/volatility,
   frictionless markets, lognormal returns, and no discrete jumps.
2. **Single-expiry sample:** the bundled data does not form a complete
   cross-maturity volatility surface.
3. **OHLC rather than bid–ask quotes:** spread, queue position, and market impact
   are not directly observable.
4. **Historical replay, not a live feed:** calculations are performed on demand,
   but the supplied observations are historical CSV records.
5. **Saved web backtest output:** strategy calculations currently live in the
   notebooks; the dashboard adapter serves exported summaries and figures.
6. **Research-period risk:** strategy results require out-of-sample validation
   before any economic conclusion can be made.

These constraints are documented deliberately so that the quantitative claims
remain reproducible and defensible.

---

## Interview-oriented code tour

For a quick review, read the project in this order:

1. `backend/dashboard/iv.py` — Black–Scholes and Brent inversion;
2. `backend/dashboard/greeks.py` — Delta/Gamma/Theta/Vega/Rho formulas;
3. `backend/dashboard/utils.py` — data discovery and contract metadata;
4. `backend/dashboard/views.py` — timestamp merge, caching, and API payloads;
5. `notebooks/straddle_backtest.ipynb` — two-leg volatility strategy;
6. `notebooks/butterfly_backtest.ipynb` — three-strike defined-risk structure.

The path refactor is documented separately in [`PATH_MIGRATION.md`](PATH_MIGRATION.md).

---

## Natural extensions

- promote notebook strategy logic into a reusable event-driven backtest module;
- use bid/ask quotes and an explicit transaction-cost/slippage model;
- add multiple expiries and interpolate a conventional volatility surface;
- validate analytical Greeks against finite differences;
- add no-arbitrage checks before IV inversion;
- add unit tests for pricing, path discovery, API responses, and metrics;
- connect a live quote adapter without changing the pricing interface.

---

## Disclaimer

This repository is for educational and research purposes only. It is not
investment advice and does not represent an executable trading recommendation.
