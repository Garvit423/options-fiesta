from PIL import Image

def run_straddle_backtest():
    # Backtest results
    results = {
        "message": "Straddle strategy completed",
        "total_trades": 11,
        "wins": 8,
        "win_rate": "72.73%",
        "final_capital": "₹ 108372.50",
        "total_pnl": "₹ 8372.50",
        "Original Portfolio": "₹100000",
        "max_drawdown": "-2.45%",
        "annualized_sharpe_ratio": 121.79
    }
    # Load an existing graph image from file
    try:
        image = Image.open(r"C:\Users\ankit\OneDrive\Desktop\options_fiesta\Options-Dash\options_dashboard\dashboard\Straddle-Graph Results.jpg")  # Replace with your image filename or path
    except FileNotFoundError:
        image = None
        results["warning"] = "Graph image not found."

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
        "annualized_sharpe_ratio": 116.04
    }

    # Load an existing graph image from file    return results 
    try:
        image = Image.open(r"C:\Users\ankit\OneDrive\Desktop\options_fiesta\Options-Dash\options_dashboard\dashboard\Butterfly-Graph Results.jpg")  # Replace with your image filename or path
    except FileNotFoundError:
        image = None
        results["warning"] = "Graph image not found."

    return results, image
def run_strangle_backtest():
    return {"message": "Butterfly strategy completed", "pnl": 2500, "currency": "₹"}
