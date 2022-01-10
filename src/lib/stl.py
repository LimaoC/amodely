import pandas as pd
from statsmodels.tsa.seasonal import STL

from .lib import DATE


def calc_decomp(time_series: pd.DataFrame, response: str):
    stl = STL(time_series.set_index(DATE)[response], period=12).fit()
    return stl
