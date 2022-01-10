import numpy as np
import pandas as pd
from scipy.stats import norm
import time

from .lib.lib import DATE, STRUCTURE
from .lib import arimatools as atools
from .lib import stl
from .lib import pipelines as pl


class Amodely:
    def __init__(self, df: pd.DataFrame, measure: str) -> None:
        """
        Initialises an anomaly detection model with a dataframe.

        Parameters
        ----------
        `df`
            The master/main dataframe.
        `measure`
            The measure of the data. Determines which columns will be
            aggregated when the data is collapsed.
            Options: `conversion_rate`,
        """
        df = pl.FillNA(0).fit_transform(df)  # convert NaNs to zeroes
        self.main_df = self.df = df
        self.anomalies_ = pd.DataFrame()  # empty dataframe to begin with
        self.measure = measure
        self.dimension = self.dimensions[0]  # default to first dimension

    @property
    def measure(self) -> str:
        """
        Returns the measure.
        """
        return self._feature

    @measure.setter
    def measure(self, measure: str) -> None:
        """
        Sets the measure to the given string.
        """
        if measure in STRUCTURE.keys():
            self._feature = measure
        else:
            raise AttributeError("Measure not found.")

    @property
    def dimensions(self) -> list[str]:
        """
        Returns a list of all the dimensions in the main dataframe.
        """
        dimensions = self.main_df.select_dtypes(object).columns.tolist()
        return dimensions

    @property
    def dimension(self) -> str:
        """
        Returns the dimension currently in use (by the dashboard).
        """
        return self._dimensions

    @dimension.setter
    def dimension(self, dimension: str) -> None:
        """
        Sets the dimension to be used (by the dashboard).
        """
        if dimension in self.dimensions:
            self._dimension = dimension
        else:
            raise AttributeError("Dimension not found.")

    @property
    def main_df(self) -> pd.DataFrame:
        """
        Returns the main dataframe.
        """
        return self._main_df

    @main_df.setter
    def main_df(self, df: pd.DataFrame) -> None:
        """
        Sets the main dataframe to the given dataframe.

        This method should not be manually called. It should only be used when
        the original dataset is first loaded into the class. Any additions to
        the data should be done through the `append()` method.
        """
        self._main_df = df.copy()

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns the working dataframe.
        """
        return self._df

    @df.setter
    def df(self, df: pd.DataFrame) -> None:
        """
        Sets the working dataframe to a copy of the given dataframe.
        """
        self._df = df.copy()

    def reset_working(self) -> None:
        """
        Resets the working dataframe to the state of the main dataframe.
        """
        self.df = self.main_df

    def append(self, df: pd.DataFrame, sort_after: bool = False,
               reset_working: bool = False) -> None:
        """
        Appends additional data to the end of the main dataframe.

        If the columns of the given dataframe are not the same as the columns
        of the main dataframe, this method does nothing.

        Parameters
        ----------
        `df`
            Dataframe containing new entries to be added to the main dataframe
        `sort_after`
            Whether a sort operation should be performed on the main dataframe
            after insertion. This is only needed if the data from the
            additional dataframe is not sorted (by date) to begin with.
        `reset_working`
            Whether to reset the working dataframe after appending.
        """
        df = pl.FillNA(0).fit_transform(df)  # convert Nans to zeroes

        # concatenate dataframe if the columns are the same
        if set(self._main_df.columns) == set(df.columns):
            self._main_df = pd.concat(
                objs=[self._main_df, df],
                axis=0,
                ignore_index=True  # reset index after concatenation
            )

            if sort_after:
                self._main_df.sort_values(
                    by=DATE, inplace=True, ignore_index=True
                )

            if reset_working:
                self.reset_working()

    def download_anomalies(self, filename: str = "output") -> None:
        """
        Downloads the dataframe of anomalies to a spreadsheet (.xlsx).

        If no anomaly detection algorithm is run before this method is called,
        the output file will be empty.

        Parameters
        ----------
        `filename`
            The filename of the output spreadsheet. The default is output.xlsx.
        """
        self.anomalies_.to_excel(f"{filename}.xlsx")

    def detect_anomalies(self, method: str, dimension: str, steps: int = 4):
        """
        Runs an ARIMA anomaly detection algorithm
        """
        # data preparation on dataframe

        # only keep categories (cats) that have more than 100 occurrences
        bad_cats = self.df[dimension].value_counts() <= 100
        bad_cats = bad_cats.drop(bad_cats.index[~bad_cats]).index

        # collapse data to one dimension, remove bad categories, convert to
        # weekly data, add measure variable
        self.df = (
            pl
            .dimension_pipeline(self.measure, dimension, bad_cats)
            .fit_transform(self.df)
        )

        response = self.measure.upper()
        categories = sorted(set(self.df[dimension]))
        anomalies = []

        for category in categories:
            print(f"{dimension}: {category}")
            start_time = time.time()

            # filter for given category
            df = (
                pl.category_pipeline(dimension, [category])
                .fit_transform(self.df)
            )

            if method == "arima":
                # split into training and test dataset
                # test dataset is last 7 days
                train, test = df[:-steps], df[-steps:]
                train_response, test_response = train[response], test[response]

                params = atools.calc_parameters(train_response)
                model = atools.calc_arima(train_response, params)

                _, ci = model.predict(
                    n_periods=steps, return_conf_int=True
                )

                indices = []
                for i, value in enumerate(test_response):
                    if not (ci[i][0] <= value <= ci[i][1]):  # outlier
                        index = train.shape[0] + i
                        indices.append(index)

                # collate anomalies in one dataframe
                anomalies.append(df.iloc[indices, :].copy())
            elif method == "stl":
                decomp = stl.calc_decomp(df, response)

                residuals = decomp.resid
                mean, std = np.mean(residuals), np.std(residuals)
                sig = 0.05
                min_bound = norm.ppf(sig/2, loc=mean, scale=std)
                max_bound = norm.ppf(1-sig/2, loc=mean, scale=std)

                indices = []
                for i, value in enumerate(residuals):
                    if not (min_bound <= value <= max_bound):
                        indices.append(i)

                # collate anomalies in one dataframe
                anomalies.append(df.iloc[indices, :].copy())

            print(f"Done, took {round(time.time() - start_time, 2)} seconds\n")

        self.anomalies_ = pd.concat(anomalies).sort_index()
        return self.anomalies_
