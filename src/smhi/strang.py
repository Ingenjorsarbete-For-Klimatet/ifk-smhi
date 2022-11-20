"""SMHI Strang client.

See validation of model: https://strang.smhi.se/validation/validation.html
"""
import json
import arrow
import requests
import logging
from datetime import datetime
from functools import partial
from collections import defaultdict
from requests.structures import CaseInsensitiveDict
from smhi.constants import (
    STRANG_POINT_URL,
    STRANG_PARAMETERS,
    STRANG_MULTIPOINT_URL,
    STRANG_TIME_INTERVALS,
)


logging.basicConfig(level=logging.INFO)


class Strang:
    """SMHI Strang class. Only supports category strang1g and version 1."""

    def __init__(self) -> None:
        """Initialise Strang object."""
        self._category = "strang1g"
        self._version = 1

        self.latitude = None
        self.longitude = None
        self.parameter = None
        self.time_from = None
        self.time_to = None
        self.valid_time = None
        self.time_interval = None
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
    def parameters(self) -> defaultdict:
        """Get parameters property.

        Returns:
            available parameters
        """
        for key, value in self.available_parameters.items():
            logging.info(
                "parameter: {parameter}, info: {meaning}".format(
                    parameter=key, meaning=value.meaning
                )
            )

        return self.available_parameters

    def get_point(
        self,
        latitude: float,
        longitude: float,
        parameter: int,
        time_from: str = None,
        time_to: str = None,
        time_interval: str = None,
    ) -> tuple[bool, CaseInsensitiveDict, list]:
        """Get data for given lon, lat and parameter.

        Args:
            latitude: latitude
            longitude: longitude
            parameter: parameter
            time_from: get data from (optional),
            time_to: get data to (optional),
            time_interval: interval of data
                           [valid values: hourly, daily, monthly] (optional)

        Returns:
            status: status code
            headers: GET headers
            data: data

        Raises:
            TypeError: wrong type of latitude and/or longitude
            NotImplementedError: parameter not supported
        """
        parameter = self.available_parameters[parameter]
        if parameter.parameter is None:
            raise NotImplementedError(
                "Parameter not implemented."
                + " Try client.parameters to list available parameters."
            )

        if longitude is None or latitude is None:
            raise TypeError("Wrong type of latitude and/or longitude provided.")

        self.longitude = longitude
        self.latitude = latitude
        self.parameter = parameter
        self.time_from = time_from
        self.time_to = time_to
        self.time_interval = time_interval

        url = self.point_raw_url
        url = self._build_base_point_url(url)
        url = self._build_time_point_url(url)
        status, headers, data = self._get_and_load_data(url)
        self.point_url = url

        return status, headers, data

    def get_multipoint(
        self, parameter: int, valid_time: str, time_interval: str = None
    ) -> tuple[bool, CaseInsensitiveDict, list]:
        """Get full spatial data for given parameter and time.

        Args:
            parameter: parameter
            valid_time: valid time
            time_interval: interval of data
                           [valid values: hourly,
                            daily, monthly] (optional)

        Returns:
            status: status code
            headers: GET headers
            data: data

        Raises:
            TypeError: wrong type of valid time
            NotImplementedError: parameter not supported
        """
        parameter = self.available_parameters[parameter]
        if parameter.parameter is None:
            raise NotImplementedError(
                "Parameter not implemented."
                + " Try client.parameters to list available parameters."
            )

        try:
            valid_time = arrow.get(valid_time).isoformat()
        except TypeError:
            raise TypeError("Wrong type of valid time provided. Check valid time.")

        self.parameter = parameter
        self.valid_time = arrow.get(valid_time).isoformat()
        self.time_interval = time_interval

        url = self.multipoint_raw_url
        url = self._build_base_multipoint_url(url)
        url = self._build_time_multipoint_url(url)
        status, headers, data = self._get_and_load_data(url)
        self.multipoint_url = url

        return status, headers, data

    def _build_base_point_url(self, url: partial) -> str:
        """Build base point url.

        Args:
            url: url to format

        Returns:
            formatted url string
        """
        return url(
            lon=self.longitude,
            lat=self.latitude,
            parameter=self.parameter.parameter,
        )

    def _build_base_multipoint_url(self, url: partial) -> str:
        """
        Build base point url.

        Args:
            url: url to format

        Returns:
            formatted url string
        """
        return url(
            validtime=self.valid_time,
            parameter=self.parameter.parameter,
        )

    def _build_time_point_url(self, url: str) -> str:
        """Build date part of the API url.

        Args:
            url: formatted url string

        Returns:
            url string

        Raises:
            ValueError: time_interval not valid
            NotImplementedError: date out of bounds
        """
        time_from = self._parse_datetime(self.time_from)
        time_to = self._parse_datetime(self.time_to)
        time_interval = self.time_interval

        if any([time_from, time_to, time_interval]) is True:
            url += "?"

        if time_from is not None:
            url += "from={time_from}".format(time_from=time_from)

        if time_to is not None:
            if time_from is not None:
                url += "&"
            url += "to={time_to}".format(time_to=time_to)

        if time_interval is not None and (time_from is None and time_to is None):
            raise NotImplementedError(
                "Date from and to not specified but interval is. Be more explicit."
            )

        if time_interval is not None and (time_from is not None or time_to is not None):
            if time_interval not in STRANG_TIME_INTERVALS:
                raise ValueError("Time interval must be hourly, daily or monthly.")
            url += "&interval={interval}".format(interval=time_interval)

        return url

    def _build_time_multipoint_url(self, url: str) -> str:
        """Build date part of the API url.

        Args:
            url: formatted url string

        Returns:
            url string

        Raises:
            ValueError
        """
        time_interval = self.time_interval

        if time_interval is not None:
            if time_interval not in STRANG_TIME_INTERVALS:
                raise ValueError("Time interval must be hourly, daily or monthly.")
            url += "?interval={interval}".format(interval=time_interval)

        return url

    def _get_and_load_data(self, url: str) -> tuple[bool, CaseInsensitiveDict, list]:
        """Fetch requested point data and parse it with datetime.

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
        else:
            logging.info("No data returned.")

        return status, headers, data

    def _parse_datetime(self, date_time: str) -> datetime:
        """Parse date into a datetime format given as string and check bounds.

        Args:
            date_time: date as string

        Returns:
            parsed date

        Raises:
            ValueError
        """
        if date_time is None:
            return date_time

        try:
            date_time = arrow.get(date_time)
        except ValueError:
            raise ValueError("Wrong format of date.")

        if self.parameter.time_from < date_time < self.parameter.time_to():
            return date_time.isoformat()
        else:
            raise ValueError(
                "Time not in allowed interval: {time_from} to {time_to}.".format(
                    time_from=self.parameter.time_from, time_to=self.parameter.time_to()
                )
            )
