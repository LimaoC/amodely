## pipelines.py

This module contains pipelines for data processing, preparation, and transformations throughout the anomaly detection process and for the anomaly detection dashboard.

---

### `FillNA(BaseEstimator, TransformerMixin)`

Transformer to fill NaNs in dataframes with some given value (defaults to 0).

Returns the given dataframe with NaN entries replaced.

### `CollapseDimensions(BaseEstimator, TransformerMixin)`

Transformer to collapse a multi-dimensional dataframe down to a single dimension.

Returns the dataframe collapsed down to a single dimension.

### `FilterCategory(BaseEstimator, TransformerMixin)`

Transformer to filter for or remove certain rows from a dataframe based on category.

Returns the dataframe with filters applied.

### `FilterYear(BaseEstimator, TransformerMixin)`

Transformer to filter for a given year in the data.

Returns the dataframe filtered for the given year.

### `ConvertFrequency(BaseEstimator, TransformerMixin)`

Transformer to convert a dataframe consisting of daily data to another given frequency.

Since this transformation will collapse the data, it should only be applied once the data has been collapsed down to a single dimension (see the `CollapseDimensions` transformer).

Returns the dataframe collapsed down to the given frequency.

### `AddMeasure(BaseEstimator, TransformerMixin)`

Transformer to add in the measure variable after other data transformations have been applied.

Since the measures are usually aggregated metrics, this transformation needs to be done after the data has been collapsed down to a single dimension (see the `CollapseDimensions` transformer).

Returns the dataframe with an added measure column at the end.


### `dimension_pipeline(measure: str, dimension: str, frequency: str = "W-MON", bad_categories: list[str] = [])`

Creates and returns a pipeline to collapse down to a single dimension, resample to a given frequency, and add a measure variable.

If dimension == "ALL", all dimensions will be collapsed down (i.e. no dimensions remaining).

Parameters
- `measure` <br /> The measure of the data. Determines which columns will be aggregated when the data is collapsed. A list of options can be found in `/src/lib/lib.py`.
- `dimension` <br /> The dimension to use for the data transformation.
- `bad_categories` <br /> Categories to be removed.
- `frequency` <br /> The frequency of the data. See `ConvertFrequency()`.