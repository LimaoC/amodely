## pipelines.py

This module contains pipelines for data processing, preparation, and transformations throughout the anomaly detection process and for the anomaly detection dashboard.

---

### `FillNA(BaseEstimator, TransformerMixin)`

Transformer to fill NaNs in dataframes with some given value (defaults to 0).

Returns the given dataframe with NaN entries replaced.

### `CollapseDimensions(BaseEstimator, TransformerMixin)`

Transformer to collapse a multi-dimensional dataframe down to a single dimension.

Returns the dataframe collapsed down to a single dimension.

If the selected dimension is ALL, then all dimensions are aggregated together.

### `FilterCategory(BaseEstimator, TransformerMixin)`

Transformer to filter for or remove certain rows from a dataframe based on category.

Returns the dataframe with category filters applied.

If the selected dimension is ALL, the original dataframe is returned as there are no categories to filter for.

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

For porportion measures (e.g. sales proportion, quote proportion) which are based on categories, the resulting measure column will consist of 1s.

Returns the dataframe with an added measure column at the end.


### `FilterOutliers(BaseEstimator, TransformerMixin)`

Transformer to filter for outliers in normally distributed data.

Returns the anomaly dataframe with outliers only.


### `dimension_pipeline(measure: str, dimension: str, frequency: str = "W-MON", bad_categories: list[str] = [])`

Creates and returns a pipeline to collapse down to a single dimension, resample to a given frequency, and add a measure variable.

If dimension is ALL, all dimensions will be collapsed down (i.e. no dimensions remaining).

Parameters
- `measure` <br /> The measure of the data. Determines which columns will be aggregated when the data is collapsed. A list of options can be found in `/src/lib/lib.py`.
- `dimension` <br /> The dimension to use for the data transformation.
- `bad_categories` <br /> Categories to be removed.
- `frequency` <br /> The frequency of the data. See `ConvertFrequency()`.


### `outliers_pipeline(dimension: str, category: str, sig: float = 0.05) -> Pipeline:`

Creates and returns a pipelien to filter for a given category's outliers for a given dimension.

Parameters
- `dimension` <br /> The dimension to filter for.
- `category` <br /> The category to filter for.
- `sig` <br /> The significance level to use for determining the outliers.