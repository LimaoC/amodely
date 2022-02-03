## app.py

This module is used to initialise and run the Dash app. It contains the app layout and app callbacks.

---

### `app.layout`

This contains the layout for the Plot.ly dashboard in HTML format.

### `@app.callback() update_master_graph(measure: str, dimension: str, year: int, filter_dimension: str, filter_categories: list, checklist: str) -> tuple[go.Figure, list]`

Callback to update the master graph.

Parameters
- `measure` <br /> The measure to select. A list of options can be found in `/src/lib/lib.py`.
- `dimension` <br /> The dimension to select. Options are determined from the dataframe columns.
- `year` <br /> The year to select, or 2019 to select all years (see explanation in `/src/dash-app/graphys.py`).
- `filter_dimension` <br /> The dimension to filter for.
- `filter_categories` <br /> A list of categories to filter for.
- `checklist` <br /> A list of checklist options. Options include `"bad-cats"`

Returns
- A 2-tuple of the updated master graph `Figure` and a list of categories to display on the "Filter for Categories" `Dropdown`.

### `@app.callback() update_anomaly_graph(measure: str, dimension: str, year: int, filter_dimension: str, filter_categories: list, conf_int: int) -> tuple[go.Figure, list, list, dict]`

Callback to update the anomaly graph.

Parameters
- `measure` <br /> The measure to select. A list of options can be found in `/src/lib/lib.py`.
- `dimension` <br /> The dimension to select. Options are determined from the dataframe columns.
- `year` <br /> The year to select, or 2019 to select all years (see explanation in `/src/dash-app/graphys.py`).
- `filter_dimension` <br /> The dimension to filter for.
- `filter_categories` <br /> A list of categories to filter for.

Returns
- A 4-tuple of the updated anomaly graph `Figure`, a list of categories to display on the "Filter for Categories" `Dropdown`, a list of columns to display on the `DataTable`, and the data to be displayed on the DataTable as a `dict`.

### `@app.callback() update_hover(hover_data: dict, filter_dimension: str, filter_categories: list) -> go.Figure`

Callback to update the anomaly sub-graph on hover.

Parameters
- `hover_data` <br /> The hovered data.
- `filter_dimension` <br /> The dimension to filter for.
- `filter_categories` <br /> A list of categories to filter for.

Returns
- The updated anomaly sub-graph `Figure`.