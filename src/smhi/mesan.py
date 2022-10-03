"""
SMHI MESAN API module.
"""
import json
import requests
from functools import partial
from smhi.constants import MESAN_URL


class Mesan:
    """
    SMHI MESAN module
    """

    def __init__(self) -> None:
        """
        Initialise MESAN.
        """
        self._category = "mesan1g"
        self._version = 2

        self.latitude = None
        self.longitude = None
        self.status = None
        self.header = None
        self.data = None
        self.raw_url = MESAN_URL
        self.url = None

    @property
    def approved_time(self):
        approved_time_url = (
            self.raw_url
            + "/api/category/{category}/version/{version}/approvedtime.json".format(
                category=self._category, version=self._version
            )
        )
        status, headers, data = self._fetch_data(approved_time_url)
        if status:
            return data

    @property
    def valid_time(self):
        valid_time_url = (
            self.raw_url
            + "/api/category/{category}/version/{version}/validtime.json".format(
                category=self._category, version=self._version
            )
        )
        status, headers, data = self._fetch_data(valid_time_url)
        if status:
            return data

    @property
    def geo_area(self):
        valid_time_url = (
            self.raw_url
            + "/api/category/{category}/version/{version}/geotype/polygon.json".format(
                category=self._category, version=self._version
            )
        )
        status, headers, data = self._fetch_data(valid_time_url)
        if status:
            return data

    @property
    def parameters(self):
        """
        Get parameters property.
        Returns:
            available parameters
        """
        parameter_url = (
            self.raw_url
            + "/api/category/{category}/version/{version}/parameter.json".format(
                category=self._category, version=self._version
            )
        )
        status, headers, data = self._fetch_data(parameter_url)
        if status:
            return data

    def fetch_point(
        self,
        longitude: float,
        latitude: float,
    ):
        """
        Get data for given lon, lat and parameter.
        Args:
            longitude: longitude
            latitude: latitude
            parameter: parameter
            date_from: get data from (optional),
            date_to: get data to (optional),
            date_interval: interval of data [valid values: hourly, daily, monthly] (optional)
        """
        point_url = partial(
            self.raw_url
            + "/api/category/{category}/version/{version}/"
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format,
            category=self._category,
            version=self._version,
            longitude=longitude,
            latitude=latitude,
        )
        self.status, self.headers, self.data = self._fetch_data(point_url)
        if self.status:
            return self.data

    def fetch_multipoint(
        self,
        validtime: str,
        parameter: str,
        leveltype: str,
        level: str,
        downsample: int,
    ):
        multipoint_url = partial(
            self.raw_url
            + "/api/category/mesan1g/version/2/geotype/multipoint/"
            + "validtime/{YYMMDDThhmmssZ}/parameter/{p}/leveltype/"
            + "{lt}/level/{l}/data.json?with-geo=false&downsample=2".format,
            category=self._category,
            version=self._version,
            validtime=validtime,
            parameter=parameter,
            leveltype=leveltype,
            level=level,
            downsample=downsample,
        )
        self.status, self.headers, self.data = self._fetch_data(multipoint_url)
        if self.status:
            return self.data

    def _fetch_data(self, url):
        """
        Fetch requested data.

        Args:
            url: url to fetch from
        """
        response = requests.get(url)
        status = response.ok
        headers = response.headers
        data = json.loads(response.content)

        return status, headers, data
