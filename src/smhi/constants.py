"""
Constans.
"""
import arrow
from collections import namedtuple
from collections import defaultdict
from posixpath import join as urljoin

TYPE_MAP = defaultdict(lambda: "application/json", json="application/json")

METOBS_URL = "https://opendata-download-metobs.smhi.se/api.json"

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
STRANG = namedtuple("STRANG", "parameter meaning time_from time_to")
STRANG_GET_NOW = lambda: arrow.utcnow().datetime  # .isoformat("T", "seconds") + "Z"
STRANG_PARAMETERS = defaultdict(lambda: STRANG(None, "Missing", None, None))
STRANG_PARAMETERS[116] = STRANG(
    116,
    "CIE UV irradiance [mW/m²]",
    arrow.get("1999-01-01"),
    STRANG_GET_NOW,
)

STRANG_PARAMETERS[117] = STRANG(
    117,
    "Global irradiance [W/m²]",
    arrow.get("1999-01-01"),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[118] = STRANG(
    118,
    "Direct normal irradiance [W/m²]",
    arrow.get("1999-01-01"),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[120] = STRANG(
    120,
    "PAR [W/m²]",
    arrow.get("1999-01-01"),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[121] = STRANG(
    121,
    "Direct horizontal irradiance [W/m²]",
    arrow.get("2017-04-18"),
    STRANG_GET_NOW,
)
STRANG_PARAMETERS[122] = STRANG(
    122,
    "Diffuse irradiance [W/m²]",
    arrow.get("2017-04-18"),
    STRANG_GET_NOW,
)
