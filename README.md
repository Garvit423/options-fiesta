# Options Fiesta

Options Fiesta is a Django-based options analytics and strategy-research project built on minute-level NIFTY spot and option data. It computes implied volatility by inverting the Black–Scholes model, calculates the main option Greeks, visualizes implied volatility across strikes and time, and includes historical backtests for long straddle and long call butterfly strategies.

The bundled dataset is historical. Analytics are computed on demand when an API request is made; the project is not connected to a live exchange feed.

## Features

- Discovers option contracts from strike, option type, and expiry encoded in CSV filenames.
- Aligns option premiums with NIFTY spot observations using minute timestamps.
- Prices European calls and puts with the Black–Scholes model.
- Solves for implied volatility with SciPy's Brent root-finding method.
- Computes Delta, Gamma, Theta, Vega, and Rho from analytical formulas.
- Exposes the analytics through Django JSON endpoints with server-side caching.
- Uses Plotly in the dashboard for interactive Greek histories and a 3D implied-volatility view.
- Contains historical long straddle and long call butterfly backtests with trade logs, position sizing, equity curves, Sharpe-ratio calculation, and drawdown analysis.

## Quantitative methodology

### Black–Scholes pricing and implied volatility

For spot price \(S\), strike \(K\), time to expiry \(T\), risk-free rate \(r\), and volatility \(\sigma\):

\[
d_1 = \frac{\ln(S/K) + (r + \frac{1}{2}\sigma^2)T}{\sigma\sqrt{T}},
\qquad
d_2 = d_1 - \sigma\sqrt{T}
\]

The call and put prices are:

\[
C = S N(d_1) - K e^{-rT}N(d_2)
\]

\[
P = K e^{-rT}N(-d_2) - S N(-d_1)
\]

Given an observed option premium \(P_{market}\), implied volatility is obtained by solving:

\[
BS(S,K,T,r,\sigma)-P_{market}=0
\]

The implementation uses `scipy.optimize.brentq` over a bounded volatility interval. Brent's method was chosen because it is a bracketed solver and does not require the initial volatility estimate or Vega-based update used by Newton–Raphson.

Implementation:

- [`backend/dashboard/iv.py`](backend/dashboard/iv.py)
- [`backend/dashboard/views.py`](backend/dashboard/views.py)

### Greeks

After implied volatility is recovered, the project computes:

| Greek | Interpretation | Reported unit |
|---|---|---|
| Delta | Change in option value for a one-unit change in spot | price units per spot unit |
| Gamma | Change in Delta for a one-unit change in spot | per spot unit squared |
| Theta | Time decay | per calendar day |
| Vega | Sensitivity to volatility | per one percentage-point volatility move |
| Rho | Sensitivity to interest rates | per one percentage-point rate move |

Implementation:

- [`backend/dashboard/greeks.py`](backend/dashboard/greeks.py)

### Implied-volatility visualization

The dashboard calculates IV for the available strikes at selected timestamps and renders an interactive Plotly surface.

The bundled options data contains one expiry, `2023-12-28`. The current 3D view is therefore a **historical strike × observation-time × implied-volatility surface**. A conventional strike × time-to-expiry surface at one valuation time requires data for multiple expiries.

Implementation:

- [`backend/dashboard/views.py`](backend/dashboard/views.py), particularly the IV endpoints
- [`backend/dashboard/templates/dashboard/index.html`](backend/dashboard/templates/dashboard/index.html)

## Strategy backtests

The strategy research is contained in two notebooks. Both use minute-level NIFTY data, select contracts from the option CSVs, maintain trade state, size positions subject to a capital-per-trade limit, record completed trades, and calculate portfolio statistics.

### Long ATM straddle

At entry, the strategy buys an at-the-money call and put with the same strike and expiry:

\[
+1\,C(K) + 1\,P(K)
\]

The signal is based on Bollinger Band Width falling below a rolling lower quantile, representing a low-volatility regime. The ATM strike is selected by rounding the underlying level to the nearest available 100-point strike.

Notebook:

- [`notebooks/straddle_backtest.ipynb`](notebooks/straddle_backtest.ipynb)

### Long call butterfly

The butterfly uses three equally spaced call strikes:

\[
+1\,C(K-d) - 2\,C(K) + 1\,C(K+d)
\]

The bundled notebook uses a 100-point wing width. It applies the same volatility-compression signal and records the entry and exit price of every leg.

Notebook:

- [`notebooks/butterfly_backtest.ipynb`](notebooks/butterfly_backtest.ipynb)

### Performance measures

The notebooks produce:

- total and per-trade P&L;
- number of trades and winning trades;
- equity curve;
- peak-to-trough drawdown;
- Sharpe ratio based on changes in portfolio equity.

For an equity series \(E_t\), drawdown is calculated as:

\[
DD_t = \frac{E_t-\max_{u\leq t}E_u}{\max_{u\leq t}E_u}
\]

The annualized Sharpe ratio follows:

\[
\text{Sharpe} = \sqrt{A}\frac{\operatorname{mean}(r_t-r_{f,t})}{\operatorname{std}(r_t)}
\]

where the annualization factor \(A\) must match the frequency of the return series.

The notebooks are the source of truth for strategy calculations. The current Django backtest endpoint displays the latest exported notebook summaries and figures rather than rerunning the notebook on every request.

## Data flow

```text
NIFTY spot CSV ───────────────┐
                              ├─ timestamp alignment ─┐
Individual option CSVs ───────┘                       │
                                                      ├─ Black–Scholes IV
                                                      ├─ Greeks
                                                      ├─ IV time series
                                                      └─ Django JSON APIs
                                                               │
                                                               └─ Plotly dashboard

Spot and option CSVs ── strategy signal ── contract selection ── trade loop
                                                               │
                                                               ├─ trade log
                                                               ├─ P&L
                                                               ├─ equity curve
                                                               ├─ drawdown
                                                               └─ Sharpe ratio
```

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
│               ├── 19800_call_2023-12-28.csv
│               ├── 19800_put_2023-12-28.csv
│               └── ...
│
├── backend/
│   ├── manage.py
│   ├── options_dashboard/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── dashboard/
│       ├── iv.py
│       ├── greeks.py
│       ├── utils.py
│       ├── views.py
│       ├── backtest.py
│       ├── urls.py
│       ├── templates/
│       │   └── dashboard/
│       │       └── index.html
│       └── static/
│           └── dashboard/
│               └── images/
│
├── notebooks/
│   ├── straddle_backtest.ipynb
│   └── butterfly_backtest.ipynb
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Data

The included option sample contains:

- NIFTY spot OHLC observations at one-minute frequency;
- calls and puts for the `2023-12-28` expiry;
- strikes from `19,800` to `22,000` at 100-point intervals;
- option OHLC premium, volume, and open-interest columns;
- 46 individual option-contract CSV files.

The expected option filename format is:

```text
<strike>_<call|put>_<YYYY-MM-DD>.csv
```

For example:

```text
21000_call_2023-12-28.csv
21000_put_2023-12-28.csv
```

See [`data/README.md`](data/README.md) for the complete column definitions and directory convention.

## Running the project

### 1. Create and activate a virtual environment

```bash
git clone https://github.com/Garvit423/options-fiesta.git
cd options-fiesta

python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Create local configuration

```bash
cp .env.example .env
```

The default configuration uses the dataset committed under `data/`.

### 4. Initialize and run Django

```bash
cd backend
python manage.py migrate
python manage.py check
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

### 5. Run the notebooks

From the repository root:

```bash
python -m pip install jupyterlab
jupyter lab notebooks/
```

The notebooks locate the repository-level data directory without depending on the directory from which Jupyter was launched.

## Configuration

The following variables can be set in `.env`:

```env
SECRET_KEY=replace-with-a-local-development-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
TIME_ZONE=Asia/Kolkata

OPTIONS_FIESTA_DATA_DIR=data
OPTIONS_UNDERLYING=NIFTY
OPTIONS_EXPIRY=2023-12-28
```

Data paths are defined centrally in [`backend/options_dashboard/settings.py`](backend/options_dashboard/settings.py) and consumed by [`backend/dashboard/utils.py`](backend/dashboard/utils.py). Changing an expiry or moving the data directory does not require editing analytics code.

## API endpoints

| Method and endpoint | Purpose | Parameters |
|---|---|---|
| `GET /` | Render the dashboard | — |
| `GET /api/greeks/` | Return historical Greek values by contract | `r` |
| `GET /api/ivs/` | Return IV values across available strikes | `spot`, `r` |
| `GET /api/iv/` | Return historical IV time series | `r` |
| `GET /api/backtest/` | Return an exported strategy summary and chart | `strategy=straddle` or `strategy=butterfly` |

Example:

```bash
curl "http://127.0.0.1:8000/api/iv/?r=0.06"
```

The risk-free rate is supplied as a decimal, so `0.06` represents 6% per year.

## Where the main claims are implemented

| Project capability | Main files |
|---|---|
| Django options analytics application | `backend/dashboard/views.py`, `backend/dashboard/urls.py`, `backend/dashboard/templates/dashboard/index.html` |
| On-demand implied-volatility calculation | `backend/dashboard/iv.py`, `backend/dashboard/views.py` |
| Delta, Gamma, Theta, Vega, and Rho | `backend/dashboard/greeks.py` |
| Interactive 3D IV visualization | `backend/dashboard/templates/dashboard/index.html`, `GET /api/iv/` |
| Straddle backtest | `notebooks/straddle_backtest.ipynb` |
| Butterfly backtest | `notebooks/butterfly_backtest.ipynb` |
| Sharpe ratio and drawdown | final analysis cells in both strategy notebooks |
| Centralized data paths and contract discovery | `backend/options_dashboard/settings.py`, `backend/dashboard/utils.py` |

## Assumptions and limitations

- The bundled market observations are historical; there is no live exchange or broker connection.
- “On demand” refers to IV and Greek computation when the API is called, not to the source of the market data.
- Black–Scholes assumes European exercise, lognormal returns, constant volatility and interest rates, and frictionless markets.
- The current dataset contains one expiry, so the 3D visualization is historical strike × time rather than a full cross-maturity surface.
- Backtests use minute-bar closing prices rather than bid and ask quotes.
- The current research notebooks do not model transaction costs, slippage, queue position, partial fills, or market impact.
- Strategy results are based on a limited historical sample and are not evidence of future profitability.
- The dashboard's backtest API serves exported research output; the actual strategy calculations remain in the notebooks.

## Disclaimer

This repository is an educational quantitative-finance project. It is not investment advice and is not intended for live trading without further validation, execution modelling, and risk controls.
