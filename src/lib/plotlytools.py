"""
Helper functions for the plotly app
"""

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ..amodely import Amodely
from .lib import DATE, STRUCTURE


def format_friendly(string: str) -> str:
    """
    Formats a string to be more read-friendly.

    Examples:
    >>> format_friendly("CONVERSION_RATE")
    Conversion Rate
    >>> format_friendly("SALES_PROPORTION")
    Sales Proportion
    """
    return " ".join(string.split("_")).title()


def get_title(model: Amodely) -> str:
    """
    Returns a string title based on the model's selected measure and dimension.
    """
    date_title = format_friendly(DATE)
    measure_title = format_friendly(model.measure)
    dimension_title = format_friendly(model.dimension)

    return f"{measure_title} vs. {date_title} ({dimension_title})"


def draw_card(contents, **kwargs) -> dbc.Card:
    """
    Returns a formatted card element.
    """
    return dbc.Card(
        dbc.CardBody([
            html.Div(contents, **kwargs)
        ])
    )


class Graph():
    def __init__(self, model: Amodely) -> None:
        """
        Initialises a graph with an Amodely model
        """
        self.model = model

    def get_figure(self) -> go.Figure:
        """
        Returns a graph figure based on the model dataframe.
        """
        raise NotImplementedError

    def draw_graph(self) -> html.Div:
        """
        Returns a formatted card element with a graph contained inside.
        """
        raise NotImplementedError

    def draw_graph_info(self) -> html.Div:
        """
        Returns a formatted card element with graph configurations and a
        description of the graph.
        """
        raise NotImplementedError

    def draw_graph_slider(self) -> html.Div:
        """
        Returns a formatted card element with a slider to control year.
        """
        raise NotImplementedError


class MasterGraph(Graph):
    def __init__(self, model: Amodely) -> None:
        """
        Initialises a master graph with an Amodely model
        """
        super().__init__(model)

    def get_figure(self) -> go.Figure:
        """
        Returns a master graph figure based on the model dataframe.

        The figure uses the model's selected measure, dimension, and working
        dataframe to plot the graph.
        """
        fig = px.line(
            self.model.df,
            x=DATE,
            y=self.model.measure,
            color=self.model.dimension,
            labels={  # use format friendly labels for the figure
                DATE: format_friendly(DATE),
                self.model.measure: format_friendly(self.model.measure),
                self.model.dimension: format_friendly(self.model.dimension)
            },
            title=get_title(self.model),
            template="flatly",
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig.update_layout({
            "title_font_size": 20,
            "margin_b": 40,  # bottom margin
            "margin_t": 40,  # tpp margin
        })

        return fig

    def draw_graph(self) -> html.Div:
        """
        Returns a formatted card element with a master graph contained inside.

        The figure uses the model's selected measure, dimension, and working
        dataframe to plot the graph.
        """
        return html.Div(
            draw_card(
                dcc.Graph(
                    id="master-graph",
                    figure=self.get_figure()
                )
            )
        )

    def draw_graph_slider(self) -> html.Div:
        """
        Returns a formatted card element with a slider to control year.
        """
        min_year = self.model.main_df[DATE].min().year
        max_year = self.model.main_df[DATE].max().year

        # 2019 is used as the value for the label "All" because the values have
        # to be equally spaced on the slider and the earliest recorded year is
        # 2020; so we use the value before that for the "All" option
        years = {year: str(year) for year in range(min_year, max_year+1)}
        years[2019] = "All"

        return html.Div(
            draw_card(
                dcc.Slider(
                    id="master-input-year",
                    min=2019,
                    max=max_year,
                    value=2019,
                    marks=years,
                    step=1
                )
            )
        )

    def draw_graph_info(self) -> html.Div:
        """
        Returns a formatted card element with graph configurations and a
        description of the graph.
        """
        return html.Div(
            draw_card([
                html.Div([
                    html.H5("Configuration"),
                    html.Label("Measure:"),
                    dcc.Dropdown(
                        id="master-input-measure",
                        value="CONVERSION_RATE",  # defaults to conversion rate
                        options=[
                            {
                                "label": format_friendly(measure),
                                "value": measure
                            } for measure in STRUCTURE.keys()
                        ],
                        clearable=False  # input can't be empty
                    ),
                    html.Br(),
                    html.Label("Dimension:"),
                    dcc.Dropdown(
                        id="master-input-dimension",
                        value=self.model.dimension,  # defaults to selected
                                                     # dimension
                        options=[
                            {"label": format_friendly(dim), "value": dim}
                            for dim in self.model.dimensions
                        ],
                        clearable=False  # input can't be empty
                    ),
                    html.Br(),
                    dcc.Checklist(
                        id="master-input-bad-cats",
                        value=["bad-cats"],
                        options=[
                            {"label": " Remove bad* categories",
                             "value": "bad-cats"}
                        ]
                    ),
                    html.Hr()
                ], className="dropdowns"),
                html.P("Extra notes: the data has been resampled as a weekly "
                       "frequency, where Quote Date is the start of each "
                       "respective week (Monday)."),
                html.P("*Bad categories (<= 100 entries) can cause issues "
                       "with the autogenerated axes and the anomaly detection "
                       "algorithm and are filtered out by default.")
            ])
        )


class AnomalyGraph(Graph):
    def __init__(self, model: Amodely) -> None:
        """
        Initialises an anomaly graph with an Amodely model
        """
        super().__init__(model)

    def get_figure(self) -> go.Figure:
        fig = px.line(
            self.model.df,
            x=DATE,
            y=self.model.measure,
            color=self.model.dimension,
            template="flatly",
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        for category in self.model.categories:
            df = self.model.anomalies_[
                    self.model.anomalies_[self.model.dimension] == category
                ]

            fig.add_trace(go.Scatter(
                x=df[DATE],
                y=df[self.model.measure],
                mode="markers"
            ))

        fig.update_layout({
            "title_font_size": 20,
            "margin_b": 40,  # bottom margin
            "margin_t": 40,  # top margin
        })

        return fig

    def draw_graph(self) -> html.Div:
        return html.Div([
            draw_card(
                dcc.Graph(
                    id="anomaly-graph",
                    figure=self.get_figure()
                )
            )
        ])
