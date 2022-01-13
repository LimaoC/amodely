import pandas as pd
from statsmodels.tsa.seasonal import STL

from .lib import DATE


def calc_decomp(time_series: pd.DataFrame, measure: str, **kwargs):
    """
    Calculates the STL (Seasonal and Trend decomposition using LOESS) based on
    the given time series and the given measure.

    Parameters
    ----------
    `time_series`
        The time series to decompose
    `measure`
        The measure to use (i.e. variable of interest to decompose). Options
        can be found in `./lib.py` in the `STRUCTURE` dictionary.
    `**kwargs`
        Arbitrary keyword arguments
    """
    stl = STL(time_series.set_index(DATE)[measure], **kwargs).fit()
    return stl
