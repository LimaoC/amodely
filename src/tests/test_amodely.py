import os
import sys
import pandas as pd
from pandas.testing import assert_frame_equal
import unittest

from ..amodely import Amodely


df = pd.read_excel("amodely/tests/test_dataset.xlsx")


class CustomTests:
    """
    Suite of custom tests in addition to unittest.TestCase
    """
    def assertFrameEqual(self, left: pd.DataFrame, right: pd.DataFrame,
                         *args, **kwargs) -> None:
        """
        Checks that the left and right dataframes are equal.

        Parameters
        ----------
        `left`
            The first dataframe to compare.
        `right`
            The second dataframe to compare.
        `*args`
            Arbitrary arguments.
        `**kwargs`
            Arbitrary keyword arguments.
        """
        assert_frame_equal(left, right, *args, **kwargs)

    def assertFrameNotEqual(self, left: pd.DataFrame, right: pd.DataFrame,
                            *args, **kwargs) -> None:
        """
        Checks that the left and right dataframes are not equal.

        Parameters
        ----------
        `left`
            The first dataframe to compare.
        `right`
            The second dataframe to compare.
        `*args`
            Arbitrary arguments.
        `**kwargs`
            Arbitrary keyword arguments.
        """
        try:
            assert_frame_equal(left, right, *args, **kwargs)
        except AssertionError:  # frames are not equal
            pass
        else:  # frames are equal
            raise AssertionError("DataFrames are equal.")


class TestSimple(unittest.TestCase, CustomTests):
    def test_init_loads_dataframes_correctly(self):
        """
        Test main and working dataframes are equal to input dataframe
        """
        model = Amodely(df, measure="conversion_rate")

        self.assertFrameEqual(df, model.main_df)
        self.assertFrameEqual(df, model.df)

    def test_init_determines_correct_dimensions(self):
        """
        Test correct dimensions are calculated
        """
        model = Amodely(df, measure="conversion_rate")
        correct_dimensions = model.df.select_dtypes(object).columns.tolist()

        self.assertCountEqual(model.dimensions, correct_dimensions)

    def test_init_creates_empty_anomalies_dataframe(self):
        """
        Test anomalies dataframe is empty to begin with
        """
        model = Amodely(df, measure="conversion_rate")

        self.assertFrameEqual(model.anomalies_, pd.DataFrame())

    def test_init_rejects_invalid_measure(self):
        """
        Test invalid measure name is rejected by initialisation
        """
        self.assertRaises(AttributeError, Amodely, df, "invalid measure")

    def test_setter_rejects_invalid_measure(self):
        """
        Test invalid measure name is rejected by measure setter
        """
        model = Amodely(df, measure="conversion_rate")

        self.assertRaises(AttributeError, Amodely.measure.fset, model,
                          "another invalid measure")
        # test measure variable hasn't been changed
        self.assertEqual(model.measure, "conversion_rate")

    def test_dimensions_not_changed_by_changes_to_working_df(self):
        """
        Test dimensions aren't changed by changes to working dataframe
        """
        model = Amodely(df, measure="conversion_rate")
        correct_dimensions = model.df.select_dtypes(object).columns.tolist()
        model.df["new_dimension"] = "dimension values"

        self.assertEqual(model.dimensions, correct_dimensions)

    def test_dimensions_changed_by_changes_to_main_df(self):
        """
        Test dimensions are changed by changes to main dataframe

        Note: columns should never be dropped from the main dataframe. This is
        just for testing purposes.
        """
        model = Amodely(df, measure="conversion_rate")
        original_dimensions = model.dimensions.copy()
        dropped_dimension = model.dimensions[0]
        model.main_df.drop(columns=dropped_dimension, inplace=True)

        self.assertSetEqual(
            set(original_dimensions) - set([dropped_dimension]),
            set(model.dimensions)
        )

    def test_main_df_is_a_copy(self):
        """
        Test main dataframe is a copy of the input dataframe
        """
        model = Amodely(df, measure="conversion_rate")
        model.main_df["new_col"] = "new values"

        self.assertFrameNotEqual(df, model.main_df)

    def test_working_df_is_a_copy(self):
        """
        Test working dataframe is a copy of the input dataframe
        """
        model = Amodely(df, measure="conversion_rate")
        model.df["new_col"] = "new values"

        self.assertFrameNotEqual(df, model.df)

    def test_main_df_different_from_working_df(self):
        """
        Test main and working dataframe are different
        """
        model = Amodely(df, measure="conversion_rate")
        model.df["new_col"] = "new_values"

        self.assertFrameNotEqual(model.main_df, model.df)

    def test_reset_working(self):
        """
        Check `reset_working` method
        """
        # change working dataframe and reset it
        model = Amodely(df, measure="conversion_rate")
        model.df["new_col"] = "new_values"
        model.reset_working()

        # check equality of working dataframe and main dataframe
        self.assertFrameEqual(model.main_df, model.df)

        # check main dataframe not attached to working dataframe
        model.df["new_col"] = "new_values"
        self.assertFrameNotEqual(model.main_df, model.df)


if __name__ == "__main__":
    unittest.main()
