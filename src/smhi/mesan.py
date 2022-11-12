"""
SMHI MESAN API module.
"""
import json
import requests
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
        self.base_url = MESAN_URL.format(category=self._category, version=self._version)
        self.url = None

    @property
    def approved_time(self) -> dict:
        """
        Get approved time.

        Returns:
            approved times
        """
        approved_time_url = self.base_url + "approvedtime.json"
        status, headers, data = self._get_data(approved_time_url)

        if status:
            return data

    @property
    def valid_time(self) -> dict:
        """
        Get valid time.

        Returns:
            valid times
        """
        valid_time_url = self.base_url + "validtime.json"
        status, headers, data = self._get_data(valid_time_url)

        if status:
            return data

    @property
    def geo_polygon(self) -> dict:
        """
        Get geographic area polygon.

        Returns:
            polygon data
        """
        valid_time_url = self.base_url + "geotype/polygon.json"
        status, headers, data = self._get_data(valid_time_url)

        if status:
            return data

    @property
    def geo_multipoint(self, downsample: int = 2) -> dict:
        """
        Get geographic area multipoint.

        Args:
            multipoint data
        """
        valid_time_url = (
            self.base_url
            + "geotype/multipoint.json?downsample={downsample}".format(
                downsample=downsample
            )
        )
        status, headers, data = self._get_data(valid_time_url)

        if status:
            return data

    @property
    def parameters(self):
        """
        Get parameters.

        Returns:
            available parameters
        """
        parameter_url = self.base_url + "parameter.json"
        status, headers, data = self._get_data(parameter_url)

        if status:
            return data

    def get_point(
        self,
        longitude: float,
        latitude: float,
    ) -> dict:
        """
        Get data for given lon, lat and parameter.

        Args:
            longitude: longitude
            latitude: latitude
            parameter: parameter
            date_from: get data from (optional),
            date_to: get data to (optional),
            date_interval: interval of data
                           [valid values: hourly, daily, monthly] (optional)

        Returns:
            data
        """
        point_url = (
            self.base_url
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=longitude, latitude=latitude
            )
        )
        self.status, self.headers, self.data = self._get_data(point_url)

        if self.status:
            return self.data

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
        multipoint_url = (
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
        self.status, self.headers, self.data = self._get_data(multipoint_url)

        if self.status:
            return self.data

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
        data = json.loads(response.content)

        return status, headers, data
