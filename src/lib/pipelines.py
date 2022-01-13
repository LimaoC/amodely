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
        Returns the given dataframe with NaN entries replaced.
        """
        return X.fillna(self.value)


class CollapseDimensions(BaseEstimator, TransformerMixin):
    """
    Transformer to collapse multi-dimensional dataframes down to
    single-dimensional dataframes.
    """
    def __init__(self, measure: str, dimension: str) -> None:
        """
        Initialises a CollapseDimensions transformer.

        The dataframe rows are sorted by date (reverse chronological) and then
        by dimension (alphabetical).

        Parameters
        ----------
        `measure`
            The measure of the data. Determines which columns in the dataframes
            will be aggregated. Options can be found in `./lib.py` in the
            `STRUCTURE` dictionary.
        `dimension`
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
        """
        return X.groupby([DATE, self.dimension]) \
                .aggregate(STRUCTURE[self.measure]) \
                .sort_values([DATE, self.dimension]) \
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

    Since this transformation will collapse the data, it should only be applied
    once the data has been collapsed down to a single dimension (see the
    `CollapseDimensions` transformer).
    """
    def __init__(self, dimension: str, frequency: str) -> None:
        """
        Initialises a ConvertFrequency transformer.

        Parameters
        ----------
        `dimension`
            The dimension of the data.
        `frequency`
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
        # convert to the given frequency
        X = X.groupby([DATE, self.dimension]) \
             .resample(self.frequency, closed="left", label="left", on=DATE) \
             .sum() \
             .sort_values([DATE, self.dimension]) \
             .reset_index()

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
    def __init__(self, measure: str, dimension: str) -> None:
        """
        Initialises an AddResponse transformer.

        Parameters
        ----------
        `measure`
            The measure to be added. Options can be found in `./lib.py` in
            the `STRUCTURE` dictionary.
        `dimension`
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
        if self.measure == "SALES_PROPORTION":
            sales = X.sort_values([DATE, self.dimension]) \
                     .drop(columns=["QUOTE_COUNT"])

            # store total number of sales for each week
            total_sales = X.groupby(DATE)["SALES_COUNT"] \
                           .sum() \
                           .reset_index() \
                           .rename(
                               columns={"SALES_COUNT": "TOTAL_SALES_COUNT"})

            # add total sales count column to data and calculate proportion
            measure = sales.merge(total_sales, on=DATE, how="left")
            measure["SALES_PROPORTION"] = \
                measure["SALES_COUNT"] / measure["TOTAL_SALES_COUNT"]

        elif self.measure == "CONVERSION_RATE":
            measure = X["SALES_COUNT"] / X["QUOTE_COUNT"]

        # df1 = df.sort_values([DATE, dimension])[[DATE, "SALES_COUNT"]]
        # df2 = df.groupby(DATE)["SALES_COUNT"].sum().reset_index()
        # df3 = df1.merge(df2, on=DATE, how="left")
        # df["SALES_PROPORTION"] = df3["SALES_COUNT_x"] / df3["SALES_COUNT_y"]

        X[self.measure] = measure

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
        The measure of the data. Determines which columns will be aggregated
        when the data is collapsed. Options can be found in `./lib.py` in the
        `STRUCTURE` dictionary.
    `dimension`
        The dimension to use for the data transformation.
    `bad_categories`
        Categories to be removed. A good rule of thumb is to remove categories
        with less than 100 entries, since these are the most likely to cause
        problems in the anomaly detection stage.
    """
    return Pipeline([
        ("FillNA", FillNA(0)),
        ("CollapseDimensions", CollapseDimensions(measure, dimension)),
        ("RemoveBadCategories", FilterCategory(
            # remove Unknown category and other bad categories
            dimension, ["Unknown", *bad_categories], remove=True
        )),
        ("ConvertWeekly", ConvertFrequency(dimension, "W-MON")),
        ("AddMeasure", AddMeasure(measure, dimension))
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
