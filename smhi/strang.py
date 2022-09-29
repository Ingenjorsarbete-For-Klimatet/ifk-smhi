"""
SMHI STRÅNG client.
"""
import json
import requests
from datetime import datetime
from functools import partial
from smhi.constants import (
    STRANG,
    STRANG_POINT_URL,
    STRANG_POINT_URL_TIME,
    STRANG_PARAMETERS,
    STRANG_DATE_FORMAT,
    STRANG_DATETIME_FORMAT,
    STRANG_DATE_INTERVALS,
)


def check_date(date):
    time_now = parameter.date_to()

    try:
        date_from_parsed = datetime.strptime(date_from, STRANG_DATE_FORMAT)
        date_to_parsed = datetime.strptime(date_to, STRANG_DATE_FORMAT)
    except ValueError:
        raise ValueError("Wrong format of from date, use %Y-%m-%d.")

    if date_from_parsed < parameter.date_from or date_to_parsed < parameter.date_from:
        raise ValueError("Data does not exist that far back.")
    if date_from_parsed > time_now or date_to_parsed > time_now:
        raise ValueError("Data does not exist for the future.")


def build_date_url(
    url: str,
    date_from: str,
    date_to: str,
    date_interval: str,
):
    """
    Build date part of the API url.

    Args:
        url: base url
        date_from: from time
        date_to: to time
        date_interval: time interval
    """
    url = url + "?"

    if date_from is not None:
        check_date(date_from)
        url = url + "from={date_from}".format(date_from=date_from)

    if date_to is not None:
        check_date(date_to)
        url = url + "&to={date_to}".format(date_to=date_to)

    if date_interval is not None:
        if date_interval not in STRANG_DATE_INTERVALS:
            raise ValueError("Time interval must be hourly, daily or monthly.")
        url = url + "&interval={date_interval}".format(date_interval=date_interval)

    return url


def fetch_and_load_strang_data(url: str):
    """
    Fetch requested data and parse it with datetime.

    Args:
        url: url to fetch data
    """
    response = requests.get(url)
    status = response.ok
    headers = response.headers
    data = None

    if status is True:
        data = json.loads(response.content)

        for entry in data:
            entry["date_time"] = datetime.strptime(
                entry["date_time"], STRANG_DATETIME_FORMAT
            )

    return status, headers, data


class StrangPoint:
    """
    SMHI STRÅNG Pointclass. Only supports category strang1g and version 1.
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
        self.status = None
        self.header = None
        self.data = None
        self.available_parameters = STRANG_PARAMETERS
        self.raw_url = partial(
            STRANG_POINT_URL.format, category=self._category, version=self._version
        )
        self.url = None

    @property
    def parameters(self):
        return self.available_parameters

    def fetch_data(
        self,
        longitude: float,
        latitude: float,
        parameter: STRANG,
        date_from: str = None,
        date_to: str = None,
        date_interval: str = None,
    ):
        """
        Get data for given lat, long and parameter.

        Args:
            longitude: longitude
            latitude: latitude
            parameter: parameter
            date_from: get data from (optional),
            date_to: get data to (optional),
            date_interval: interval of data [valid values: hourly, daily, monthly] (optional)
        """
        self.longitude = longitude
        self.latitude = latitude
        self.parameter = self.available_parameters[parameter]

        if self.parameter.parameter is None:
            raise NotImplementedError(
                "Parameter not implemented. Try client.parameters to list available parameters."
            )

        self.url = self.raw_url(
            lon=self.longitude,
            lat=self.latitude,
            parameter=self.parameter.parameter,
        )

        self.url = build_date_url(
            self.url,
            date_from,
            date_to,
            date_interval,
        )
        self.status, self.headers, self.data = fetch_and_load_strang_data(self.url)
