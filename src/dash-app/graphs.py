"""
This module provides helper functions for the Dash app.
"""

from dash import dash_table
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from ..amodely import Amodely
from ..lib import pipelines as pl
from ..lib.lib import COLOR_PALETTE, COLOR_PARAMS, DATE, \
                      DEFAULT_FIGURE_LAYOUT, GRAPH_CONFIG, STRUCTURE, TEMPLATE


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


class Graph:
    """
    Abstract class used to contain an Amodely model and for creating figures
    and drawing graphs
    """
    def __init__(self, model: Amodely) -> None:
        """
        Initialises a graph with an Amodely model
        """
        self.model = model

    def get_measure_dropdown(self, config_id: str) -> dcc.Dropdown:
        """
        Returns a dropdown to configure the measure variable.

        Parameters
        ----------
        config_id
            The id to assign to the Dropdown element.
        """
        return dcc.Dropdown(
            id=config_id,
            value="CONVERSION_RATE",  # defaults to conversion rate
            options=[{"label": format_friendly(measure), "value": measure} for
                     measure in STRUCTURE.keys()],
            clearable=False  # config can't be empty
        )

    def get_dimension_dropdown(self, config_id: str) -> dcc.Dropdown:
        """
        Returns a dropdown to configure the dimension variable.

        Parameters
        ----------
        config_id
            The id to assign to the Dropdown element.
        """
        return dcc.Dropdown(
            id=config_id,
            value="ALL",  # defaults to selecting all dimensions
            options=[{"label": "All", "value": "ALL"},  # add "ALL" as option
                     *[{"label": format_friendly(dim), "value": dim} for dim in
                       self.model.dimensions]],
            clearable=False  # config can't be empty
        )

    def get_filter_dimension_dropdown(self, config_id: str) -> dcc.Dropdown:
        """
        Returns a dropdown to select the filtered dimension.

        Parameters
        ----------
        config_id
            The id to assign to the Dropdown element.
        """
        return dcc.Dropdown(
            id=config_id,
            value="",  # no filter applied by default
            options=[{"label": format_friendly(dim), "value": dim} for dim in
                     self.model.dimensions],
        )

    def get_filter_category_dropdown(self, config_id: str) -> dcc.Dropdown:
        """
        Returns a multi-select dropdown to configure filtered categories.

        Parameters
        ----------
        config_id
            The id to the assign to the multi-select Dropdown element.
        """
        return dcc.Dropdown(
            id=config_id,
            value=[],  # no category selected by default
            options=[],  # no options by default
            multi=True
        )

    def get_figure(self) -> go.Figure:
        """
        Returns a Plot.ly graph figure based on the model dataframe.
        """
        raise NotImplementedError

    def draw_graph(self, graph_id: str) -> html.Div:
        """
        Returns a formatted card element containing a graph.

        Parameters
        ----------
        graph_id
            The id to assign to the Dropdown element.
        """
        return html.Div(
            draw_card(
                dcc.Graph(
                    id=graph_id,
                    figure=self.get_figure()
                )
            )
        )

    def draw_graph_config(self) -> html.Div:
        """
        Returns a formatted card element with graph configurations and a
        description of the graph.
        """
        raise NotImplementedError

    def draw_graph_slider(self, slider_id: str) -> html.Div:
        """
        Returns a formatted card element with a slider to control the quote
        year.

        Parameters
        ----------
        config_id
            The id to assign to the Slider element.
        """
        min_year = self.model.main_df[DATE].min().year
        max_year = self.model.main_df[DATE].max().year

        # 2020 is the earliest recorded year so use 2019 as the value for the
        # label "All"
        years = {year: str(year) for year in range(min_year, max_year+1)}
        years[2019] = "All"

        return html.Div(
            draw_card(
                dcc.Slider(
                    id=slider_id,
                    min=2019,
                    max=max_year,
                    value=2019,
                    marks=years,
                    step=1
                )
            )
        )


class MasterGraph(Graph):
    """
    MasterGraph is a Graph used for the master dashboard
    """
    def __init__(self, model: Amodely) -> None:
        """
        Initialises a master graph with an Amodely model
        """
        super().__init__(model)

    def get_config_checklist(self, config_id: str) -> dcc.Checklist:
        """
        Returns a checklist to configure extra settings.

        Parameters
        ----------
        config_id
            The id to assign to the Checklist element.
        """
        return dcc.Checklist(
            id=config_id,
            value=["bad-cats"],  # default to filtering out bad categories
            options=[
                {"label": " Remove categories with < 100 entries",
                 "value": "bad-cats"}]
        )

    def get_figure(self) -> go.Figure:
        """
        Returns a Plot.ly master graph figure based on the model dataframe.

        The figure uses the model's selected measure, dimension, and working
        dataframe to plot the graph. It graphs the model's selected measure
        against quote date, and plots a separate line for each dimension
        category.
        """
        # params that are common between selecting 1 dimension vs. selecting
        # ALL dimensions
        params = dict(
            data_frame=self.model.df,
            x=DATE,
            y=self.model.measure,
            title=get_title(self.model),
            **COLOR_PARAMS
        )

        if self.model.dimension == "ALL":  # select ALL dimensions
            fig = px.line(
                **params,
                labels={  # use format friendly labels for figure
                    DATE: format_friendly(DATE),
                    self.model.measure: format_friendly(self.model.measure)
                },
            )
        else:  # select a particular dimension
            fig = px.line(
                **params,
                color=self.model.dimension,
                labels={  # use format friendly labels for the figure
                    DATE: format_friendly(DATE),
                    self.model.measure: format_friendly(self.model.measure),
                    self.model.dimension: format_friendly(self.model.dimension)
                }
            )

        fig.update_layout(dict(
            **DEFAULT_FIGURE_LAYOUT,
            yaxis=dict(
                tickformat=GRAPH_CONFIG[self.model.measure]["TICK_FORMAT"]
            )
        ))

        return fig

    def draw_graph_config(self, config_ids: tuple[str]) -> html.Div:
        """
        Returns a formatted card element with graph configurations.

        Parameters
        ----------
        config_ids
            A 4-tuple of ids to assign to the measure Dropdown, dimension
            Dropdown, filter dimension Dropdown, filter category Dropdown, and
            Checklist respectively.
        """
        return html.Div(
            draw_card([
                html.Div([
                    html.H5("Configuration"),
                    html.Label("Measure:"),
                    self.get_measure_dropdown(config_ids[0]),
                    html.Br(),
                    html.Label("Dimension:"),
                    self.get_dimension_dropdown(config_ids[1]),
                    html.Br(),
                    html.Label("Filter for Dimension:"),
                    self.get_filter_dimension_dropdown(config_ids[2]),
                    html.Br(),
                    html.Label("Filter for Category(s):"),
                    self.get_filter_category_dropdown(config_ids[3]),
                    html.Br(),
                    self.get_config_checklist(config_ids[4]),
                ], className="dropdowns")
            ])
        )


class AnomalyGraph(Graph):
    def __init__(self, model: Amodely) -> None:
        """
        Initialises an anomaly graph with an Amodely model
        """
        super().__init__(model)

    def get_figure(self, max_size: int = 30, sig_level: float = 0.05
                   ) -> go.Figure:
        """
        Returns a Plot.ly anomaly graph figure based on the model dataframe.

        The figure uses the model's selected measure, dimension, and working
        dataframe to plot the graph. It graphs the model's selected measure
        against quote date, and plots a separate line for each dimension
        category.

        The anomaly detection algorithm transforms the lines to be stationary.
        The transformations also tend to be normally distributed, so a simple
        confidence interval can be used to determine outliers; the number of
        standard deviations from the mean for each line is also plotted as
        marker size.

        Parameters
        ----------
        max_size
            Maximum bubble size. The default is 30.
        sig
            The significance level to use to determine the outliers. The
            default is 0.05.
        """
        if self.model.dimension == "ALL":
            fig = px.line(
                title=get_title(self.model),
                labels={  # use format friendly labels for the figure
                    DATE: format_friendly(DATE),
                    self.model.measure: format_friendly(self.model.measure)
                },
                **COLOR_PARAMS
            )

            # create dataframe of data & standard deviations
            df = self.model.anomalies_
            stds = df["STANDARD_DEVIATIONS"]
            # create dataframe of outliers & outlier standard deviations
            df_outliers = pl.FilterOutliers(sig_level).fit_transform(df)
            stds_outliers = abs(df_outliers["STANDARD_DEVIATIONS"])

            scatter_params = dict(  # params common to scatter & bubble plot
                legendgroup=1,  # group scatter and bubble plot traces together
                showlegend=False,  # hide both legends
                line_color=COLOR_PALETTE[0]  # use same color
            )

            # add scatter plot
            fig.add_trace(go.Scatter(
                x=df[DATE],
                y=df[self.model.measure],
                **scatter_params,
                name="All",
                mode="lines",  # scatter plot mode
                customdata=stds,  # used for hovering
                hovertemplate=f"{format_friendly(DATE)}: " + "%{x} <br>"
                              f"{format_friendly(self.model.measure)}: " +
                              "%{y} <br>"
                              "Standard Deviations: %{customdata}"
                              "<extra></extra>"
            ))

            # add bubble chart (outliers only)
            fig.add_trace(go.Scatter(
                x=df_outliers[DATE],
                y=df_outliers[self.model.measure],
                **scatter_params,
                mode="markers",  # bubble plot mode
                marker={
                    "size": stds_outliers,
                    # hide bubbles (sizeref=0) if there aren't any outliers
                    "sizeref": (0 if stds_outliers.empty else
                                (2*max(stds_outliers) / (max_size**2))),
                    "sizemin": 4,  # min size
                    "sizemode": "area"  # required for sizeref to work
                },
                hoverinfo="skip"  # hide hover
            ))

        else:
            fig = px.scatter(
                title=get_title(self.model),
                labels={  # use format friendly labels for the figure
                    DATE: format_friendly(DATE),
                    self.model.measure: format_friendly(self.model.measure),
                    self.model.dimension: format_friendly(self.model.dimension)
                },
                **COLOR_PARAMS
            )

            # filter out bad categories
            categories = sorted(set(self.model.categories) -
                                set(self.model.bad_categories))

            for i, category in enumerate(categories):
                # for each category, add a scatter and bubble trace

                # create dataframe of data & standard deviations for the
                # current category
                df = pl.FilterCategory(self.model.dimension, [category]) \
                       .fit_transform(self.model.anomalies_)
                stds = df["STANDARD_DEVIATIONS"]

                # create dataframe of outliers & outlier standard deviations
                df_outliers = pl.outliers_pipeline(self.model.dimension,
                                                   category, sig_level) \
                                .fit_transform(self.model.anomalies_)
                stds_outliers = abs(df_outliers["STANDARD_DEVIATIONS"])

                fig_params = dict(
                    legendgroup=str(i),  # group scatter and bubble plot traces
                    # same line color for scatter and bubble plot traces
                    line_color=COLOR_PALETTE[i % len(COLOR_PALETTE)],
                )

                # add scatter plot
                fig.add_trace(go.Scatter(
                    x=df[DATE],
                    y=df[self.model.measure],
                    **fig_params,
                    name=category,
                    # same line color as bubble plot for the same trace
                    mode="lines",  # scatter plot mode
                    customdata=stds,
                    hovertemplate=f"{format_friendly(self.model.dimension)}: "
                                  f"{category} <br>"
                                  f"{format_friendly(DATE)}: " + "%{x} <br>"
                                  f"{format_friendly(self.model.measure)}: " +
                                  "%{y} <br>"
                                  "Standard Deviations: %{customdata}"
                                  "<extra></extra>"
                ))

                # add bubble chart (outliers only)
                fig.add_trace(go.Scatter(
                    x=df_outliers[DATE],
                    y=df_outliers[self.model.measure],
                    **fig_params,
                    showlegend=False,  # use scatter plot legend, hide this one
                    mode="markers",  # bubble plot mode
                    marker={
                        "size": stds_outliers,
                        "sizeref": (0 if stds_outliers.empty else \
                                    (2*max(stds_outliers) / (max_size**2))),
                        "sizemin": 4,
                        "sizemode": "area",
                    },
                    hoverinfo="skip"
                ))

        fig.update_layout({
            **DEFAULT_FIGURE_LAYOUT,
            "legend": {
                "title": format_friendly(self.model.dimension),
            },
            "xaxis": {
                "title": format_friendly(DATE)
            },
            "yaxis": {
                "tickformat": GRAPH_CONFIG[self.model.measure]["TICK_FORMAT"],
                "title": format_friendly(self.model.measure)
            }
        })

        return fig

    def get_sub_figure(self, hover_data: dict) -> go.Figure:
        """
        Returns a Plot.ly anomaly graph sub figure based on the hovered data
        point in the main graph figure.

        The figure provides daily data points for the hovered data point's week
        for that particular category.

        Parameters
        ----------
        hover_data
            The Plot.ly hover data of the hovered data point.
        """
        # divide by 2 as there are 2 curves for each category; one for the
        # scatter plot and one for the bubble plot
        category = self.model.categories[
            hover_data["points"][0]["curveNumber"] // 2
        ]

        DATE_FORMAT = "%Y-%m-%d"  # 2020-12-30
        DATE_FORMAT_FRIENDLY = "%b %d, %Y"  # Dec 30, 2020
        # get the start and end date of the hovered week
        start_date = hover_data["points"][0]["x"]
        end_date = (datetime.strptime(start_date, DATE_FORMAT) +
                    timedelta(days=6)).strftime(DATE_FORMAT)

        # format start and end date for title
        title_start_date = datetime.strptime(start_date, DATE_FORMAT) \
                                   .strftime(DATE_FORMAT_FRIENDLY)
        title_end_date = datetime.strptime(end_date, DATE_FORMAT) \
                                 .strftime(DATE_FORMAT_FRIENDLY)

        # filter dataframe for the hovered week
        df = self.model.df[(self.model.df[DATE] >= start_date) &
                           (self.model.df[DATE] <= end_date)]

        if self.model.dimension == "ALL":
            df2 = df
        else:
            df2 = df[df[self.model.dimension] == category]

        fig = px.line(
            df2,
            x=DATE,
            y=self.model.measure,
            title=f"{title_start_date} to {title_end_date} ({category})",
            labels={  # use format friendly labels for figure
                DATE: format_friendly(DATE),
                self.model.measure: format_friendly(self.model.measure)
            },
            **COLOR_PARAMS
        )

        if GRAPH_CONFIG[self.model.measure]["HOVER_DATA"] == "point":
            # add the hovered data point to the anomaly subplot
            hover_data = hover_data["points"][0]["y"]
        elif GRAPH_CONFIG[self.model.measure]["HOVER_DATA"] == "average":
            # add the average of the hovered data point to the anomaly subplot
            hover_data = hover_data["points"][0]["y"] / 6

        # add the hovered data as a line
        fig.add_shape(
            type="line",
            x0=start_date,
            x1=end_date,
            y0=hover_data,
            y1=hover_data,
            xref="x",
            yref="y",
            line=dict(
                color=COLOR_PALETTE[0]
            )
        )

        fig.update_layout(dict(
            **DEFAULT_FIGURE_LAYOUT,
            xaxis=dict(
                tickmode="linear"
            ),
            yaxis=dict(
                tickformat=GRAPH_CONFIG[self.model.measure]["TICK_FORMAT"]
            )
        ))

        return fig

    def draw_sub_graph(self, graph_id: str, hover_data: dict) -> html.Div:
        """
        Returns a formatted card element containing an anomaly sub graph.

        Parameters
        ----------
        graph_id
            The id to assign to the Dropdown element.
        hover_data
            The Plot.ly hover data of the hovered data point.
        """
        return html.Div([
            draw_card(
                dcc.Graph(
                    id=graph_id,
                    figure=self.get_sub_figure(hover_data)
                )
            )
        ])

    def draw_graph_config(self, config_ids: tuple[str]) -> html.Div:
        """
        Returns a formatted card element with graph configurations and a
        description of the graph.

        Parameters
        ----------
        config_ids
            A 5-tuple of ids to assign to the measure Dropdown, dimension
            Dropdown, filter dimension Dropdown, filter category Dropdown,
            and confidence interval Slider respectively.
        """
        return html.Div(
            draw_card([
                html.Div([
                    html.H5("Configuration"),
                    html.Label("Measure:"),
                    self.get_measure_dropdown(config_ids[0]),
                    html.Br(),
                    html.Label("Dimension:"),
                    self.get_dimension_dropdown(config_ids[1]),
                    html.Br(),
                    html.Label("Filter for Dimension:"),
                    self.get_filter_dimension_dropdown(config_ids[2]),
                    html.Br(),
                    html.Label("Filter for Category(s):"),
                    self.get_filter_category_dropdown(config_ids[3]),
                    html.Br(),
                    html.Label("Confidence Interval:"),
                    self.draw_conf_int_slider(config_ids[4]),
                    # html.Br(),
                    # html.P("80% ≈ 1.28 standard deviations"),
                    # html.P("90% ≈ 1.64 standard deviations"),
                    # html.P("95% ≈ 1.96 standard deviations")
                ], className="dropdowns"),
            ])
        )

    def draw_conf_int_slider(self, slider_id: str) -> html.Div:
        """
        Returns a formatted card element with a slider to control the
        confidence interval for the anomaly detection algorithm.

        Parameters
        ----------
        slider_id
            The id to assign to the Slider element.
        """
        # 80% up to 97.5% in intervals of 2.5%
        intervals = np.linspace(80, 100, 8, endpoint=False) / 100
        marks = {interv: f"{interv*100}%" for interv in intervals}

        return html.Div(
            draw_card(
                dcc.Slider(
                    id=slider_id,
                    min=intervals[0],
                    max=intervals[-1],
                    value=intervals[-2],  # default to 95% confidence interval
                    marks=marks,
                    step=0.025
                )
            )
        )

    def get_table(self, config_id: str, sig: float = 0.05
                  ) -> dash_table.DataTable:
        df = self.model.anomalies_.copy()
        df[DATE] = df[DATE].dt.date
        df.drop(["ANOMALY"], axis="columns", inplace=True)
        df = pl.FilterOutliers(sig).fit_transform(df)

        table = dash_table.DataTable(
            id=config_id,
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            export_format="csv"
        )

        return table

    def draw_table(self, table_id: str, sig: float = 0.05) -> html.Div:
        return html.Div(
            self.get_table(table_id, sig)
        )
