"""
Helper functions for the plotly app
"""

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from ..amodely import Amodely
from .lib import DATE


def draw_heading(text: str):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H3(text),
                ], style={"textAlign": "center"})
            ])
        )
    ])


def draw_text(text: str):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.P(text),
                ], style={"textAlign": "center"})
            ])
        )
    ])


def get_motor_graph(model: Amodely):
    """
    Returns the motor business dashboard graph based on the given dataframe.

    `model`
        The amodely model to use for the graph. Uses the model's current
        measure, dimension, and working dataframe to plot the grpah.
    """
    measure_title = " ".join(model.measure.lower().split("_")).title()
    dimension_title = " ".join(model.dimension.lower().split("_")).title()
    date_title = " ".join(DATE.lower().split("_")).title()
    title = f"{measure_title} vs. {date_title} ({dimension_title})"

    return px.line(
        model.df,
        x=DATE,
        y=model.measure.upper(),
        color=model.dimension.upper(),
        title=title,
        template="darkly",
        color_discrete_sequence=px.colors.qualitative.Dark24
    )


def draw_motor_graph(model: Amodely):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    dcc.Dropdown(
                        id="input-dimension",
                        options=[{"label": dim, "value": dim} for dim in
                                 model.dimensions],
                        value=model.dimension,
                        searchable=False,
                        clearable=False
                    )
                ], style={"width": "25%"}),
                dcc.Graph(
                    id="master-graph",
                    figure=get_motor_graph(model),
                    config={
                        "displayModeBar": False
                    }
                )
            ])
        )
    ])
