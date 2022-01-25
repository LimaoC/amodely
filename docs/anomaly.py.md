# amodely.py

### `Amodely(df: pd.DataFrame, measure: str, dimension: str)`

Amodely is the main anomaly detection model class. It handles the dataframes and runs the anomaly detection algorithm(s) on the data.

The model stores two dataframes - the main dataframe (`main_df` attribute) and the working dataframe (`df` attribute). Data processing, pipelining, anomaly detection algorithms, etc. are done on the working dataframe. When you want to use another configuration (i.e. another measure or dimension), the working dataframe can be reset to the state of the main dataframe using the `reset_working()` method. For this reason, the main dataframe shouldn't be altered at all.

(adding to the main df)

An anomaly detection algorithm can be run on the working dataframe using the method `detect_anomalies()` (configuration options available). The results of the algorithm are stored in the `anomalies_` dataframe attribute (see [this](https://blog.finxter.com/why-does-the-scikit-learn-library-use-a-trailing-underscore-convention-for-attribute-names/) for an explanation of the underscore).

Parameters
- `df` <br /> The master dataframe to be loaded in.
- `measure` <br /> The selected measure. A list of options can be found in `/src/lib/lib.py`. The default is `CONVERSION_RATE`.
- `dimension` <br /> The selected dimension. The default is the leftmost dimension in the dataframe.

#### `@property Amodely.measure -> str`

Getter: Returns the selected measure. <br />
Setter: Sets the measure to the given string.

#### `@property Amodely.dimension -> str`

Getter: Returns the selected dimension. <br />
Setter: Sets the dimension to the given string.

#### `@property Amodely.dimensions -> list[str]`

Returns a list of all the dimensions in the main dataframe.

#### `@property Amodely.categories -> list[str]`

Returns a list of all the categories in the selected dimension.

#### `@property Amodely.main_df -> pd.DataFrame`

Getter: Returns the main dataframe. <br />
Setter: Sets the main dataframe to a copy of the given dataframe.

#### `@property Amodely.df -> pd.DataFrame`

Getter: Returns the working dataframe. <br />
Setter: Sets the working dataframe to a copy of the given dataframe.

#### `@property Amodely.bad_categories`

Returns a list of the bad categories in the working dataframe.

Bad categories have less than 100 data points and as such tend to cause problems with the anomaly detection algorithm.

#### `Amodely.reset_working()`

Resets the working dataframe to the state of the main dataframe (as a copy).

#### `Amodely.append(df: pd.DataFrame, sort_after: bool = False, reset_working: bool = False)`

Appends additional data to the dataframe.

The columns of the given dataframe must be the same as the columns of the main dataframe, or this method will do nothing. Note: this method doesn't affect the working dataframe.

Parameters
- `df` <br /> Dataframe containing new entries to be added to the main dataframe.
- `sort_after` <br /> Whether a sort should be performed on the main dataframe after appending the data. This is only needed if the data from the additional dataframe does not "match" the sort of the main dataframe (e.g. dimensions and categories not sorted in the same order).

#### `Amodely.download_anomalies(filename: str = "output")`

Downloads the dataframe of anomalies to a spreadsheet (.xlsx).

If no anomaly detection algorithm was run before this method was called, the output file will be empty. Note: data points considered to be anomalies are determined by the `sig_level` parameter that was used in the `detect_anomalies()` method.

Parameters
- `filename` <br /> The filename of the output spreadsheet. The default is `output.xlsx`.

#### `Amodely.detect_anomalies(method: str, sig_level: float = 0.05)`

Runs an anomaly detection algorithm on the model's working dataframe using the selected measure and dimension. The output is stored in the `anomalies_` attribute.

The methods that have been implemented are ARIMA (outdated) and STL.

Parameters
- `method` <br /> The method to use for the anomaly detection algorithm. The available options are `arima`, `stl`,
- `sig_level` <br /> The significance level to use for the anomaly detection algorithm.