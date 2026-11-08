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

SNOW_URL = (
    "https://opendata-download-metfcst.smhi.se/"
    + "api/category/{category}/version/{version}/"
)

SNOW_LEVELS_UNIT = "m"

SNOW_PARAMETER_DESCRIPTIONS = {
    "air_temperature": "Air temperature at 2 metres height.",
    "wind_from_direction": "Wind from direction at 10 metre.",
    "wind_speed": "Wind speed at 10 metre.",
    "wind_speed_of_gust": "Instantaneous 10 metre wind gust",
    "relative_humidity": "Relative humidity at 2 metres height.",
    "air_pressure_at_mean_sea_level": "Air pressure at mean sea level.",
    "visibility_in_air": "Visibility in air.",
    "thunderstorm_probability": "Thunderstorm probability",
    "probability_of_frozen_precipitation": "Probability of frozen precipitation.",
    "cloud_area_fraction": "Total Cloud Cover",
    "low_type_cloud_area_fraction": "Low cloud cover",
    "medium_type_cloud_area_fraction": "Medium cloud cover",
    "high_type_cloud_area_fraction": "High cloud cover",
    "cloud_base_altitude": "Cloud base altitude.",
    "cloud_top_altitude": "Cloud top altitude.",
    "precipitation_amount_mean_deterministic": "Deterministic mean total precipitation amount",
    "precipitation_amount_mean": "Mean total precipitation amount",
    "precipitation_amount_min": "Minimum total precipitation amount",
    "precipitation_amount_max": "Maximum total precipitation amount",
    "precipitation_amount_median": "Median total precipitation amount",
    "probability_of_precipitation": "Propability of precipitation of at least 0.1 mm",
    "precipitation_frozen_part": "Frozen part of precipitation.",
    "predominant_precipitation_type_at_surface": "Precipitation type",
    "symbol_code": "Weather symbol code with 27 different codes.",
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
    "air_pressure": "Air pressure.",
    "air_pressure_at_mean_sea_level": "Air pressure at mean sea level.",
    "dew_point_temperature": "2 metre dewpoint temperature.",
    "wet_bulb_temperature": "Wet bulb temperature",
    "cloud_base_altitude": "Cloud base altitude.",
    "cloud_area_fraction": "Total cloud cover",
    "cloud_top_altitude": "Cloud top altitude.",
    "low_type_cloud_area_fraction": "Low cloud cover",
    "high_type_cloud_area_fraction": "High cloud cover",
    "medium_type_cloud_area_fraction": "Medium cloud cove",
    "predominant_precipitation_type_at_surface": "Type of precipitation",
    "precipitation_amount_last_1_hours": "Precipitation amount last hour",
    "precipitation_amount_last_3_hours": "Precipitation amount last 3 hours",
    "change_over_time_in_surface_snow_amount_1_hours": "Change of snow on surface in last hour",
    "change_over_time_in_surface_snow_amount_3_hours": "Change of snow on surface in last 3 hours",
    "change_over_time_in_surface_snow_amount_12_hours": "Change of snow on surface in last 12 hours",
    "change_over_time_in_surface_snow_amount_24_hours": "Change of snow on surface in last 24 hours",
    "visibility_in_air": "Visibility in air.",
    "precipitation_frozen_part": "Frozen part of precipitation.",
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
