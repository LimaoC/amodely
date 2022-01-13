import numpy as np
import pandas as pd
from scipy.stats import norm
import time

from .lib.lib import DATE, STRUCTURE
from .lib import arimatools as atools
from .lib import stl
from .lib import pipelines as pl


class Amodely:
    def __init__(self, df: pd.DataFrame, measure: str = "CONVERSION_RATE",
                 dimension: str = None) -> None:
        """
        Initialises an anomaly detection model with a main dataframe, a measure
        and a dimension.

        The dataframe to be loaded in is the unprocessed "main" dataframe. The
        measure and dimension are used in the anomaly detection algorithm and
        the dashboard. They can be changed afterwards.

        Parameters
        ----------
        `df`
            The master/main dataframe.
        `measure`
            The selected measure. Options can be found in `./lib/lib.py` in the
            `STRUCTURE` dictionary. The default is `CONVERSION_RATE`.
        `dimension`
            The selected dimension. The default is the leftmost dimension in
            the dataframe.
        """
        # convert NaNs to zeroes in the dataframe first before assigning it
        self.main_df = self.df = pl.FillNA(0).fit_transform(df)
        self.measure = "CONVERSION_RATE" if measure is None else measure
        self.dimension = self.dimensions[0] if dimension is None else dimension
        # anomalies_ contains anomaly scores after an anomaly detection
        # algo is run
        self.anomalies_ = pd.DataFrame()

    @property
    def measure(self) -> str:
        """
        Returns the current measure in use.

        This is the measure displayed on the dashboard when the anomaly
        detection algorithm is run.
        """
        return self._measure

    @measure.setter
    def measure(self, measure: str) -> None:
        """
        Sets the measure to the given string. Options can be found in
        `./lib/lib.py` in the `STRUCTURE` dictionary.
        """
        if measure in STRUCTURE.keys():
            self._measure = measure
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
        Returns the current dimension in use.

        This is the dimension displayed on the dashboard when the anomaly
        detection algorithm is run.
        """
        return self._dimension

    @dimension.setter
    def dimension(self, dimension: str) -> None:
        """
        Sets the dimension to the given string. Options can be found by
        accessing the `dimensions` property.
        """
        dimension = dimension.upper()
        if dimension in self.dimensions:
            self._dimension = dimension
        else:
            raise AttributeError("Dimension not found.")

    @property
    def categories(self) -> list[str]:
        """
        Returns a list of all the categories in the current dimension.
        """
        return sorted(set(self.df[self.dimension]))

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
        df = pl.FillNA(0).fit_transform(df)  # convert NaNs to zeroes

        # concatenate dataframe if the columns are the same
        if set(self._main_df.columns) == set(df.columns):
            self._main_df = pd.concat(
                objs=[self._main_df, df],
                axis=0,
                ignore_index=True)  # reset index after concatenation

            if sort_after:
                self._main_df.sort_values(by=DATE, inplace=True,
                                          ignore_index=True)

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

    def detect_anomalies(self, method: str, steps: int = 4):
        """
        Runs an ARIMA anomaly detection algorithm on the model's selected
        measure and dimension. The output is stored in the `anomalies_`
        attribute.

        Parameters
        ----------
        `method`
            The method to use for the anomaly detection algorithm.
            Options: `arima`, `stl`.
        `steps`
        """
        # only keep categories that have more than 100 occurrences
        filt = self.df[self.dimension].value_counts() <= 100
        bad_categories = filt.drop(filt.index[~filt]).index

        # collapse data to one dimension, remove bad categories, convert to
        # weekly data, add measure variable
        self.df = pl.dimension_pipeline(self.measure, self.dimension,
                                        bad_categories) \
                    .fit_transform(self.df)

        anomalies = []

        for category in self.categories:
            print(f"{self.dimension}: {category}")  # debug
            start_time = time.time()

            # filter for given category
            df = pl.category_pipeline(self.dimension, [category]) \
                   .fit_transform(self.df)

            if method == "arima":
                # split into training and test dataset, size of test dataset
                # determined by steps parameter
                train, test = df[:-steps], df[-steps:]
                train_values = train[self.measure]
                test_values = test[self.measure]

                # calculate best fit arima model
                arima_params = atools.calc_parameters(train_values)
                model = atools.calc_arima(train_values, arima_params,
                                          alpha=0.05)

                # get confidence interval of forecast
                _, conf_int = model.predict(n_periods=steps,
                                            return_conf_int=True)

                # iterate through test dataset and mark data points as outliers
                # if they are outside the confidence interval
                indices = []
                for i, value in enumerate(test_values):
                    if not (conf_int[i][0] <= value <= conf_int[i][1]):
                        # outlier
                        index = train.shape[0] + i
                        indices.append(index)

                # collate anomalies in one dataframe
                anomalies.append(df.iloc[indices, :].copy())

            elif method == "stl":
                decomposition = stl.calc_decomp(df, self.measure,
                                                period=12)

                residuals = decomposition.resid
                mean, std = np.mean(residuals), np.std(residuals)
                sig = 0.05
                min_bound = norm.ppf(sig/2, loc=mean, scale=std)
                max_bound = norm.ppf(1-sig/2, loc=mean, scale=std)

                indices = []
                for i, value in enumerate(residuals):
                    if not (min_bound <= value <= max_bound):
                        indices.append(i)

                # collate anomalies in one dataframe
                stds = (residuals / std).rename("STANDARD_DEVIATIONS") \
                                        .reset_index()
                df = df.merge(stds, on=DATE, how="left")
                anomalies.append(df.iloc[indices, :].copy())

            print(f"Done, took {round(time.time() - start_time, 2)} seconds\n")

        self.anomalies_ = pd.concat(anomalies).sort_index()
        return self.anomalies_
