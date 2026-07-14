"""Data discovery helpers for the Options Fiesta dashboard."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings

# The paths are declared once in options_dashboard/settings.py.  Keeping these
# aliases preserves the existing imports in views.py while avoiding fragile
# assumptions about the current working directory.
DATA_DIR = Path(settings.OPTIONS_DATA_DIR)
SPOT_CSV = Path(settings.SPOT_CSV_PATH)


def _validate_data_layout() -> None:
    """Raise a useful error when the configured data layout is incomplete."""

    if not SPOT_CSV.is_file():
        raise FileNotFoundError(
            f"Underlying data file was not found at {SPOT_CSV}. "
            "Set OPTIONS_FIESTA_DATA_DIR or restore data/spot/nifty_underlying.csv."
        )
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(
            f"Option data directory was not found at {DATA_DIR}. "
            "Set OPTIONS_FIESTA_DATA_DIR or restore data/options/<underlying>/<expiry>/."
        )


def list_option_files() -> list[dict[str, object]]:
    """Discover option CSVs and return contract metadata.

    Expected filename format::

        <strike>_<call|put>_<YYYY-MM-DD>.csv

    Malformed CSV filenames are ignored so non-market files can safely coexist
    in the directory.
    """

    _validate_data_layout()
    files: list[dict[str, object]] = []

    for file_path in sorted(DATA_DIR.glob("*.csv")):
        parts = file_path.stem.split("_", maxsplit=2)
        if len(parts) != 3:
            continue

        strike_text, option_type, expiry = parts
        option_type = option_type.lower()
        if option_type not in {"call", "put"}:
            continue

        try:
            strike = int(strike_text)
        except ValueError:
            continue

        files.append(
            {
                "path": file_path,
                "strike": strike,
                "type": option_type,
                "expiry": expiry,
                "filename": file_path.name,
            }
        )

    return files
