"""
Constans.
"""
from collections import defaultdict
from collections import namedtuple


TYPE_MAP = defaultdict(lambda: "application/json", json="application/json")

METOBS_URL = "https://opendata-download-metobs.smhi.se/api.json"

STRANG_URL = (
    "https://opendata-download-metanalys.smhi.se/api/category/"
    + "{category}/version/{version}/geotype/point/lon/{lon}/lat/"
    + "{lat}/parameter/{parameter}/data.json"
)
STRANG_URL_TIME = "?from={time_from}&to={time_to}&interval={time_interval}"
STRANG = namedtuple("STRANG", "parameter meaning availability")
STRANG_PARAMETERS = [
    STRANG(116, "CIE UV irradiance [mW/m²]", "1999-01-01 - present"),
    STRANG(117, "Global irradiance [W/m²]", "1999-01-01 - present"),
    STRANG(118, "Direct normal irradiance [W/m²]", "1999-01-01 - present"),
    STRANG(120, "PAR [W/m²]", "1999-01-01 - present"),
    STRANG(121, "Direct horizontal irradiance [W/m²]", "2017-04-18 - present"),
    STRANG(122, "Diffuse irradiance [W/m²]", "2017-04-18 - present"),
]
