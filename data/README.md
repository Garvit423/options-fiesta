# Market-data layout

The application deliberately keeps market data outside the Django source tree.
This prevents analytics code from depending on the server's current working
directory and allows another dataset to be selected through an environment
variable.

```text
data/
├── spot/
│   └── nifty_underlying.csv
└── options/
    └── NIFTY/
        └── 2023-12-28/
        ├── 19800_call_2023-12-28.csv
        ├── 19800_put_2023-12-28.csv
        └── ...
```

## Underlying schema

`data/spot/nifty_underlying.csv`

| Column | Meaning |
|---|---|
| `datetime` | Observation timestamp |
| `open`, `high`, `low`, `close` | NIFTY OHLC values |
| `volume` | Reported underlying volume |

## Option schema

Each option CSV contains one strike/right/expiry contract.

| Column | Meaning |
|---|---|
| `datetime` | Observation timestamp |
| `stock_code` | Underlying symbol |
| `exchange_code` | Exchange segment |
| `product_type` | Instrument type |
| `expiry_date` | Contract expiry |
| `right` | Call or Put |
| `strike_price` | Contract strike |
| `open`, `high`, `low`, `close` | Option OHLC premium |
| `volume` | Traded volume |
| `open_interest` | Open interest |
| `count` | Source row/index field |

## Selecting another dataset

The default option directory is `data/options/NIFTY/2023-12-28`. To use another
repository-level data directory, set:

```bash
OPTIONS_FIESTA_DATA_DIR=/absolute/path/to/data
OPTIONS_UNDERLYING=NIFTY
OPTIONS_EXPIRY=2024-01-25
```

The expected option filename format is:

```text
<strike>_<call|put>_<YYYY-MM-DD>.csv
```
