"""
This module contains the Amodely class, which is the anomaly detection model.
It handles the dataframes and runs the anomaly detection algorithm(s) on the
data.

The model stores two dataframes - the main dataframe (main_df attribute) and
the working dataframe (df attribute). Data processing, pipelining, anomaly
detection algorithms, etc. are done on the working dataframe. When you want to
use another configuration (i.e. another measure or dimension), the working
dataframe can be reset to the state of the main dataframe using the
reset_working() method. For this reason, the main dataframe shouldn't be
altered at all.

(adding to the main df)

An anomaly detection algorithm can be run on the working dataframe using the
method detect_anomalies(` (configuration options available). The results of the
algorithm are stored in the anomalies_ dataframe attribute (see
https://blog.finxter.com/why-does-the-scikit-learn-library-use-a-trailing-underscore-convention-for-attribute-names/
for an explanation of the underscore).
"""


import numpy as np
import pandas as pd
from scipy.stats import norm
import time

from .lib.lib import DATE, STRUCTURE
from .lib import arimatools as atools
from .lib import stl
from .lib import pipelines as pl


class Amodely:
    def __init__(self, df: pd.DataFrame, measure: str,
                 dimension: str = None) -> None:
        """
        Initialises an anomaly detection model with a main dataframe, a measure
        and a dimension.

        The dataframe to be loaded in is the unprocessed "main" dataframe. The
        measure and dimension are used in the anomaly detection algorithm and
        the dashboard. They can be changed afterwards.

        Parameters
        ----------
        df
            The main dataframe to be loaded in.
        measure
            The selected measure. A list of options can be found in
            /src/lib/lib.py. The default is "CONVERSION_RATE".
        dimension
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
        Returns the selected measure.
        """
        return self._measure

    @measure.setter
    def measure(self, measure: str) -> None:
        """
        Sets the selected measure to the given string.
        """
        if measure in STRUCTURE.keys():
            self._measure = measure
        else:
            raise AttributeError("Measure not found.")

    @property
    def dimension(self) -> str:
        """
        Returns the selected dimension.
        """
        return self._dimension

    @dimension.setter
    def dimension(self, dimension: str) -> None:
        """
        Sets the selected dimension to the given string.
        """
        dimension = dimension.upper()
        if dimension in self.dimensions or dimension == "ALL":
            self._dimension = dimension
        else:
            raise AttributeError("Dimension not found.")

    @property
    def dimensions(self) -> list[str]:
        """
        Returns a list of all the dimensions in the main dataframe.
        """
        dimensions = self.main_df.select_dtypes(object).columns.tolist()
        return dimensions

    @property
    def categories(self) -> list[str]:
        """
        Returns a list of all the categories in the selected dimension. If the
        selected dimension is ALL, returns a list with a single element "ALL".
        """
        if self.dimension == "ALL":
            return ["ALL"]
        return sorted(set(self.main_df[self.dimension]))

    @property
    def main_df(self) -> pd.DataFrame:
        """
        Returns the main dataframe.
        """
        return self._main_df

    @main_df.setter
    def main_df(self, df: pd.DataFrame) -> None:
        """
        Sets the main dataframe to a copy of the given dataframe.
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

    @property
    def bad_categories(self) -> list[str]:
        """
        Returns a list of the bad categories in the selected dimension.

        Bad categories have less than 100 data points and tend to cause
        problems with the anomaly detection algorithm. If the selected
        dimension is ALL, an empty list is returned.
        """
        if self.dimension == "ALL":
            return []
        else:
            # find categories with less than 100 entries
            filt = self.df[self.dimension].value_counts() < 100

            # find "Unknown" categories
            for category in self.categories:
                if "Unknown" in category:
                    return [*filt.drop(filt.index[~filt]).index, category]

            return filt.drop(filt.index[~filt]).index

    def reset_working(self) -> None:
        """
        Resets the working dataframe to the state of the main dataframe (as a
        copy).
        """
        self.df = self.main_df.copy()

    def download_anomalies(self, filename: str = "output") -> None:
        """
        Downloads the dataframe of anomalies to a spreadsheet (.xlsx).

        If no anomaly detection algorithm was run before this method was
        called, the output file will be empty. Note: data points considered to
        be anomalies are determined by the sig_level parameter that was used in
        the detect_anomalies() method.

        Parameters
        ----------
        filename
            The filename of the output spreadsheet. The default is output.xlsx.
        """
        self.anomalies_.to_excel(f"{filename}.xlsx")

    def detect_anomalies(self, method: str, sig_level: float = 0.05,
                         filter_dimension: str = "",
                         filter_categories: list = []) -> None:
        """
        Runs an anomaly detection algorithm on the model's working dataframe
        using the selected measure and dimension. The output is stored in the
        anomalies_ attribute.

        The methods that have been implemented are ARIMA (outdated) and STL.

        Parameters
        ----------
        method
            The method to use for the anomaly detection algorithm. The
            available options are "arima", "stl",
        sig_level
            The significance level to use for the anomaly detection algorithm.
        filter_dimension
            An (optional) dimension, different to the model's selected
            dimension, to filter for before the anomaly detection algorithm is
            run. See /src/dash-app/app.py for more details.
        filter_categories
            An (optional) category(s) to filter for in the filter dimension.
        """
        # filter for filter dimension & categories if specified
        self.reset_working()
        if filter_dimension:
            self.df = pl.FilterCategory(filter_dimension, filter_categories) \
                        .fit_transform(self.df)

        # collapse data to one dimension, remove bad categories, convert to
        # weekly data, add measure variable
        self.df = pl.dimension_pipeline(self.measure, self.dimension,
                                        bad_categories=self.bad_categories) \
                    .fit_transform(self.df)

        start_time = time.time()  # timing for diagnostic purposes
        anomalies = []

        for category in self.categories:
            # filter for given category
            df = pl.FilterCategory(self.dimension, [category]) \
                   .fit_transform(self.df)

            if method == "arima":  # NOT UP TO DATE
                steps = 4
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
                # decompose data and keep residuals
                decomposition = stl.calc_decomp(df, self.measure, period=12)
                residuals = decomposition.resid

                # add column for number of standard deviations from mean and
                # merge it with dataframe
                mean, std = np.mean(residuals), np.std(residuals)
                stds = ((residuals-mean) / std).rename("STANDARD_DEVIATIONS") \
                                               .reset_index()
                df = df.merge(stds, on=DATE, how="left")

                # add column to classify data points as anomalies based on sig.
                # level (assume standard normal - this almost always holds true
                # for the residuals)
                min_bound = norm.ppf(sig_level/2)
                max_bound = norm.ppf(1-sig_level/2)
                df["ANOMALY"] = (df["STANDARD_DEVIATIONS"] <= min_bound) | \
                                (df["STANDARD_DEVIATIONS"] >= max_bound)

                # add df of anomalies to list
                anomalies.append(df)

        print(f"Done, took {round(time.time() - start_time, 2)} seconds\n")

        # clean up working dataframe and add anomalies to anomalies_ attribute
        self.reset_working()
        self.anomalies_ = pd.concat(anomalies).sort_index()
