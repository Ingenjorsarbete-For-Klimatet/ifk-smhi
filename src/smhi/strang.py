"""
SMHI STRÅNG client.

See validation of model: https://strang.smhi.se/validation/validation.html
"""
import json
import arrow
import requests
from functools import partial
from smhi.constants import (
    STRANG,
    STRANG_POINT_URL,
    STRANG_PARAMETERS,
    STRANG_MULTIPOINT_URL,
    STRANG_DATE_INTERVALS,
)


class Strang:
    """
    SMHI STRÅNG class. Only supports category strang1g and version 1.
    """

    def __init__(self) -> None:
        """
        Initialise STRÅNG object.
        """
        self._category = "strang1g"
        self._version = 1

        self.latitude = None
        self.longitude = None
        self.parameter = None
        self.date_from = None
        self.date_to = None
        self.valid_time = None
        self.date_interval = None
        self.status = None
        self.header = None
        self.data = None
        self.available_parameters = STRANG_PARAMETERS
        self.point_raw_url = partial(
            STRANG_POINT_URL.format, category=self._category, version=self._version
        )
        self.multipoint_raw_url = partial(
            STRANG_MULTIPOINT_URL.format, category=self._category, version=self._version
        )
        self.point_url = None
        self.multipoint_url = None

    @property
    def parameters(self):
        """
        Get parameters property.

        Returns:
            available parameters
        """
        return self.available_parameters

    def get_point(
        self,
        longitude: float,
        latitude: float,
        parameter: int,
        date_from: str = None,
        date_to: str = None,
        date_interval: str = None,
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
        parameter = self.available_parameters[parameter]
        if parameter is None:
            raise NotImplementedError(
                "Parameter not implemented. Try client.parameters to list available parameters."
            )

        self.longitude = longitude
        self.latitude = latitude
        self.parameter = parameter
        self.date_from = date_from
        self.date_to = date_to
        self.date_interval = date_interval

        url = self.point_raw_url
        url = self._build_base_point_url(url)
        url = self._build_date_point_url(url)
        self.status, self.headers, self.data = self._get_and_load_data(url)
        self.point_url = url

        if self.status is False:
            raise ValueError(
                "Fetch failed and no data was returned. Check longitude and latitude coordinates."
            )

    def get_multipoint(
        self, parameter: int, valid_time: str, date_interval: str = None
    ):
        """
        Get full spatial data for given parameter and time.
        """
        parameter = self.available_parameters[parameter]
        if parameter is None:
            raise NotImplementedError(
                "Parameter not implemented. Try client.parameters to list available parameters."
            )

        self.parameter = parameter
        self.valid_time = valid_time
        self.date_interval = date_interval

        url = self.multipoint_raw_url
        url = self._build_base_multipoint_url(url)
        url = self._build_date_multipoint_url(url)
        self.status, self.headers, self.data = self._get_and_load_data(url)
        self.multipoint_url = url

        if self.status is False:
            raise ValueError(
                "Fetch failed and no data was returned. Check longitude and latitude coordinates."
            )

    def _build_base_point_url(self, url):
        """
        Build base point url.

        Args:
            url: url to format
        """
        return url(
            lon=self.longitude,
            lat=self.latitude,
            parameter=self.parameter.parameter,
        )

    def _build_base_multipoint_url(self, url):
        """
        Build base point url.

        Args:
            url: url to format
        """
        return url(
            validtime=self.valid_time,
            parameter=self.parameter.parameter,
        )

    def _build_date_point_url(self, url):
        """
        Build date part of the API url.
        """
        date_from = self._parse_date(self.date_from)
        date_to = self._parse_date(self.date_to)
        date_interval = self.date_interval

        if any([date_from, date_to, date_interval]) is True:
            url += "?"

        if date_from is not None:
            url += "from={date_from}".format(date_from=date_from)

        if date_to is not None:
            if date_from is not None:
                url += "&"
            url += "to={date_to}".format(date_to=date_to)

        if date_interval is not None and (date_from is None and date_to is None):
            raise NotImplementedError(
                "Date from and to not specified but interval is. Be more explicit."
            )

        if date_interval is not None and (date_from is not None or date_to is not None):
            if date_interval not in STRANG_DATE_INTERVALS:
                raise ValueError("Time interval must be hourly, daily or monthly.")
            url += "&interval={interval}".format(interval=date_interval)

        return url

    def _build_date_multipoint_url(self, url):
        """
        Build date part of the API url.
        """
        date_interval = self.date_interval

        if date_interval is True:
            url += "?"

        if date_interval is not None:
            if date_interval not in STRANG_DATE_INTERVALS:
                raise ValueError("Time interval must be hourly, daily or monthly.")
            url += "&interval={interval}".format(interval=date_interval)

        return url

    def _get_and_load_data(self, url):
        """
        Fetch requested point data and parse it with datetime.

        Args:
            url: url to fetch from
        """
        response = requests.get(url)
        status = response.ok
        headers = response.headers
        data = None

        if status is True:
            data = json.loads(response.content)

            if "date_time" in data[0]:
                for entry in data:
                    entry["date_time"] = arrow.get(entry["date_time"]).datetime

        return status, headers, data

    def _parse_date(self, date):
        """
        Parse date into a datetime format given as string and check bounds.

        Args:
            date: date as string

        Returns:
            parsed date
        """
        if date is None:
            return date

        try:
            date = arrow.get(date).datetime
        except ValueError:
            raise ValueError("Wrong format of date.")

        if self.parameter.date_from < date < self.parameter.date_to():
            return date
        else:
            raise ValueError(
                "Date not in allowed interval: {date_from} to {date_to}.".format(
                    date_from=self.parameter.date_from, date_to=self.parameter.date_to()
                )
            )
