"""
This file contains constants necessary for the model and dashboard to function.
"""


import plotly.express as px


# ----------------------------- DATA CONSTANTS ------------------------------ #

DATE = "QUOTE_DATE"  # name of quote date column

# STRUCTURE contains measure variables as keys, which are themselves
# dictionaries containing the aggregation options used for each measure
# variable. See the CollapseDimensions transformer in /src/lib/pipelines.py.
STRUCTURE = {
    "QUOTE_VOLUME": {
        "QUOTE_COUNT": "sum",
    },
    "SALES_VOLUME": {
        "SALES_COUNT": "sum",
    },
    "QUOTE_PROPORTION": {
        "QUOTE_COUNT": "sum",
    },
    "SALES_PROPORTION": {
        "SALES_COUNT": "sum",
    },
    "CONVERSION_RATE": {
        "QUOTE_COUNT": "sum",
        "SALES_COUNT": "sum",
    }
}

# ----------------------- PLOTLY DASHBOARD CONSTANTS ------------------------ #

DEFAULT_MEASURE = "CONVERSION_RATE"  # default on first load for graphs
DEFAULT_DIMENSION = "STATE_CODE"  # default on first load for graphs
DEFAULT_HOVER_DATA = {  # default on first load for graphs
    "points": [
        {
            "curveNumber": 0,
            "x": "2019-12-30",
            "y": 0
        }
    ]
}
TEMPLATE = "flatly"
COLOR_PALETTE = px.colors.qualitative.Pastel

if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
