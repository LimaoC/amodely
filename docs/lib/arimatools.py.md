## arimatools.py

This module contains helper functions to determine the best parameters for an ARIMA model.

---

### `is_stationary(time_series: pd.Series, sig_level: bool = 0.05) -> bool`

Tests whether the given time series is stationary at the given significance level using an ADF unit root test.

Parameters
- `time_series` <br /> The time series to test.
- `sig_level` <br /> The significance level to use for the ADF test. The default is 0.05.

Returns
- `True` if the time series is stationary, `False` otherwise.

### `calc_d(time_series: pd.Series, iter: int = 3, sig_level: float = 0.05) -> int`

Calculates the optimal order of differencing, d, for a given time series.

The optimal order of differencing is given by the (stationary) time series with the smallest standard deviation. See https://people.duke.edu/~rnau/arimrule.htm.

Parameters
- `time_series` <br /> The time series to use.
- `iter` <br /> The maximum number of differences to test. The optimal differencing order is usually between 0-2. The default is 3.
- `sig_level` The signfiicance level to use for the stationarity test (see the `is_stationary()` method). The edefault is 0.05.

Returns
- The optimal order of differencing, `d`.

### `calc_p(time_series: pd.Series, sig_level: float = 0.05) -> int`

Calculates the maximum value for the order of the AR model, p, for a given time series.

The maximum possible value is given by the number of lags that cross the critical region in the partial autocorrelation (PACF) plot of the time series. The optimal value can be difficult to determine programmatically (as it can be subjective), so the upper limit for `p` is returned instead.

Parameters
- `time_series` <br /> The time series to use.
- `sig_level` The significance level to use to determine the critical region in the PACF plot. The default is 0.05.

Returns
- The maximum value for the order of the AR model, `p`.

### `calc_q(time_series: pd.Series, sig_level: int = 0.05) -> int`

Calculates the maximum value for the order of the MA term, q, for a given time series.

The maximum possible value is given by the number of lags that cross the critical region in the autocorrelation (ACF) plot of the time series. The optimal value can be difficult to determine programmatically (as it can be subjective), so the upper limit for `q` is returned instead.

Parameters
- `time_series` <br /> The time series to use.
- `sig_level` <br /> The significance level to use to determine the critical region in the ACF plot. The default is 0.05.

Returns
- The maximum value for the order of the MA model, `q`.

### `calc_parameters(time_series: pd.Series, sig_level: float = 0.05) -> tuple`

Calculates the starting ARIMA parameters `(p, d, q)` for a given time series.

`d` is the optimal value while `p` and `q` are the maximum values. See `calc_p()`, `calc_d()`, and `calc_q()` for an explanation.

Parameters
- `time_series` <br /> The time series to use.
- `sig_level` The significance level to use for the stationarity test (`q`) and to determine the critical region in the ACF and PACF plots (`p` and `q`). The default is 0.05.

Returns
- A tuple of the three calculated ARIMA parameters `(p, d, q)`.

### `calc_arima(time_series: pd.Series, params: tuple, **kwargs) -> ARIMAResults`

Calculates the best fit ARIMA model for the given time series and given starting parameters.

A grid search is performed to determine the best parameter combinations, ranging from (0, 0, 0) up to (p, d, q) where `params = (p, d, q)` ("best" as determined by each model's AICc score).

Parameters
- `time_series` <br /> The time serie sto use.
- `params` <br /> A tuple of the three calculated ARIMA parameters `(p, d, q)`.
- `**kwargs` <br /> Arbitrary keyword arguments for the auto arima function