from scipy.optimize import brentq
from scipy.stats import norm
import numpy as np

def bs_price(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def implied_volatility(S, K, T, r, market_price, option_type='call'):
    try:
        return brentq(lambda x: bs_price(S, K, T, r, x, option_type) - market_price, 1e-5, 5)
    except:
        return np.nan
