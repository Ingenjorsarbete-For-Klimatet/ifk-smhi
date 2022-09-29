"""
Constans.
"""
from datetime import datetime
from collections import defaultdict
from collections import namedtuple


TYPE_MAP = defaultdict(lambda: "application/json", json="application/json")

METOBS_URL = "https://opendata-download-metobs.smhi.se/api.json"


STRANG_POINT_URL = (
    "https://opendata-download-metanalys.smhi.se/api/category/"
    + "{category}/version/{version}/geotype/point/lon/{lon}/lat/"
    + "{lat}/parameter/{parameter}/data.json"
)
STRANG_POINT_URL_TIME = "?from={time_from}&to={time_to}&interval={time_interval}"


STRANG_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
STRANG_DATE_FORMAT = "%Y-%m-%d"
STRANG_TIME_INTERVALS = ["hourly", "daily", "monthly"]
STRANG = namedtuple("STRANG", "parameter meaning time_from time_to")
STRANG_PARAMETERS = [
    STRANG(
        116,
        "CIE UV irradiance [mW/m²]",
        datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
        lambda: datetime.now(),
    ),
    STRANG(
        117,
        "Global irradiance [W/m²]",
        datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
        lambda: datetime.now(),
    ),
    STRANG(
        118,
        "Direct normal irradiance [W/m²]",
        datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
        lambda: datetime.now(),
    ),
    STRANG(
        120,
        "PAR [W/m²]",
        datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
        lambda: datetime.now(),
    ),
    STRANG(
        121,
        "Direct horizontal irradiance [W/m²]",
        datetime.strptime("2017-04-18", STRANG_DATE_FORMAT),
        lambda: datetime.now(),
    ),
    STRANG(
        122,
        "Diffuse irradiance [W/m²]",
        datetime.strptime("2017-04-18", STRANG_DATE_FORMAT),
        lambda: datetime.now(),
    ),
]
