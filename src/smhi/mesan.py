"""SMHI Mesan API module."""
import json
import arrow
import requests
from functools import wraps
from smhi.constants import MESAN_URL
from typing import Any, Callable, Optional
from requests.structures import CaseInsensitiveDict


def get_data(func: Callable) -> Callable:
    """Get data from url.

    Args:
        function func

    Returns:
        function inner
    """

    @wraps(func)
    def inner(self, *args) -> tuple[dict[str, str], dict[str, Any]]:
        url = func(self, *args)
        status, headers, data = self._get_data(url)
        return headers, data

    return inner


class Mesan:
    """SMHI Mesan module."""

    def __init__(self) -> None:
        """Initialise Mesan."""
        self._category: str = "mesan1g"
        self._version: int = 2

        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.status: Optional[bool] = None
        self.header: Optional[dict[str, str]] = None
        self.data: Optional[dict[str, Any]] = None
        self.base_url: str = MESAN_URL.format(
            category=self._category, version=self._version
        )
        self.url: Optional[str] = None

    @property
    @get_data
    def approved_time(self) -> str:
        """Get approved time.

        Returns:
            approved times
        """
        return self.base_url + "approvedtime.json"

    @property
    @get_data
    def valid_time(self) -> str:
        """Get valid time.

        Returns:
            valid times
        """
        return self.base_url + "validtime.json"

    @property
    @get_data
    def geo_polygon(self) -> str:
        """Get geographic area polygon.

        Returns:
            polygon data
        """
        return self.base_url + "geotype/polygon.json"

    @get_data
    def get_geo_multipoint(self, downsample: int = 2) -> str:
        """Get geographic area multipoint.

        Args:
            downsample: downsample parameter

        Returns:
            multipoint data
        """
        if downsample < 1:
            multipoint_url = "geotype/multipoint.json"
        elif downsample > 20:
            multipoint_url = "geotype/multipoint.json?downsample=20"
        else:
            multipoint_url = "geotype/multipoint.json?downsample={downsample}".format(
                downsample=downsample
            )

        return self.base_url + multipoint_url

    @property
    @get_data
    def parameters(self) -> str:
        """Get parameters.

        Returns:
            available parameters
        """
        return self.base_url + "parameter.json"

    @get_data
    def get_point(
        self,
        latitude: float,
        longitude: float,
    ) -> str:
        """Get data for given lon, lat and parameter.

        Args:
            latitude: latitude
            longitude: longitude

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
        level: int,
        downsample: int = 2,
    ) -> str:
        """Get multipoint data.

        Args:
            validtime: valid time
            parameter: parameter
            leveltype: level type
            level: level
            downsample: downsample

        Returns:
            data
        """
        validtime = arrow.get(validtime).format("YYYYMMDDThhmmss") + "Z"
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

    def _get_data(
        self, url
    ) -> tuple[bool, CaseInsensitiveDict[str], Optional[dict[str, Any]]]:
        """Get requested data.

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
