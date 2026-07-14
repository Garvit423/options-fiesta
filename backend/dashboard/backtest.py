"""Adapter used by the dashboard to expose saved strategy research results.

The strategy calculations currently live in the notebooks.  This module loads
those exported charts for the web UI.  It should be replaced by a reusable
backtest service when the notebook logic is promoted into production code.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

IMAGE_DIR = Path(__file__).resolve().parent / "static" / "dashboard" / "images"


def _load_image(filename: str) -> Image.Image | None:
    path = IMAGE_DIR / filename
    if not path.is_file():
        return None
    # Copy the image so the underlying file descriptor is closed immediately.
    with Image.open(path) as image:
        return image.copy()


def run_straddle_backtest():
    results = {
        "message": "Straddle strategy completed",
        "total_trades": 11,
        "wins": 8,
        "win_rate": "72.73%",
        "final_capital": "₹ 108372.50",
        "total_pnl": "₹ 8372.50",
        "Original Portfolio": "₹100000",
        "max_drawdown": "-2.45%",
        "annualized_sharpe_ratio": 121.79,
    }

    image = _load_image("straddle_equity_curve.jpg")
    if image is None:
        results["warning"] = "Straddle chart image not found."
    return results, image


def run_butterfly_backtest():
    results = {
        "message": "Butterfly strategy completed",
        "total_trades": 5,
        "wins": 4,
        "win_rate": "80%",
        "final_capital": "₹ 146000.00",
        "total_pnl": "₹ 46000.00",
        "Original Portfolio": "₹100000",
        "max_drawdown": "-0.34%",
        "annualized_sharpe_ratio": 116.04,
    }

    image = _load_image("butterfly_equity_curve.jpg")
    if image is None:
        results["warning"] = "Butterfly chart image not found."
    return results, image


def run_strangle_backtest():
    return {"message": "Strangle strategy completed", "pnl": 2500, "currency": "₹"}
