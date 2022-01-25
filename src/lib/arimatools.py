"""
This module contains helper functions to determine the best parameters for an
ARIMA model.
"""


import pandas as pd
from pmdarima.arima import auto_arima
import numpy as np
from statsmodels.tsa.arima.model import ARIMAResults
from statsmodels.tsa.stattools import acf, adfuller, pacf


def is_stationary(time_series: pd.Series, sig_level: bool = 0.05) -> bool:
    """
    Tests whether the given time series is stationary at the given significance
    level using an ADF unit root test.

    Parameters
    ----------
    time_series
        The time series to test.
    sig_level
        The significance level to use for the ADF test. The default is 0.05.

    Returns
    -------
        True if the time series is stationary, False otherwise.
    """
    results = adfuller(time_series.values)
    p_value = results[1]

    return (p_value < sig_level)


def calc_d(time_series: pd.Series, iter: int = 3,
           sig_level: float = 0.05) -> int:
    """
    Calculates the optimal order of differencing, d, for a given time series.

    The optimal order of differencing is given by the (stationary) time series
    with the smallest standard deviation.
    See: https://people.duke.edu/~rnau/arimrule.htm

    Parameters
    ----------
    time_series
        The time series to use.
    iter
        The maximum number of differences to take. The optimal differencing
        order is usually between 0-2. The default is 3.
    sig_level
        The significance level to use for the stationarity test (see the
        is_stationary() method). The default is 0.05.

    Returns
    -------
        The optimal order of differencing, d.
    """
    # repeatedly difference the time series up to iter times, and pick the
    # stationary time series with the smallest standard deviation

    differences = [(time_series, np.std(time_series), 0)]

    series_diff = time_series.copy()
    for order in range(iter):
        # difference the previous time series and store it in list
        series_diff = series_diff.diff().dropna()
        differences.append((series_diff, np.std(series_diff), order+1))

    # sort list by ascending standard deviation
    sorted(differences, key=lambda x: x[1])

    # find the first time series in list that is stationary
    d = 0
    for difference, _, order in differences:
        if is_stationary(difference, sig_level=sig_level):
            # optimal order of differencing found
            d = order
            break

    return d


def calc_p(time_series: pd.Series, sig_level: float = 0.05) -> int:
    """
    Calculates the maximum value for the order of the AR model, p, for a given
    time series.

    The maximum possible value is given by the number of lags that cross the
    critical region in the partial autocorrelation (PACF) plot of the time
    series. The optimal value can be difficult to determine programmatically
    (as it can be subjective), so the upper limit for p is returned instead.

    Parameters
    ----------
    time_series
        The time series to use.
    sig_level
        The significance level to use to determine the critical region in the
        PACF plot. The default is 0.05.

    Returns
    -------
        The maximum value for the order of the AR model, p.
    """
    # number of lags to include in PACF
    nlags = min(int(10*np.log10(time_series.size)), time_series.size//2 - 1)

    # calculate PACF values and confidence intervals
    values, conf_int = pacf(time_series, alpha=sig_level, nlags=nlags,
                            method="ywmle")
    # trim first values since PACF value is always 1
    values, conf_int = values[1:], conf_int[1:]

    # width of confidence interval is constant for all PACFs so store it here
    conf_int_width = (conf_int[0][1] - conf_int[0][0]) / 2

    # find number of values outside the critical region
    p = 0
    for value in values:
        if abs(value) >= conf_int_width:  # outside critical region
            p += 1
        else:
            break

    return p


def calc_q(time_series: pd.Series, sig_level: int = 0.05) -> int:
    """
    Calculates the maximum value for the order of the MA term, q, for a given
    time series.

    The maximum possible value is given by the number of lags that cross the
    critical region in the autocorrelation (ACF) plot of the time series.
    The optimal value can be difficult to determine programmatically (as it can
    be subjective), so the upper limit for q is returned instead.

    Parameters
    ----------
    time_series
        The time series to use.
    sig_level
        The significance level to use to determine the critical region in the
        ACF plot. The default is 0.05.

    Returns
    -------
        The maximum value for the order of the MA model, q.
    """
    # number of lags to include in ACF
    nlags = min(int(10*np.log10(time_series.size)), time_series.size//2 - 1)

    # calculate ACF values and confidence intervals
    values, conf_int = acf(time_series, alpha=sig_level, nlags=nlags, fft=True)
    # trim first values since ACF value is always 1 and convert NaNs to zeroes
    values, conf_int = np.nan_to_num(values[1:]), np.nan_to_num(conf_int[1:])

    # find number of values outside the critical region
    q = 0
    for i, value in enumerate(values):
        if abs(value) >= abs(conf_int[i][0] - value):
            # point is outside critical region
            q += 1
        else:
            break

    return q


def calc_parameters(time_series: pd.Series, sig_level: float = 0.05) -> tuple:
    """
    Calculates the starting ARIMA parameters (p, d, q) for a given time series.

    d is the optimal value while p and q are the maximum values. See
    calc_p(), calc_d(), and calc_q() for a more detailed explanation.

    Parameters
    ----------
    time_series
        The time series to use.
    sig_level
        The significance level to use to determine the critical region in the
        ACF and PACF plots for calculating p and q. The default is 0.05.

    Returns
    -------
        A tuple of the three calculated ARIMA parameters (p, d, q).
    """
    # calculate optimal order of differencing
    d = calc_d(time_series)

    # difference data d times
    series_diff = time_series.copy()
    for _ in range(d):
        # difference series and remove NA values
        series_diff = series_diff.diff().dropna()

    # calculate p and q with differenced series
    p = calc_p(series_diff, sig_level=sig_level)
    q = calc_q(series_diff, sig_level=sig_level)

    while q >= 10:
        # too many lags; reduce order of MA term and add a differencing order
        q -= 5
        d += 1

        # recalculate p
        series_diff = series_diff.diff().dropna()
        p = calc_p(series_diff, sig_level=sig_level)

    return (p, d, q)


def calc_arima(time_series: pd.Series, params: tuple,
               **kwargs) -> ARIMAResults:
    """
    Calculates the best fit ARIMA model for the given time series and given
    starting parameters.

    A grid search is performed to determine the best parameter combinations,
    ranging from (0, 0, 0) up to (p, d, q) where params = (p, d, q) ("best" as
    determined by each model's AICc score).

    Parameters
    ----------
    time_series
        The time series to use.
    params
        A tuple of the three calculated ARIMA parameters (p, d, q).
    **kwargs
        Arbitrary keyword arguments for the auto arima function

    Returns
    -------
        An ARIMAResults object initialized with the best fit parameters.
    """
    p, d, q = params

    return auto_arima(
        time_series,
        start_p=0,
        start_d=0,
        start_q=0,
        max_p=p,
        max_d=max(d, 1),
        max_q=q,
        m=52,  # weekly data
        seasonal=True,
        information_criterion="aicc",
        **kwargs
    )


if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
