"""
Pipelines for data processing/preparation/transformations
"""


import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

from .lib import STRUCTURE, DATE


class FillNA(BaseEstimator, TransformerMixin):
    """
    Transformer to fill NaNs in dataframes with some value.
    """
    def __init__(self, value: float) -> None:
        """
        Initialises a FillNA transformer.

        Parameters
        ----------
        `value`
            Value to fill NaN entries with.
        """
        self.value = value

    def fit(self, X: pd.DataFrame, y=None) -> "FillNA":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the given dataframe with NaN entries replaced with the given
        value.
        """
        return X.fillna(self.value)


class Collapse(BaseEstimator, TransformerMixin):
    """
    Transformer to collapse multi-dimensional dataframes down to
    single-dimensional dataframes.
    """
    def __init__(self, measure: str, dimension: str) -> None:
        """
        Initialises a Collapse transformer.

        Parameters
        ----------
        `measure`
            The measure of the data. Determines which columns will be
            aggregated when the data is collapsed.
            Options: `conversion_rate`,
        `dimension`
            The dimension to collapse down to.
        """
        self.measure = measure
        self.dimension = dimension

    def fit(self, X: pd.DataFrame, y=None) -> "Collapse":
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Returns the dataframe collapsed down to a single dimension.

        The dataframe columns that are aggregated are determined by the measure
        type (`measure`). Rows are sorted by date (chronologically) and then by
        dimension (alphabetically).
        """
        return (
            X
            .groupby([DATE, self.dimension])
            # aggregate columns based on measure
            .aggregate(STRUCTURE[self.measure])
            .sort_values([DATE, self.dimension])
            .reset_index()
        )


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
            A list of categories to filter for. Can be a list of one category.
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
        Returns the dataframe with filters applied.
        """
        regex = "|".join(self.category)
        filt = X[self.dimension.upper()].str.contains(regex)

        # reset index if categories are being removed
        return (X[~filt].reset_index(drop=True) if self.remove else X[filt])


class ConvertFrequency(BaseEstimator, TransformerMixin):
    """
    Transformer to convert a dataframe consisting of daily data to another
    given frequency.

    Since this transformation will collapse the data, it needs to be done after
    the data has been collapsed down to a single dimension.
    """
    def __init__(self, dimension: str, frequency: str) -> None:
        """
        Initialises a ConvertFrequency transformer.
        """
        self.dimension = dimension
        self.frequency = frequency

    def fit(self, X: pd.DataFrame, y=None):
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None):
        # convert to the given frequency
        X = (
            X
            .groupby(self.dimension)
            .resample(self.frequency, closed="left", label="left", on=DATE)
            .sum()
            .reset_index()
        )

        # switch first and second rows around so that date is the first column
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
    dimension.
    """
    def __init__(self, measure: str):
        """
        Initialises an AddResponse transformer.

        Parameters
        ----------
        `measure`
            The measure of the data. Determines which columns will be
            aggregated when the data is collapsed.
            Options: `conversion_rate`,
        """
        self.measure = measure

    def fit(self, X: pd.DataFrame, y=None):
        """
        No fitting needed.
        """
        return self

    def transform(self, X: pd.DataFrame, y=None):
        """
        Returns the dataframe with an added measure column at the end.
        """
        if self.measure == "conversion_rate":
            response = X["SALES_COUNT"] / X["QUOTE_COUNT"]

        X[self.measure.upper()] = response

        return X


def dimension_pipeline(measure: str, dimension: str,
                       bad_categories: list[str] = []) -> Pipeline:
    """
    Creates and returns a pipeline to collapse down to a single dimension and
    to add a measure variable.

    This is a pre-processing step to prepare the data for the anomaly detection
    algorithm.

    Parameters
    ----------
    `measure`
        The measure of the data. Determines which columns will be
        aggregated when the data is collapsed.
        Options: `conversion_rate`,
    `dimension`
        The dimension to use for the data transformation.
    `bad_categories`
        Categories to be removed. Usually these are categories that have less
        than 100 entries.
    """
    return Pipeline([
        ("FillNA", FillNA(0)),
        ("CollapseDimension", Collapse(measure, dimension)),
        ("RemoveBadCategories", FilterCategory(
            # remove Unknown category and other bad categories
            dimension, ["Unknown", *bad_categories], remove=True
        )),
        ("ConvertWeekly", ConvertFrequency(dimension, "W-MON")),
        ("AddMeasure", AddMeasure(measure))
    ])


def category_pipeline(dimension: str, category: list[str]) -> Pipeline:
    """
    Creates and returns a pipeline to filter for a category from
    single-dimensional data.

    Parameters
    ----------
    `dimension`
        The dimension to use for the data transformation.
    `category`
        A category or list of categories to filter for from the dataframe.
    """
    return Pipeline([
        ("FilterCategory", FilterCategory(dimension, category))
    ])


if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
