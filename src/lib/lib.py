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

TEMPLATE = "flatly"
COLOR_PALETTE = px.colors.qualitative.Pastel
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
DEFAULT_FIGURE_LAYOUT = {
    "title": {
        "font_size": 20,
    },
    "margin": {
        "b": 40,  # bottom margin
        "t": 40,  # top margin
    },
}
# HOVER_DATA:
#   "average": add the average of the hovered data point on the anomaly subplot
#   "point": add the hovered data point on the anomaly subplot
# TICK_FORMAT:
#   ",.0f" separate thousands with a comma instead of a "k"
#   ".1%"  show percentages instead of decimals
GRAPH_CONFIG = {
    "QUOTE_VOLUME": {
        "HOVER_DATA": "average",
        "TICK_FORMAT": ",.0f"
    },
    "SALES_VOLUME": {
        "HOVER_DATA": "average",
        "TICK_FORMAT": ",.0f"
    },
    "QUOTE_PROPORTION": {
        "HOVER_DATA": "point",
        "TICK_FORMAT": ".2%"
    },
    "SALES_PROPORTION": {
        "HOVER_DATA": "point",
        "TICK_FORMAT": ".2%"
    },
    "CONVERSION_RATE": {
        "HOVER_DATA": "point",
        "TICK_FORMAT": ".2%"
    }
}

if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
