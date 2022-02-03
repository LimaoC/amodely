"""
This file contains constants necessary for the model and dashboard to function.
"""


import plotly.express as px


# ----------------------------- DATA CONSTANTS ------------------------------ #

DATASET_NAME = "dataset.xlsx"
DATE = "QUOTE_DATE"  # name of quote date column

# STRUCTURE contains measure variables as keys, which are themselves
# dictionaries containing the aggregation options used for each measure
# variable. See the CollapseDimensions transformer in /src/lib/pipelines.py.
STRUCTURE = dict(
    QUOTE_VOLUME=dict(
        QUOTE_COUNT="sum"
    ),
    SALES_VOLUME=dict(
        SALES_COUNT="sum"
    ),
    QUOTE_PROPORTION=dict(
        QUOTE_COUNT="sum"
    ),
    SALES_PROPORTION=dict(
        SALES_COUNT="sum"
    ),
    CONVERSION_RATE=dict(
        QUOTE_COUNT="sum",
        SALES_COUNT="sum"
    )
)

# ----------------------- PLOTLY DASHBOARD CONSTANTS ------------------------ #

TEMPLATE = "flatly"
COLOR_PALETTE = px.colors.qualitative.Pastel
COLOR_PARAMS = dict(  # for plot.ly graphs
    template=TEMPLATE,
    color_discrete_sequence=COLOR_PALETTE
)
DEFAULT_MEASURE = "CONVERSION_RATE"  # default on first load for graphs
DEFAULT_DIMENSION = "ALL"  # default on first load for graphs
DEFAULT_HOVER_DATA = dict(  # default on first load for graphs
    points=[dict(
        curveNumber=0,
        x="2019-12-30",
        y=0
    )]
)
DEFAULT_FIGURE_LAYOUT = dict(  # for plot.ly figures
    title=dict(
        font_size=20
    ),
    margin=dict(
        b=40,  # bottom margin
        t=40  # top margin
    )
)
# HOVER_DATA:
#   "average": add the average of the hovered data point on the anomaly subplot
#   "point": add the hovered data point on the anomaly subplot
# TICK_FORMAT:
#   ",.0f" separate thousands with a comma instead of a "k"
#   ".1%"  show percentages instead of decimals
GRAPH_CONFIG = dict(
    QUOTE_VOLUME=dict(
        HOVER_DATA="average",
        TICK_FORMAT=",.0f"
    ),
    SALES_VOLUME=dict(
        HOVER_DATA="average",
        TICK_FORMAT=",.0f"
    ),
    QUOTE_PROPORTION=dict(
        HOVER_DATA="point",
        TICK_FORMAT=".2%"
    ),
    SALES_PROPORTION=dict(
        HOVER_DATA="point",
        TICK_FORMAT=".2%"
    ),
    CONVERSION_RATE=dict(
        HOVER_DATA="point",
        TICK_FORMAT=".2%"
    )
)

if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
