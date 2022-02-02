"""
This module contains pipelines for data processing, preparation, and
transformations throughout the anomaly detection process and for the anomaly
detection dashboard.
"""


import pandas as pd
from scipy.stats import norm
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

from .lib import STRUCTURE, DATE


class FillNA(BaseEstimator, TransformerMixin):
    """
    Transformer to fill NaNs in dataframes with some given value (defaults to
    0).
    """
    def __init__(self, value: float = 0) -> None:
        """
        Initialises a FillNA transformer.

        Parameters
        ----------
        value
            Value to fill NaN entries with. The default is 0.
        """
        self.value = value

    def fit(self, X: pd.DataFrame, y=None) -> "FillNA":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the given dataframe with NaN entries replaced.
        """
        return X.fillna(self.value)


class CollapseDimensions(BaseEstimator, TransformerMixin):
    """
    Transformer to collapse a multi-dimensional dataframe down to a single
    dimension.
    """
    def __init__(self, measure: str, dimension: str) -> None:
        """
        Initialises a CollapseDimensions transformer.

        The dataframe rows are sorted by date (reverse chronological) and then
        by dimension (alphabetical).

        Parameters
        ----------
        measure
            The measure of the data. Determines which columns in the dataframes
            will be aggregated. A list of options can be found in
            /src/lib/lib.py.
        dimension
            The dimension to collapse down to.
        """
        self.measure = measure
        self.dimension = dimension

    def fit(self, X: pd.DataFrame, y=None) -> "CollapseDimensions":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the dataframe collapsed down to a single dimension.

        If the selected dimension is ALL, then all dimensions are aggregated
        together.
        """
        if self.dimension == "ALL":
            sort = DATE  # sort df by date
        else:
            sort = [DATE, self.dimension]  # sort df by date then by dimension

        return X.groupby(sort) \
                .aggregate(STRUCTURE[self.measure]) \
                .sort_values(sort) \
                .reset_index()


class FilterCategory(BaseEstimator, TransformerMixin):
    """
    Transformer to filter for or remove certain rows from a dataframe based on
    category.
    """
    def __init__(self, dimension: str, category: list[str],
                 remove: bool = False) -> None:
        """
        Initialises a FilterCategory transformer.

        Parameters
        ----------
        `dimension`
            The dimension in which to search for the category(s).
        `category`
            A list of categories to filter for.
        `remove`
            Whether to remove (True) or to filter (False) the given category(s)
            from the data. The default is False.
        """
        self.dimension = dimension
        self.category = category
        self.remove = remove

    def fit(self, X: pd.DataFrame, y=None) -> "FilterCategory":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the dataframe with category filters applied.

        If the selected dimension is ALL, the original dataframe is returned as
        there are no categories to filter for.
        """
        if self.dimension == "ALL":
            # apply no filters; return the original dataframe
            return X

        regex = "|".join(self.category)
        filt = X[self.dimension.upper()].str.contains(regex)

        # reset index if categories are being removed
        return (X[~filt].reset_index(drop=True) if self.remove else X[filt])


class FilterYear(BaseEstimator, TransformerMixin):
    """
    Transformer to filter for a given year in the data.
    """
    def __init__(self, year: int) -> None:
        """
        Initialises a FilterYear transformer.

        Parameters
        ----------
        `year`
            The year to filter for
        """
        self.year = year

    def fit(self, X: pd.DataFrame, y=None) -> "FilterYear":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the dataframe filtered for the given year.
        """
        X = X[X[DATE].dt.year == self.year]

        return X


class ConvertFrequency(BaseEstimator, TransformerMixin):
    """
    Transformer to convert a dataframe consisting of daily data to another
    given frequency.

    Since this transformation will collapse the data, it should only be applied
    once the data has been collapsed down to a single dimension (see the
    CollapseDimensions transformer).
    """
    def __init__(self, dimension: str, frequency: str) -> None:
        """
        Initialises a ConvertFrequency transformer.

        Parameters
        ----------
        dimension
            The dimension of the data.
        frequency
            The frequency to convert the data to.
        """
        self.dimension = dimension
        self.frequency = frequency

    def fit(self, X: pd.DataFrame, y=None) -> "ConvertFrequency":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the dataframe collapsed down to the given frequency.
        """
        if self.dimension == "ALL":
            X = X.resample(self.frequency, closed="left", label="left",
                           on=DATE) \
                 .sum() \
                 .sort_values(DATE) \
                 .reset_index()
        else:
            # convert to the given frequency
            X = X.groupby(self.dimension) \
                .resample(self.frequency, closed="left", label="left",
                          on=DATE) \
                .sum() \
                .sort_values([DATE, self.dimension]) \
                .reset_index()

            # switch first and second rows to keep date in the first column
            cols = list(X.columns)
            cols[0], cols[1] = cols[1], cols[0]
            X[[X.columns[0], X.columns[1]]] = X[[X.columns[1], X.columns[0]]]
            X.columns = cols

        return X


class AddMeasure(BaseEstimator, TransformerMixin):
    """
    Transformer to add in the measure variable (e.g. conversion rate) after
    other data transformations have been applied.

    Since the measures are usually aggregated metrics, this transformation
    needs to be done after the data has been collapsed down to a single
    dimension (see the CollapseDimensions transformer).

    For proportion measures (e.g. sales proportion, quote proportion) which are
    based on categories, the resulting measure column will consist of 1s.
    """
    def __init__(self, measure: str, dimension: str) -> None:
        """
        Initialises an AddResponse transformer.

        Parameters
        ----------
        measure
            The measure to be added. A list of options can be found in
            /src/lib/lib.py.
        dimension
            The dimension being used by the dataframe.
        """
        self.measure = measure
        self.dimension = dimension

    def fit(self, X: pd.DataFrame, y=None) -> "AddMeasure":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the dataframe with an added measure column at the end.
        """
        if self.dimension == "ALL" and self.measure in \
                ("QUOTE_PROPORTION", "SALES_PROPORTION"):
            measure = 1  # proportion measures are always 1 for ALL
        elif self.measure == "QUOTE_VOLUME":
            measure = X["QUOTE_COUNT"]
        elif self.measure == "SALES_VOLUME":
            measure = X["SALES_COUNT"]
        elif self.measure == "QUOTE_PROPORTION":
            quotes = X.sort_values([DATE, self.dimension])

            # store total number of quotes for each week
            total_quotes = X.groupby(DATE)["QUOTE_COUNT"] \
                            .sum() \
                            .reset_index() \
                            .rename(columns={
                                "QUOTE_COUNT": "TOTAL_QUOTE_COUNT"
                            })

            # add total quote count column to data and calculate proportion
            merged = quotes.merge(total_quotes, on=DATE, how="left")
            measure = merged["QUOTE_COUNT"] / merged["TOTAL_QUOTE_COUNT"]

            # add total quote count column to dataframe
            X["TOTAL_QUOTE_COUNT"] = merged["TOTAL_QUOTE_COUNT"]
        elif self.measure == "SALES_PROPORTION":
            sales = X.sort_values([DATE, self.dimension])

            # store total number of sales for each week
            total_sales = X.groupby(DATE)["SALES_COUNT"] \
                           .sum() \
                           .reset_index() \
                           .rename(columns={
                               "SALES_COUNT": "TOTAL_SALES_COUNT"
                           })

            # add total sales count column to data and calculate proportion
            merged = sales.merge(total_sales, on=DATE, how="left")
            measure = merged["SALES_COUNT"] / merged["TOTAL_SALES_COUNT"]

            # add total sales count column to dataframe
            X["TOTAL_SALES_COUNT"] = merged["TOTAL_SALES_COUNT"]
        elif self.measure == "CONVERSION_RATE":
            measure = X["SALES_COUNT"] / X["QUOTE_COUNT"]

        # add measure column to dataframe
        X[self.measure] = measure

        return X


class FilterOutliers(BaseEstimator, TransformerMixin):
    """
    Transformer to filter for outliers in normally distributed data.
    """
    def __init__(self, sig: float) -> None:
        """
        Initialises a FilterOutliers transformer

        Parameters
        ----------
        sig
            The significance level to use to determine the outliers.
        """
        self.sig = sig

    def fit(self, X: pd.DataFrame, y=None) -> "FilterOutliers":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the anomaly dataframe with outliers only.
        """
        min_bound, max_bound = norm.ppf(self.sig/2), norm.ppf(1 - self.sig/2)

        return X[(X["STANDARD_DEVIATIONS"] >= max_bound) |
                 (X["STANDARD_DEVIATIONS"] <= min_bound)]


def dimension_pipeline(measure: str, dimension: str, frequency: str = "W-MON",
                       bad_categories: list[str] = []) -> Pipeline:
    """
    Creates and returns a pipeline to collapse down to a single dimension,
    resample to a given frequency, and add a measure variable.

    If dimension is ALL, all dimensions will be collapsed down (i.e. no
    dimensions remaining).

    Parameters
    ----------
    measure
        The measure of the data. Determines which columns will be aggregated
        when the data is collapsed. A list of options can be found in
        /src/lib/lib.py.
    dimension
        The dimension to use for the data transformation.
    bad_categories
        Categories to be removed.
    frequency
        The frequency of the data. See ConvertFrequency().
    """
    if dimension == "ALL":
        return Pipeline([
            ("CollapseDimensions", CollapseDimensions(measure, dimension)),
            ("ConvertWeekly", ConvertFrequency(dimension, frequency)),
            ("AddMeasure", AddMeasure(measure, dimension))
        ])
    else:
        return Pipeline([
            ("CollapseDimensions", CollapseDimensions(measure, dimension)),
            ("RemoveBadCategories", FilterCategory(
                # remove Unknown category and other bad categories
                dimension, ["Unknown", *bad_categories], remove=True
            )),
            ("ConvertWeekly", ConvertFrequency(dimension, frequency)),
            ("AddMeasure", AddMeasure(measure, dimension))
        ])


def outliers_pipeline(dimension: str, category: str,
                      sig: float = 0.05) -> Pipeline:
    """
    Creates and returns a pipeline to filter for a given category's outliers
    for a given dimension.

    Parameters
    ----------
    dimension
        The dimension to filter for.
    category
        The category to filter for.
    sig
        The significance level to use for determining the outliers.
    """
    return Pipeline([
        ("FilterCategory", FilterCategory(dimension, [category])),
        ("FilterOutliers", FilterOutliers(sig))
    ])


if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
