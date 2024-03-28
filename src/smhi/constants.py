"""Constans."""

import logging
from collections import defaultdict
from datetime import datetime
from posixpath import join as urljoin

import arrow
from smhi.models.strang import StrangParameter

logging.basicConfig(level=logging.INFO, format="%(message)s")


def get_now() -> datetime:
    """
    Get current datetime.

    Returns
        current datetime
    """
    return arrow.utcnow().datetime  # .isoformat("T", "seconds") + "Z"


METOBS_AVAILABLE_PERIODS = [
    "latest-hour",
    "latest-day",
    "latest-months",
    "corrected-archive",
]

METFCTS_URL = (
    "https://opendata-download-metfcst.smhi.se/"
    + "api/category/{category}/version/{version}/"
)
MESAN_URL = (
    "https://opendata-download-metanalys.smhi.se/"
    + "api/category/{category}/version/{version}/"
)

MESAN_LEVELS_UNIT = "m"

STRANG_EMPTY = StrangParameter(
    parameter=None, meaning="Missing", time_from=None, time_to=lambda: None
)
STRANG_PARAMETERS: defaultdict[int, StrangParameter] = defaultdict(lambda: STRANG_EMPTY)
STRANG_PARAMETERS[116] = StrangParameter(
    parameter=116,
    meaning="CIE UV irradiance [mW/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)

STRANG_PARAMETERS[117] = StrangParameter(
    parameter=117,
    meaning="Global irradiance [W/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[118] = StrangParameter(
    parameter=118,
    meaning="Direct normal irradiance [W/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[120] = StrangParameter(
    parameter=120,
    meaning="PAR [W/m²]",
    time_from=arrow.get("1999-01-01").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[121] = StrangParameter(
    parameter=121,
    meaning="Direct horizontal irradiance [W/m²]",
    time_from=arrow.get("2017-04-18").datetime,
    time_to=get_now,
)
STRANG_PARAMETERS[122] = StrangParameter(
    parameter=122,
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
