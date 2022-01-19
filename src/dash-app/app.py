"""
################################### app.py ####################################
This module is used to initialise and run the Dash app. It contains the app
layout and app callbacks.
###############################################################################
"""


import dash
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from .models import master, anomaly
from ..lib import pipelines as pl
from ..lib import plotlytools as pt


load_figure_template("flatly")
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="Amodely Dashboard")

app.layout = html.Div([
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    pt.draw_card(
                        html.H1("Master Dashboard"),
                        className="heading")
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row(
                        dbc.Col(pt.MasterGraph(master).draw_graph())
                    ),
                    dbc.Row(
                        dbc.Col(pt.MasterGraph(master).draw_graph_slider())
                    )
                ], width=9),
                dbc.Col([
                    pt.MasterGraph(master).draw_graph_info()
                ], width=3)
            ]),
            dbc.Row([
                dbc.Col([
                    pt.draw_card(
                        html.H1("Anomaly Detection Dashboard"),
                        className="heading")
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    pt.AnomalyGraph(anomaly).draw_graph()
                ], width=9),
                dbc.Col([html.Div(id="hover")], width=3)
            ])
        ])
    ], className="dashboard")
], className="webpage")


@app.callback(
    Output("hover", "children"),
    Input("master-graph", "hoverData")
)
def hover_data(hover):
    return str(hover)


@app.callback(
    Output("master-graph", "figure"),
    Input("master-input-measure", "value"),
    Input("master-input-dimension", "value"),
    Input("master-input-year", "value"),
    Input("master-input-bad-cats", "value")
)
def update_master_graph(measure: str, dimension: str, year: int,
                        bad_cats: str):
    """
    Updates the master business dashboard graph.

    `measure`
        The measure to filter for. Options can be found in `./lib/lib.py` in
        the `STRUCTURE` dictionary.
    `dimension`
        The dimension to filter for.
    """
    # debug
    print(f"Config: {measure}, {dimension}, {year}, {bad_cats}")

    master.reset_working()

    # update model's parameters if they have changed
    if measure != master.measure:
        master.measure = measure
    if dimension != master.dimension:
        master.dimension = dimension
    if year != 2019:  # 2019 => use all years (see explanation in plotlytools)
        # filter for the given year
        master.df = pl.FilterYear(year).fit_transform(master.df)
    if bad_cats:
        filt = master.df[master.dimension].value_counts() <= 100
        bad_categories = filt.drop(filt.index[~filt]).index
    else:
        bad_categories = []

    master.df = \
        pl.dimension_pipeline(master.measure,
                              master.dimension,
                              bad_categories) \
          .fit_transform(master.df)

    return pt.MasterGraph(master).get_figure()


if __name__ == "__main__":
    app.run_server(debug=True)
