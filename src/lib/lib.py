# CONSTANTS
DATE = "QUOTE_DATE"
DEFAULT_MEASURE = "CONVERSION_RATE"  # for dash app
DEFAULT_DIMENSION = "STATE_CODE"  # for dash app

# STRUCTURE contains the measure variables (QUOTE_VOLUME, SALES_VOLUME, etc.)
# and the aggregation options used for each variable (see the `Collapse`
# transformer in `./pipelines.py`).
STRUCTURE = {
    "QUOTE_VOLUME": {
        "QUOTE_COUNT": "sum",
    },
    "SALES_VOLUME": {
        "SALES_COUNT": "sum",
    },
    "QUOTE_PROPORTION": {
        "QUOTE_COUNT": "sum",
    },
    "SALES_PROPORTION": {
        "SALES_COUNT": "sum",
    },
    "CONVERSION_RATE": {
        "QUOTE_COUNT": "sum",
        "SALES_COUNT": "sum",
    },
    "MATURED_CONVERSION_RATE": {

    },
    "AVERAGE_PREMIUM": {

    },
    "AVERAGE_INSURED_VALUE": {

    },
    "HIRE_CAR_TAKE_UP_RATE": {

    },
    "ROADSIDE_TAKE_UP_RATE": {

    },
    "CHOICE_OF_REPAIRER_TAKE_UP_RATE": {

    },
}

if __name__ == '__main__':
    print("This file is not meant to be run on its own.")
