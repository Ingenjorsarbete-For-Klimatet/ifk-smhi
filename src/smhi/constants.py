"""Constans."""

import logging
from collections import defaultdict
from datetime import datetime
from posixpath import join as urljoin

import arrow
from smhi.models.strang_model import StrangParameter

logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_now() -> datetime:
    """
    Get current datetime.

    Returns
        current datetime
    """
    return arrow.utcnow().datetime  # .isoformat("T", "seconds") + "Z"


METOBS_AVAILABLE_PERIODS = {
    "corrected-archive": 0,
    "latest-months": 1,
    "latest-day": 2,
    "latest-hour": 3,
}

METFCTS_URL = (
    "https://opendata-download-metfcst.smhi.se/"
    + "api/category/{category}/version/{version}/"
)

METFCTS_PARAMETER_DESCRIPTIONS = {
    "msl": "Air pressure",
    "t": "Air temperature",
    "vis": "Horizontal visibility",
    "wd": "Wind direction",
    "ws": "Wind speed",
    "r": "Relative humidity",
    "tstm": "Thunder probability",
    "tcc_mean": "Mean value of total cloud cover",
    "lcc_mean": "Mean value of low level cloud cover",
    "mcc_mean": "Mean value of medium level cloud cover",
    "hcc_mean": "Mean value of high level cloud cover",
    "gust": "Wind gust speed",
    "pmin": "Minimum precipitation intensity",
    "pmax": "Maximum precipitation intensity",
    "spp": "Percent of precipitation in frozen form",
    "pmean": "Mean precipitation intensity",
    "pmedian": "Median precipitation intensity",
    "Wsymb2": "Weather Symbol",
}

MESAN_URL = (
    "https://opendata-download-metanalys.smhi.se/"
    + "api/category/{category}/version/{version}/"
)

MESAN_LEVELS_UNIT = "m"

MESAN_PARAMETER_DESCRIPTIONS = {
    "t": "Air temperature",
    "tmin": "Minimum air temperature",
    "tmax": "Maximum air temperature",
    "Tiw": "Wet bulb temperature",
    "gust": "Wind gust speed",
    "wd": "Wind direction",
    "ws": "Wind speed",
    "r": "Relative humidity",
    "prec1h": "Precipitation last hour",
    "prec3h": "Precipitation last three hours",
    "prec12h": "Precipitation last 12 hours",
    "prec24h": "Precipitation last 24 hours",
    "frsn1h": "Snow precipitation last hour ",
    "frsn3h": "Snow precipitation last three hours",
    "frsn12h": "Snow precipitation last 12 hours",
    "frsn24h": "Snow precipitation last 24 hours",
    "vis": "Horizontal visibility",
    "msl": "Pressure reduced to medium sea level",
    "tcc": "Total cloud cover",
    "lcc": "Low level cloud cover",
    "mcc": "Medium level cloud cover",
    "hcc": "High level cloud cover",
    "c_sigfr": "Fraction of significant clouds",
    "cb_sig": "Cloud base of significant clouds",
    "ct_sig": "Cloud top of significant clouds",
    "prtype": "Type of precipitation",
    "pmax": "Maximum precipitation",
    "pmin": "Minimum precipitation",
    "pmedian": "Median precipitation",
    "pmean": "Mean precipitation",
    "prsort": "Sort of precipitation",
    "spp": "Frozen part of total precipitation",
    "Wsymb2": "Weather Symbol",
}


STRANG_EMPTY = StrangParameter(
    key=None, meaning="Missing", time_from=None, time_to=lambda: None
)
STRANG_PARAMETERS: defaultdict[int, StrangParameter] = defaultdict(lambda: STRANG_EMPTY)
STRANG_PARAMETERS[116] = StrangParameter(
    key=116,
    meaning="CIE UV irradiance [mW/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)

STRANG_PARAMETERS[117] = StrangParameter(
    key=117,
    meaning="Global irradiance [W/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[118] = StrangParameter(
    key=118,
    meaning="Direct normal irradiance [W/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[120] = StrangParameter(
    key=120,
    meaning="PAR [W/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[121] = StrangParameter(
    key=121,
    meaning="Direct horizontal irradiance [W/m²]",
    time_from=arrow.get("2017-04-18").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[122] = StrangParameter(
    key=122,
    meaning="Diffuse irradiance [W/m²]",
    time_from=arrow.get("2017-04-18").datetime,
    time_to=get_now,
)

STRANG_BASE_URL = "https://opendata-download-metanalys.smhi.se"
STRANG_POINT_URL = urljoin(
    STRANG_BASE_URL,
    "api/category/"
    + "{category}/version/{version}/geotype/point/lon/{lon}/lat/"
    + "{lat}/parameter/{parameter}/data.json",
)
STRANG_MULTIPOINT_URL = urljoin(
    STRANG_BASE_URL,
    "api/category/"
    + "{category}/version/{version}/geotype/multipoint/validtime/{validtime}/"
    + "parameter/{parameter}/data.json",
)

STRANG_TIME_INTERVALS = ["hourly", "daily", "monthly"]

STATUS_OK = 200
OUT_OF_BOUNDS = "out of bounds"
