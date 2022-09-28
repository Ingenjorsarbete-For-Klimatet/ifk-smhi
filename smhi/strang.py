"""
SMHI STRÅNG client.
"""
import json
import requests
from functools import partial
from smhi.constants import STRANG_URL, STRANG_URL_TIME, STRANG_PARAMETERS


class Strang:
    """
    SMHI STRÅNG class. Only supports category strang1g and version 1.
    """

    def __init__(self):
        """
        Initialise STRÅNG object.
        """
        self._category = "strang1g"
        self._version = 1

        self.latitude = None
        self.longitude = None
        self.parameter = None
        self.data = None

        self.available_parameters = STRANG_PARAMETERS
        self.raw_url = partial(
            STRANG_URL.format, category=self._category, version=self._version
        )
        self.time_url = STRANG_URL_TIME
        self.url = None

    @property
    def parameters(self):
        return self.available_parameters

    def fetch_data(
        self,
        longitude: float,
        latitude: float,
        parameter: int,
        time_from: str = None,
        time_to: str = None,
        time_interval: str = "hourly",
    ):
        """
        Get data for given lat, long and parameter.

        Args:
            longitude: longitude
            latitude: latitude
            parameter: parameter
            time_from: get data from (optional),
            time_to: get data to (optional),
            time_interval: interval of data [valid values: hourly, daily, monthly] (optional)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.parameter = [
            p.parameter for p in self.available_parameters if p.parameter == parameter
        ]
        if len(self.parameter) != 0:
            self.parameter = self.parameter[0]
        else:
            raise NotImplementedError(
                "Parameter not implemented. Try client.parameters to list available parameters."
            )

        self.url = self.raw_url(
            lon=self.longitude,
            lat=self.latitude,
            parameter=self.parameter,
        )
        if time_from is not None:
            if time_from is None or time_interval is None:
                raise NotImplementedError("All time arguments must be set.")

            self.url = self.url + self.time_url.format(
                time_from=time_from,
                time_to=time_to,
                time_interval=time_interval,
            )

        response = requests.get(self.url)
        self.headers = response.headers
        self.data = json.loads(response.content)
