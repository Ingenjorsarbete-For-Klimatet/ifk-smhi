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

STRANG_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
STRANG_DATE_FORMAT = "%Y-%m-%d"
STRANG_DATE_INTERVALS = ["hourly", "daily", "monthly"]
STRANG = namedtuple("STRANG", "parameter meaning date_from date_to")
STRANG_GET_NOW = lambda: datetime.utcnow()  # .isoformat("T", "seconds") + "Z"
STRANG_PARAMETERS = defaultdict(lambda: STRANG(None, "Missing", None, None))
STRANG_PARAMETERS[116] = STRANG(
    116,
    "CIE UV irradiance [mW/m²]",
    datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
    STRANG_GET_NOW,
)

STRANG_PARAMETERS[117] = STRANG(
    117,
    "Global irradiance [W/m²]",
    datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[118] = STRANG(
    118,
    "Direct normal irradiance [W/m²]",
    datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[120] = STRANG(
    120,
    "PAR [W/m²]",
    datetime.strptime("1999-01-01", STRANG_DATE_FORMAT),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[121] = STRANG(
    121,
    "Direct horizontal irradiance [W/m²]",
    datetime.strptime("2017-04-18", STRANG_DATE_FORMAT),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[122] = STRANG(
    122,
    "Diffuse irradiance [W/m²]",
    datetime.strptime("2017-04-18", STRANG_DATE_FORMAT),
    STRANG_GET_NOW,
)
