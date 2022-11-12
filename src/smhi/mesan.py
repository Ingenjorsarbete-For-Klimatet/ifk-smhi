"""
SMHI MESAN API module.
"""
import json
import requests
from functools import wraps
from smhi.constants import MESAN_URL


def get_data(func: callable) -> callable:
    """
    Get data from url.

    Args:
        function func

    Returns:
        function inner
    """

    @wraps(func)
    def inner(self, *args):
        url = func(self, *args)
        status, headers, data = self._get_data(url)
        return data

    return inner


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
        self.base_url = MESAN_URL.format(category=self._category, version=self._version)
        self.url = None

    @property
    @get_data
    def approved_time(self) -> dict:
        """
        Get approved time.

        Returns:
            approved times
        """
        return self.base_url + "approvedtime.json"

    @property
    @get_data
    def valid_time(self) -> dict:
        """
        Get valid time.

        Returns:
            valid times
        """
        return self.base_url + "validtime.json"

    @property
    @get_data
    def geo_polygon(self) -> dict:
        """
        Get geographic area polygon.

        Returns:
            polygon data
        """
        return self.base_url + "geotype/polygon.json"

    @get_data
    def get_geo_multipoint(self, downsample: int = 2) -> dict:
        """
        Get geographic area multipoint.

        Args:
            multipoint data
        """
        return self.base_url + "geotype/multipoint.json?downsample={downsample}".format(
            downsample=downsample
        )

    @property
    @get_data
    def parameters(self):
        """
        Get parameters.

        Returns:
            available parameters
        """
        return self.base_url + "parameter.json"

    @get_data
    def get_point(
        self,
        latitude: float,
        longitude: float,
    ) -> dict:
        """
        Get data for given lon, lat and parameter.

        Args:
            latitude: latitude
            longitude: longitude
            parameter: parameter
            date_from: get data from (optional),
            date_to: get data to (optional),
            date_interval: interval of data
                           [valid values: hourly, daily, monthly] (optional)

        Returns:
            data
        """
        return (
            self.base_url
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=longitude, latitude=latitude
            )
        )

    @get_data
    def get_multipoint(
        self,
        validtime: str,
        parameter: str,
        leveltype: str,
        level: str,
        downsample: int,
    ) -> dict:
        """
        Get multipoint data.

        Args:
            validtime: valid time
            parameter: parameter
            leveltype: level type
            level: level
            downsample: downsample

        Returns:
            data
        """
        return (
            self.base_url
            + "geotype/multipoint/"
            + "validtime/{YYMMDDThhmmssZ}/parameter/{p}/leveltype/".format(
                YYMMDDThhmmssZ=validtime,
                p=parameter,
            )
            + "{lt}/level/{l}/data.json?with-geo=false&downsample={downsample}".format(
                lt=leveltype,
                l=level,
                downsample=downsample,
            )
        )

    def _get_data(self, url) -> tuple[bool, str, dict]:
        """
        get requested data.

        Args:
            url: url to get from

        Returns:
            status of response
            headers of response
            data of response
        """
        response = requests.get(url)
        status = response.ok
        headers = response.headers

        if status:
            return status, headers, json.loads(response.content)
        else:
            return status, headers, None
