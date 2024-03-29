"""SMHI Strang client.

See validation of model: https://strang.smhi.se/validation/validation.html
"""

import json
import logging
from collections import defaultdict
from functools import partial
from typing import Optional

import arrow
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
from smhi.constants import (
    STATUS_OK,
    STRANG_MULTIPOINT_URL,
    STRANG_PARAMETERS,
    STRANG_POINT_URL,
    STRANG_TIME_INTERVALS,
)
from smhi.models.strang import StrangMultiPoint, StrangParameter, StrangPoint

logger = logging.getLogger(__name__)


class Strang:
    """SMHI Strang class. Only supports category strang1g and version 1."""

    def __init__(self) -> None:
        """Initialise Strang object."""
        self._category = "strang1g"
        self._version = 1

        self._point_raw_url: partial[str] = partial(
            STRANG_POINT_URL.format, category=self._category, version=self._version
        )
        self._multipoint_raw_url: partial[str] = partial(
            STRANG_MULTIPOINT_URL.format, category=self._category, version=self._version
        )
        self._point_url: Optional[str] = None
        self._multipoint_url: Optional[str] = None
        self._available_parameters: defaultdict[int, StrangParameter] = (
            STRANG_PARAMETERS
        )

    @property
    def parameters(
        self,
    ) -> list[int]:
        """Get parameters property.

        Returns:
            available parameters
        """
        for key, value in self._available_parameters.items():
            logger.info(
                "parameter: {parameter}, info: {meaning}".format(
                    parameter=key, meaning=value.meaning
                )
            )

        return list(self._available_parameters.keys())

    def get_point(
        self,
        latitude: float,
        longitude: float,
        parameter: int,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        time_interval: Optional[str] = None,
    ) -> StrangPoint:
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
            strange point model

        Raises:
            TypeError: wrong type of latitude and/or longitude
            NotImplementedError: parameter not supported
        """
        strang_parameter = self._available_parameters[parameter]
        if strang_parameter.key is None:
            raise NotImplementedError(
                "Parameter not implemented."
                + " Try client.parameters to list available parameters."
            )

        if longitude is None or latitude is None:
            raise TypeError("Wrong type of latitude and/or longitude provided.")

        time_from = self._parse_datetime(time_from, strang_parameter)
        time_to = self._parse_datetime(time_to, strang_parameter)

        url = self._point_raw_url
        url = self._build_base_point_url(url, strang_parameter, longitude, latitude)
        url = self._build_time_point_url(url, time_from, time_to, time_interval)
        data, header, status = self._get_and_load_data(url, strang_parameter)

        return StrangPoint(
            parameter_key=strang_parameter.key,
            parameter_meaning=strang_parameter.meaning,
            longitude=longitude,
            latitude=latitude,
            time_from=time_from,
            time_to=time_to,
            time_interval=time_interval,
            url=url,
            status=status,
            headers=header,
            data=data,
        )

    def get_multipoint(
        self, parameter: int, valid_time: str, time_interval: Optional[str] = None
    ) -> StrangMultiPoint:
        """Get full spatial data for given parameter and time.

        Args:
            parameter: parameter
            valid_time: valid time
            time_interval: interval of data
                           [valid values: hourly,
                            daily, monthly] (optional)

        Returns:
            strange multipoint model

        Raises:
            TypeError: wrong type of valid time
            NotImplementedError: parameter not supported
        """
        strang_parameter = self._available_parameters[parameter]
        if strang_parameter.key is None:
            raise NotImplementedError(
                "Parameter not implemented."
                + " Try client.parameters to list available parameters."
            )

        try:
            valid_time = arrow.get(valid_time).isoformat()
        except TypeError:
            raise TypeError("Wrong type of valid time provided. Check valid time.")

        url = self._multipoint_raw_url
        url = self._build_base_multipoint_url(url, strang_parameter, valid_time)
        url = self._build_time_multipoint_url(url, time_interval)
        data, header, status = self._get_and_load_data(url, strang_parameter)

        return StrangMultiPoint(
            parameter_key=strang_parameter.key,
            parameter_meaning=strang_parameter.meaning,
            valid_time=valid_time,
            time_interval=time_interval,
            url=url,
            status=status,
            headers=header,
            data=data,
        )

    def _build_base_point_url(
        self,
        url: partial[str],
        parameter: StrangParameter,
        longitude: float,
        latitude: float,
    ) -> str:
        """Build base point url.

        Args:
            url: url to format
            parameter: strang parameter
            longitude: longitude
            latitude: latitude

        Returns:
            formatted url string
        """
        return url(
            lon=longitude,
            lat=latitude,
            parameter=parameter.key,
        )

    def _build_base_multipoint_url(
        self, url: partial[str], parameter: StrangParameter, valid_time: str
    ) -> str:
        """
        Build base point url.

        Args:
            url: url to format
            parameter: strang parameter
            valid_time: valid time for call

        Returns:
            formatted url string
        """
        return url(
            validtime=valid_time,
            parameter=parameter.key,
        )

    def _build_time_point_url(
        self, url: str, time_from: str, time_to: str, time_interval: str
    ) -> str:
        """Build date part of the API url.

        Args:
            url: formatted url string
            time_from: from time
            time_to: to time
            time_interval: interval

        Returns:
            url string

        Raises:
            ValueError: time_interval not valid
            NotImplementedError: date out of bounds
        """
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

    def _build_time_multipoint_url(self, url: str, time_interval: str) -> str:
        """Build date part of the API url.

        Args:
            url: formatted url string
            time_interval: time interval

        Returns:
            url string

        Raises:
            ValueError
        """
        if time_interval is not None:
            if time_interval not in STRANG_TIME_INTERVALS:
                raise ValueError("Time interval must be hourly, daily or monthly.")
            url += "?interval={interval}".format(interval=time_interval)

        return url

    def _get_and_load_data(
        self, url: str, parameter: StrangParameter
    ) -> tuple[pd.DataFrame, CaseInsensitiveDict[str], int]:
        """Fetch requested point data and parse it with datetime.

        Args:
            url: url to fetch from
            parameter: strang parameter

        Returns:
            data
            header
            status code
        """
        response = requests.get(url)
        status = response.status_code
        header = response.headers

        if status == STATUS_OK:
            data = json.loads(response.content)

            if "date_time" in data[0]:
                data = self._parse_point_data(data, parameter)
            else:
                data = self._parse_multipoint_data(data, parameter)

            return data, header, status
        else:
            logging.info("No data returned.")

            return pd.DataFrame(), header, status

    def _parse_datetime(
        self, date_time: Optional[str], parameter: StrangParameter
    ) -> Optional[str]:
        """Parse date into a datetime format given as string and check bounds.

        Args:
            date_time: date as string
            parameter: strang parameter

        Returns:
            parsed date

        Raises:
            ValueError
        """
        if date_time is None:
            return date_time

        try:
            date_time_arrow = arrow.get(date_time)
        except ValueError:
            raise ValueError("Wrong format of date.")

        if parameter.time_from < date_time_arrow < parameter.time_to():
            return date_time_arrow.isoformat()
        else:
            raise ValueError(
                "Time not in allowed interval: {time_from} to {time_to}.".format(
                    time_from=parameter.time_from, time_to=parameter.time_to()
                )
            )

    def _parse_point_data(self, data: list, parameter: StrangParameter) -> pd.DataFrame:
        """Parse point data into a pandas DataFrame.

        Args:
            data: data as a list
            parameter: strang parameter

        Returns
            data_pd: pandas dataframe
        """
        for entry in data:
            entry["date_time"] = arrow.get(entry["date_time"]).datetime

        data_pd = pd.DataFrame(data)
        data_pd.set_index("date_time", inplace=True)
        # data_pd.rename(columns={"value": parameter.meaning}, inplace=True)

        return data_pd

    def _parse_multipoint_data(
        self, data: list, parameter: StrangParameter
    ) -> pd.DataFrame:
        """Parse multipoint data into a pandas DataFrame.

        Args:
            data: data as a list
            parameter: strang parameter

        Returns
            data_pd: pandas dataframe
        """
        data_pd = pd.DataFrame(data)
        # data_pd.rename(
        #     columns={
        #         "value": str(parameter.meaning)
        #         + " {0} {1}".format(self.valid_time, self.time_interval)
        #     },
        #     inplace=True,
        # )

        return data_pd
