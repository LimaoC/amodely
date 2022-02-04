# amodely
 
<h3 align="center">An anomaly detection dashboard for time-series data</h3>

<details open="open">
    <summary>Table of Contents</summary>
    <ol>
        <li>
            <a href="#about-the-project">About the Project</a>
            <ul>
                <li><a href="#tech-stack">Tech Stack</a></li>
            </ul>
        </li>
        <li>
            <a href="#getting-started">Getting Started</a>
            <ul>
                <li><a href="#dependencies">Dependencies</a></li>
                <li><a href="#installation">Installation</a></li>
            </ul>
        </li>
        <li>
            <a href="#usage">Usage</a>
        </li>
        <li>
            <a href="#documentation">Documentation</a>
        </li>
    </ol>
</details>

## About the Project

Amodely is an anomaly detection dashboard that I built during my time as a Pricing Intern at Auto & General. It is used to identify anomalies in time-series data using (primarily) a Seasonal-Trend decomposition with LOESS (STL) algorithm.

### Tech Stack

The teck stack consists wholy of Python and various Python frameworks;
- [Dash Plot.ly](https://plotly.com/)
- [Pandas](https://pandas.pydata.org/)
- [statsmodels](https://www.statsmodels.org/stable/index.html)
- [scikit-learn](https://scikit-learn.org/)

## Getting Started

### Dependencies

The required dependencies can be found under `/requirements.txt`.

### Installation

To install and set up the dashboard, open up Windows PowerShell or Git Bash and follow the steps below:

1. Clone the repo and enter the directory

    ```
    git clone https://github.com/LimaoC/amodely.git

    cd amodely
    ```

2. Create a virtual environment

    ```
    python -m virtualenv venv
    ```

3. Enter the virtual environment

    Windows PowerShell:
    ```
    venv/Scripts/activate
    ```

    Git Bash:
    ```
    source venv/Scripts/activate
    ```

4. Install the required dependencies

    ```
    pip install -r requirements.txt
    ```

5. Create a `.env` file in the root directory with the following variable pointing to the path of the dataset:

    ```
    DATASET_PATH="C:/Path/To/Dataset/"
    ```

6. Change the `DATASET_NAME` variable in `/src/lib/lib.py` (the default is `dataset.xlsx`):

    ```python
    DATASET_NAME = "dataset.xlsx"
    ```

7. Run the dashboard on localhost

    Dashboard:
    ```
    python -m src.dash-app.app
    ```

    Anomaly detection model (for debugging purposes):
    ```
    python -i -m src.amodely
    ```

## Usage

Examples of how the dashboard can be used (note that the data below was randomly generated):

**General Plot.ly features**
- Hover over data points to see info (date, category, conversion rate)
- Adjust graph axes dynamically
- Zoom in on a particular region
- Download plot as a png

![ex1](/assets/ex1.png)

**Master dashboard**
- Configurations:
    - Graphing `Conversion Rate` vs. `Quote Date`
    - Categorising data by `Dimension 1`
    - All categories displayed (`CATEGORY_1A`, `CATEGORY_1B`, ...)
    - Filtering for `Dimension 2` data that are either in the category `CATEGORY_2A` or `CATEGORY_2B`
    - Removing categories that have less than 100 entries
    - Filtering for 2020 data

![ex2](/assets/ex2.png)
![ex3](/assets/ex3.png)

**Anomaly detection dashboard**
- Image 1 configurations:
    - Graphing `Quote Volume` vs. `Quote Date`
    - Categorising data by `All` (combining all dimensions)
    - No filter applied
    - Categories with less than 100 entries removed automatically to avoid interfering with the anomaly detection algorithm
    - Anomaly detection algorithm running at a confidence interval of 95% (default)
    - Filtering for all data (2020 - 2021)
    - Hovering over Sep 06, 2021 week to inspect daily data points from that week
- Image 2 configurations:
    - Graphing `Conversion Rate` vs. `Quote Date`
    - Categorising data by `Dimension 1`
    - Isolating second and third category in `Dimension 1`
    - No filter applied
    - Categories with less than 100 entries removed automatically to avoid interfering with the anomaly detection algorithm
    - Anomaly detection algorithm running at a confidence interval of 80% (smaller threshold for standard deviations, more outliers)
    - Filtering for all data (2020 - 2021)

![ex4](/assets/ex4.png)

**Anomaly detection output table**
- Table of anomalies based on the current configurations of the anomaly detection dashboard
- Updates dynamically when settings/configurations are changed
- Export as CSV

### Documentation

The documentation can be viewed [here](/docs/).
