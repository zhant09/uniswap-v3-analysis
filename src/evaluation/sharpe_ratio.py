# write a function to calculate sharpe ratio
import numpy as np


def calc(returns, rf):
    """
    Calculate sharpe ratio given returns and risk-free rate
    """
    return (np.mean(returns) - rf) / np.std(returns)
    