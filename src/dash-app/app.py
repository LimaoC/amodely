"""
This module is used to initialise and run the Dash app. It contains the app
layout and app callbacks.
"""


import dash
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go

from .models import master, anomaly
from ..lib import pipelines as pl
from . import graphs
from ..lib.lib import DEFAULT_HOVER_DATA


# initialise app
load_figure_template("flatly")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
                title="Amodely Dashboard")

# ------------------------------- APP LAYOUT -------------------------------- #

master_graph = graphs.MasterGraph(master)
anomaly_graph = graphs.AnomalyGraph(anomaly)

app.layout = html.Div([
    dbc.Card([
        dbc.CardBody([
            dbc.Row([  # master graph heading
                dbc.Col([
                    graphs.draw_card(
                        html.H1("Master Dashboard"),
                        className="heading")
                ], width=12)
            ]),
            dbc.Row([  # master graph row
                dbc.Col([
                    dbc.Row(dbc.Col(
                        master_graph.draw_graph("master-graph")
                    )),
                    dbc.Row(dbc.Col(
                        master_graph.draw_graph_slider("master-input-year")
                    )),
                ], width=9),
                dbc.Col([
                    master_graph.draw_graph_config((
                        "master-input-measure",
                        "master-input-dimension",
                        "master-input-filter-dimension",
                        "master-input-filter-category",
                        "master-input-checklist"
                    ))
                ], width=3)
            ]),
            dbc.Row([  # anomaly graph heading
                dbc.Col([
                    graphs.draw_card(
                        html.H1("Anomaly Detection Dashboard"),
                        className="heading")
                ], width=12)
            ]),
            dbc.Row([  # anomaly graph row
                dbc.Col([
                    dbc.Row(dbc.Col(
                        anomaly_graph.draw_graph("anomaly-graph")
                    )),
                    dbc.Row(dbc.Col(
                        anomaly_graph.draw_graph_slider("anomaly-input-year")
                    ))
                ], width=6),
                dbc.Col([
                    anomaly_graph.draw_sub_graph("anomaly-sub-graph",
                                                 DEFAULT_HOVER_DATA)
                ], width=3),
                dbc.Col([
                    anomaly_graph.draw_graph_config((
                        "anomaly-input-measure",
                        "anomaly-input-dimension",
                        "anomaly-input-filter-dimension",
                        "anomaly-input-filter-category"
                    ))
                ], width=3)
            ])
        ])
    ], className="dashboard")
], className="webpage")

# ------------------------------ APP CALLBACKS ------------------------------ #


@app.callback(
    Output("anomaly-sub-graph", "figure"),
    Input("anomaly-graph", "hoverData"),
    Input("anomaly-input-filter-dimension", "value"),
    Input("anomaly-input-filter-category", "value")
)
def update_hover(hover_data: dict, filter_dimension: str,
                 filter_categories: list) -> go.Figure:
    """
    Callback to update the anomaly sub-graph on hover.

    Parameters
    ----------
    hover_data
        The hovered data.
    filter_dimension
        The dimension to filter for.
    filter_categories
        A list of categories to filter for.

    Returns
    -------
    The updated anomaly sub-graph Figure.
    """
    anomaly.reset_working()

    # filter for the categories specified
    if filter_categories:
        anomaly.df = pl.FilterCategory(filter_dimension, filter_categories) \
                       .fit_transform(anomaly.df)

    anomaly.df = pl.dimension_pipeline(anomaly.measure, anomaly.dimension,
                                       frequency="D",
                                       bad_categories=anomaly.bad_categories) \
                   .fit_transform(anomaly.df)

    if hover_data is None:
        hover_data = DEFAULT_HOVER_DATA

    return graphs.AnomalyGraph(anomaly).get_sub_figure(hover_data)


@app.callback(
    Output("anomaly-graph", "figure"),
    Output("anomaly-input-filter-category", "options"),
    Input("anomaly-input-measure", "value"),
    Input("anomaly-input-dimension", "value"),
    Input("anomaly-input-year", "value"),
    Input("anomaly-input-filter-dimension", "value"),
    Input("anomaly-input-filter-category", "value"),
)
def update_anomaly_graph(measure: str, dimension: str, year: int,
                         filter_dimension: str, filter_categories: list
                         ) -> go.Figure:
    """
    Callback to update the anomaly graph.

    Parameters
    ----------
    measure
        The measure to select. A list of options can be found in
        /src/lib/lib.py.
    dimension
        The dimension to select. Options are determined from the dataframe
        columns.
    year
        The year to select, or 2019 to select all years (see explanation in
        /src/dash-app/graphs.py).
    filter_dimension
        The dimension to filter for.
    filter_categories
        A list of categories to filter for.

    Returns
    -------
    A 2-tuple of the updated anomaly graph Figure and a list of categories to
    display on the "Filter for Categories" dropdown.
    """
    print(f"Anomaly: {measure}, {dimension}, {year}")  # debug

    anomaly.reset_working()

    # update model's parameters if they have changed
    if measure != anomaly.measure:
        anomaly.measure = measure
    if dimension != anomaly.dimension:
        anomaly.dimension = dimension

    # remove bad categories from "Filter for Dimension" dropdown if specified
    filter_category_options = sorted(set(master.main_df[filter_dimension])) \
        if filter_dimension else []

    # filter for the categories specified
    if filter_categories:
        anomaly.df = pl.FilterCategory(filter_dimension, filter_categories) \
                       .fit_transform(anomaly.df)

    # apply any changes to measure, dimension, and bad categories to the
    # anomaly working dataframe
    anomaly.df = pl.dimension_pipeline(anomaly.measure, anomaly.dimension,
                                       bad_categories=anomaly.bad_categories) \
                   .fit_transform(anomaly.df)
    if filter_categories:
        anomaly.detect_anomalies(method="stl",
                                 filter_dimension=filter_dimension,
                                 filter_categories=filter_categories)
    else:
        anomaly.detect_anomalies(method="stl")

    if year != 2019:  # 2019 => use all years (see explanation in plotlytools)
        # filter for the given year
        anomaly.df = pl.FilterYear(year).fit_transform(anomaly.df)
        anomaly.anomalies_ = pl.FilterYear(year) \
                               .fit_transform(anomaly.anomalies_)

    return (
        graphs.AnomalyGraph(anomaly).get_figure(),
        [{"label": cat, "value": cat} for cat in filter_category_options]
    )


@app.callback(
    Output("master-graph", "figure"),
    Output("master-input-filter-category", "options"),
    Input("master-input-measure", "value"),
    Input("master-input-dimension", "value"),
    Input("master-input-year", "value"),
    Input("master-input-filter-dimension", "value"),
    Input("master-input-filter-category", "value"),
    Input("master-input-checklist", "value")
)
def update_master_graph(measure: str, dimension: str, year: int,
                        filter_dimension: str, filter_categories: list,
                        checklist: str) -> tuple[go.Figure, list]:
    """
    Callback to update the master graph.

    Parameters
    ----------
    measure
        The measure to select. A list of options can be found in
        /src/lib/lib.py.
    dimension
        The dimension to select. Options are determined from the dataframe
        columns.
    year
        The year to select, or 2019 to select all years (see explanation in
        /src/dash-app/graphs.py).
    filter_dimension
        The dimension to filter for.
    filter_categories
        A list of categories to filter for.
    checklist
        A list of checklist options. Options include "bad-cats"

    Returns
    -------
    A 2-tuple of the updated master graph Figure and a list of categories to
    display on the "Filter for Categories" dropdown.
    """
    print(f"Master: {measure}, {dimension}, {year}, {checklist}")  # debug

    master.reset_working()

    # update model's parameters if they have changed
    if measure != master.measure:
        master.measure = measure
    if dimension != master.dimension:
        master.dimension = dimension

    # remove bad categories from master graph if specified
    bad_categories = master.bad_categories if "bad-cats" in checklist else []

    # remove bad categories from "Filter for Dimension" dropdown if specified
    filter_category_options = sorted(set(master.main_df[filter_dimension])) \
        if filter_dimension else []

    # filter for the categories specified
    if filter_categories:
        master.df = pl.FilterCategory(filter_dimension, filter_categories) \
                      .fit_transform(master.df)

    # apply any changes to measure, dimension, and bad categories to the master
    # working dataframe
    master.df = pl.dimension_pipeline(master.measure, master.dimension,
                                      bad_categories=bad_categories) \
                  .fit_transform(master.df) \

    # filter for the given year; 2019 => select all years
    if year != 2019:
        master.df = pl.FilterYear(year).fit_transform(master.df)

    return (
        graphs.MasterGraph(master).get_figure(),
        [{"label": cat, "value": cat} for cat in filter_category_options]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
