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
    "air_temperature": "Air temperature at 2 metres height.",
    "wind_speed_of_gust": "Wind gusts",
    "relative_humidity": "Relative humidity at 2 metres height.",
    "air_pressure_at_mean_sea_level": "Air pressure at mean sea level.",
    "wet_bulb_temperature": "Wet bulb temperature",
    "air_temperature_min": "Minimum air temperature at 2 metres height.",
    "air_temperature_max": "Maximum air temperature at 2 metres height.",
    "cloud_base_altitude": "Cloud base altitude.",
    "cloud_are_fraction_significant": "Fraction of significant clouds",
    "cloud_area_fraction": "Total cloud cover",
    "cloud_top_altitude": "Cloud top altitude.",
    "low_type_cloud_area_fraction": "Low cloud cover",
    "high_type_cloud_area_fraction": "High cloud cover",
    "medium_type_cloud_area_fraction": "Medium cloud cove",
    "predominant_precipitation_type_at_surface": "Type of precipitation",
    "precipitation_rate_max": "Maximum precipitation rate",
    "precipitation_rate_min": "Minimum precipitation rate",
    "precipitation_rate_median": "Median precipitation rate",
    "precipitation_rate_mean": "Median precipitation rate",
    "precipitation_amount_last_1_hours": "Precipitation amount last hour",
    "precipitation_amount_last_3_hours": "Precipitation amount last 3 hours",
    "precipitation_amount_last_12_hours": "Precipitation amount last 12 hours",
    "change_over_time_in_surface_snow_amount_1_hours": "Change of snow on surface in last hour",
    "change_over_time_in_surface_snow_amount_3_hours": "Change of snow on surface in last 3 hours",
    "change_over_time_in_surface_snow_amount_12_hours": "Change of snow on surface in last 12 hours",
    "change_over_time_in_surface_snow_amount_24_hours": "Change of snow on surface in last 24 hours",
    "visibility_in_air": "Visibility in air.",
    "precipitation_frozen_part": "Frozen part of precipitation.",
    "precipitation_sort": "Sort of precipitation",
    "wind_from_direction": "Wind from direction at 10 metre.",
    "wind_speed": "Wind speed at 10 metre.",
    "symbol_code": "Weather symbol code with 27 different codes.",
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
