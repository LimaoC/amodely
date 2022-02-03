## graphs.py

This module contains the graphs and configurations used by the Dash app.

There are two main Graphs - the MasterGraph (for the master dashboard) and the AnomalyGraph (for the anomaly detection dashboard). They are independent from each other on the dashboard (i.e. they are separate copies of the data). Each class contains relevant methods to render and generate the graphs, configurations, etc. on the dashboard.

---

### `format_friendly(string: str) -> str`

Formats a string to be more read-friendly.

Examples:
```python
>>> format_friendly("CONVERSION_RATE")
Conversion Rate
>>> format_friendly("SALES_PROPORTION")
Sales Proportion
```

### `get_title(model: Amodely) -> str`

Returns a string title based on the model's selected measure and dimension.

### `draw_card(contents, **kwargs) -> dbc.Card`

Returns a formatted Card element.

Parameters
- `contents` <br /> The contents of the Card element.
- `**kwargs` <br /> Arbitrary keyword arguments to attach to the Div.

### `Graph()`

Abstract class used to contain an Amodely model and for creating figures and drawing graphs

#### `Graph().__init__(self, model: Amodely)`

Initialises a graph with an `Amodely` model.

#### `Graph().get_measure_dropdown(self, config_id: str) -> dcc.Dropdown`

Returns a dropdown to configure the measure variable.

Parameters
- `config_id` <br /> The id to assign to the Dropdown element.

#### `Graph().get_dimension_dropdown(self, config_id: str) -> dcc.Dropdown`

Returns a dropdown to configure the dimension variable.

Parameters
- `config_id` <br /> The id to assign to the Dropdown element.

#### `Graph().get_filter_dimension_dropdown(self, config_id: str) -> dcc.Dropdown`

Returns a dropdown to select the filtered dimension.

Parameters
- `config_id` <br /> The id to assign to the Dropdown element.

#### `Graph().get_filter_category_dropdown(self, config_id: str) -> dcc.Dropdown`

Returns a multi-select dropdown to configure filtered categories.

Parameters
- `config_id` <br /> The id to assign to the multi-select Dropdown element.

#### `Graph().get_figure(self) -> go.Figure`

Returns a Plot.ly graph figure based on the model dataframe.

#### `Graph().draw_graph(self, graph_id: str) -> html.Div`

Returns a formatted card element containing a graph.

Parameters
- `config_id` <br /> The id to assign to the Dropdown element.

#### `Graph().draw_graph_config(self) -> html.Div`

Returns a formatted Card element with graph configurations and a description of the graph.

#### `Graph().draw_graph_slider(self, slider_id: str) -> html.Div`

Returns a formatted Card element with a slider to control the quote year.

Parameters
- `config_id` <br /> The id to assign to the Slider element.

### `MasterGraph(Graph)`

MasterGraph is a Graph used for the master dashboard

#### `MasterGraph().__init__(self, model: Amodely)`

Initialises a master graph with an Amodely model

#### `MasterGraph().get_config_checklist(self, config_id: str) -> dcc.Checklist`

Returns a checklist to configure extra settings.

Parameters
- `config_id` <br /> The id to assign to the Checklist element.

#### `MasterGraph().get_figure(self) -> go.Figure`

Returns a Plot.ly master graph figure based on the model dataframe.

The figure uses the model's selected measure, dimension, and working dataframe to plot the graph. It graphs the model's selected measure against quote date, and plots a separate line for each dimension category.

#### `MasterGraph().draw_graph_config(self, config_ids: tuple[str]) -> html.Div`

Returns a formatted card element with graph configurations.

Parameters
- `config_ids` <br /> A 5-tuple of ids to assign to the measure Dropdown, dimension Dropdown, filter dimension Dropdown, filter category Dropdown, and Checklist respectively.

### `AnomalyGraph(Graph)`

AnomalyGraph is a Graph used for the anomaly detection dashboard

#### `AnomalyGraph().__init__(self, model: Amodely)`

Initialises an anomaly detection graph with an Amodely model

#### `AnomalyGraph().get_figure(self, max_size: int = 30, sig_level: float = 0.05) -> go.Figure`

Returns a Plot.ly anomaly graph figure based on the model dataframe.

The figure uses the model's selected measure, dimension, and working dataframe to plot the graph. It graphs the model's selected measure against quote date, and plots a separate line for each dimension category.

The anomaly detection algorithm transforms the lines to be stationary. The transformations also tend to be normally distributed, so a simple confidence interval can be used to determine outliers; the number of standard deviations from the mean for each line is also plotted as marker size.

Parameters
- `max_size` <br /> Maximum bubble size. The default is 30.
- `sig` <br /> The significance level to use to determine the outliers. The default is `0.05`.

#### `AnomalyGraph().get_sub_figure(self, hover_data: dict) -> go.Figure`

Returns a Plot.ly anomaly graph sub figure based on the hovered data point in the main graph figure.

The figure provides daily data points for the hovered data point's week for that particular category.

Parameters
- `hover_data` <br /> The Plot.ly hover data of the hovered data point.

#### `AnomalyGraph().draw_graph_config(self, config_ids: tuple[str]) -> html.Div`

Returns a formatted Card element with graph configurations and a description of the graph.

Parameters
- `config_ids` <br /> A 5-tuple of ids to assign to the measure Dropdown, dimension Dropdown, filter dimension Dropdown, filter category Dropdown, and confidence interval Slider respectively.

#### `AnomalyGraph().draw_conf_int_slider(self, config_id: str) -> html.Div`

Returns a formatted card element with a slider to control the confidence interval for teh anomaly detection algorithm.

Parameters
- `config_id` The id to assign to the Slider element

#### `AnomalyGraph().get_table(self, config_id: str, sig: float = 0.05 ) -> dash_table.DataTable`

Returns a Plot.ly anomaly graph data table based on the anomalies that have been detected.

The table contents are based on the currently chosen configurations and parameters.

Parameters
- `config_id` <br /> The id to assign to the DataTable element.
- `sig` <br /> The significance level to filter for outliers at.

#### `AnomalyGraph().draw_table(self, config_id: str, sig: float = 0.05) -> html.Div`

Returns a formatted Card element with the anomaly data table.

Parameters
- `config_id` <br /> The id to assign to the DataTable element.
- `sig` <br /> The significance level to filter for outliers at.