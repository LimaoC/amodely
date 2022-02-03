## amodely.py

This module contains the Amodely class, which is the anomaly detection model. It handles the dataframes and runs the anomaly detection algorithm(s) on the data.

The model stores two dataframes - the main dataframe (`main_df` attribute) and the working dataframe (`df` attribute). Data processing, pipelining, anomaly detection algorithms, etc. are done on the working dataframe. When you want to use another configuration (i.e. another measure or dimension), the working dataframe can be reset to the state of the main dataframe using the `reset_working()` method. For this reason, the main dataframe shouldn't be altered at all.

An anomaly detection algorithm can be run on the working dataframe using the method `detect_anomalies()` (configuration options available). The results of the algorithm are stored in the `anomalies_` dataframe attribute (see [this](https://blog.finxter.com/why-does-the-scikit-learn-library-use-a-trailing-underscore-convention-for-attribute-names/) for an explanation of the underscore).

---

### `Amodely()`

#### `Amodely.__init__(df: pd.DataFrame, measure: str, dimension: str)`

Parameters
- `df` <br /> The master dataframe to be loaded in.
- `measure` <br /> The selected measure. A list of options can be found in `/src/lib/lib.py`. The default is `"CONVERSION_RATE"`.
- `dimension` <br /> The selected dimension. The default is the leftmost dimension in the dataframe.

#### `@property Amodely.measure -> str`

Getter: Returns the selected measure. <br />
Setter: Sets the selected measure to the given string.

#### `@property Amodely.dimension -> str`

Getter: Returns the selected dimension. <br />
Setter: Sets the selected dimension to the given string.

#### `@property Amodely.dimensions -> list[str]`

Returns a list of all the dimensions in the main dataframe.

#### `@property Amodely.categories -> list[str]`

Returns a list of all the categories in the selected dimension. If the selected dimension is ALL, returns a list with a single element `"ALL"`.

#### `@property Amodely.main_df -> pd.DataFrame`

Getter: Returns the main dataframe. <br />
Setter: Sets the main dataframe to a copy of the given dataframe.

#### `@property Amodely.df -> pd.DataFrame`

Getter: Returns the working dataframe. <br />
Setter: Sets the working dataframe to a copy of the given dataframe.

#### `@property Amodely.bad_categories`

Returns a list of the bad categories in the working dataframe.

Bad categories have less than 100 data points and tend to cause problems with the anomaly detection algorithm. If the selected dimension is ALL, an empty list is returned.

#### `Amodely.reset_working()`

Resets the working dataframe to the state of the main dataframe (as a copy).

#### `Amodely.download_anomalies(filename: str = "output")`

Downloads the dataframe of anomalies to a spreadsheet (.xlsx).

If no anomaly detection algorithm was run before this method was called, the output file will be empty. Note: data points considered to be anomalies are determined by the `sig_level` parameter that was used in the `detect_anomalies()` method.

Parameters
- `filename` <br /> The filename of the output spreadsheet. The default is `output.xlsx`.

#### `Amodely.detect_anomalies(method: str, sig_level: float = 0.05, filter_dimension: str = "", filter_categories: list = [])`

Runs an anomaly detection algorithm on the model's working dataframe using the selected measure and dimension. The output is stored in the `anomalies_` attribute.

The methods that have been implemented are ARIMA (outdated) and STL.

Parameters
- `method` <br /> The method to use for the anomaly detection algorithm. The available options are `arima`, `stl`,
- `sig_level` <br /> The significance level to use for the anomaly detection algorithm.
- `filter_dimension` <br /> An (optional) dimension, different to the model's selected dimension, to filter for before the anomaly detection algorithm is run. See `/src/dash-app/app.py` for more details.
- `filter_categories` <br /> An (optional) category(s) to filter for in the filter dimension.