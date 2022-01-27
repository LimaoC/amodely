"""
This module contains helper functions for decomposing time series data using
the STL (Seasonal-Trend decomposition using LOESS) algorithm.
"""


import pandas as pd
from statsmodels.tsa.seasonal import STL

from .lib import DATE


def calc_decomp(time_series: pd.DataFrame, measure: str, **kwargs):
    """
    Calculates the STL (Seasonal-Trend decomposition using LOESS) based on the
    given time series and the given measure.

    Parameters
    ----------
    time_series
        The time series to decompose.
    measure
        The measure to use (i.e. to decompose). A list of
        options can be found in /src/lib/lib.py.
    **kwargs
        Arbitrary keyword arguments for the STL algorithm.
    """
    stl = STL(time_series.set_index(DATE)[measure], **kwargs).fit()
    return stl


if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
