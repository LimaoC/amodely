"""
This module is used to read in the main dataframe and to initialise the master
and anomaly detection models for the dashboard.
"""


from dotenv import load_dotenv
import os

import pandas as pd

from ..amodely import Amodely
from ..lib.lib import DATASET_NAME, DEFAULT_DIMENSION, DEFAULT_MEASURE
from ..lib.pipelines import dimension_pipeline


load_dotenv()
DATASET_PATH = os.environ.get("DATASET_PATH")

# read in dataframe
df = pd.read_excel(DATASET_PATH + DATASET_NAME)

# dimension pipeline with default settings
default_pipeline = dimension_pipeline(DEFAULT_MEASURE, DEFAULT_DIMENSION)

# master model
master = Amodely(
    df=df,
    measure=DEFAULT_MEASURE,
    dimension=DEFAULT_DIMENSION)
master.df = default_pipeline.fit_transform(master.df)

# anomaly detection model
anomaly = Amodely(
    df=df,
    measure=DEFAULT_MEASURE,
    dimension=DEFAULT_DIMENSION)
anomaly.detect_anomalies(method="stl")
anomaly.df = default_pipeline.fit_transform(anomaly.df)
