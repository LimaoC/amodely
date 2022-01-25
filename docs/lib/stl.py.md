## stl.py

This module contains helper functions for decomposing time series data using the STL (Seasonal-Trend decomposition using LOESS) algorithm.

---

### `calc_decomp(time_series: pd.DataFrame, measure: str, **kwargs)`

Calculates the STL (Seasonal-Trend decomposition using LOESS) based on the given time series and the given measure.

Parameters
- `time_series` <br /> The time series to decompose.
- `measure` <br /> The measure to use (i.e. to decompose). A list of options can be found in `/src/lib/lib.py`.
- `**kwargs` <br /> Arbitrary keyweord arguments for the STL algorithm.