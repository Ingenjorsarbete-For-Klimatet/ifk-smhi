"""SMHI Snow API module."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union

import arrow
import pandas as pd
from requests.structures import CaseInsensitiveDict

from smhi.constants import (
    SNOW_LEVELS_UNIT,
    SNOW_PARAMETER_DESCRIPTIONS,
    SNOW_URL,
)
from smhi.models.snow_model import (
    SnowCreatedTime,
    SnowGeoMultiPoint,
    SnowGeoPolygon,
    SnowMultiPoint,
    SnowParameter,
    SnowPoint,
    SnowValidTime,
)
from smhi.utils import format_datetime, get_request

logger = logging.getLogger(__name__)


class Snow:
    """SMHI Snow module."""

    _parameters_model: type[SnowParameter] = SnowParameter
    _created_time_model: type[SnowCreatedTime] = SnowCreatedTime
    _times_model: type[SnowValidTime] = SnowValidTime
    _geo_polygon_model: type[SnowGeoPolygon] = SnowGeoPolygon
    _geo_multipoint_model: type[SnowGeoMultiPoint] = SnowGeoMultiPoint
    _point_data_model: type[SnowPoint] = SnowPoint
    _multipoint_data_model: type[SnowMultiPoint] = SnowMultiPoint

    _category: str = "snow1g"
    _version: int = 1
    _base_url: str = SNOW_URL
    _parameter_descriptions: Dict[str, str] = SNOW_PARAMETER_DESCRIPTIONS

    def __init__(self) -> None:
        """Initialise Snow."""
        self._base_url: str = self._base_url.format(
            category=self._category, version=self._version
        )
        self._parameters = self._get_parameters()

    @property
    def parameter_descriptions(self) -> Dict[str, str]:
        """Get parameter descriptions from object state.

        Returns:
            parameter model
        """
        return self._parameter_descriptions

    @property
    def parameters(self) -> SnowParameter:
        """Get parameters from object state.

        Returns:
            parameter model
        """
        return self._parameters

    def _get_parameters(self) -> SnowParameter:
        """Get parameters from SMHI.

        Returns:
            parameter model
        """
        url = self._base_url + "parameter.json"
        data, headers, status = self._get_data(url)

        return self._parameters_model(
            url=url, status=status, headers=headers, parameter=data["parameter"]
        )

    @property
    def created_time(self) -> SnowCreatedTime:
        """Get created time.

        Returns:
            created time model
        """
        url = self._base_url + "createdtime.json"
        data, headers, status = self._get_data(url)

        return self._created_time_model(
            url=url,
            status=status,
            headers=headers,
            created_time=data["createdTime"],
            reference_time=data["referenceTime"],
        )

    @property
    def times(self) -> SnowValidTime:
        """Get valid time.

        Returns:
            valid time model
        """
        url = self._base_url + "times.json"
        data, headers, status = self._get_data(url)

        return self._times_model(
            url=url, status=status, headers=headers, times=data["time"]
        )

    @property
    def geo_polygon(self) -> SnowGeoPolygon:
        """Get geographic area polygon.

        Returns:
            polygon model
        """
        url = self._base_url + "geotype/polygon.json"
        data, headers, status = self._get_data(url)

        return self._geo_polygon_model(
            url=url,
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_geo_multipoint(self, downsample: int = 2) -> SnowGeoMultiPoint:
        """Get geographic area multipoint.

        Args:
            downsample: downsample parameter

        Returns:
            multipoint polygon model
        """
        downsample = self._check_downsample(downsample)
        url = self._base_url + f"geotype/multipoint.json?downsample={downsample}"
        data, headers, status = self._get_data(url)

        return self._geo_multipoint_model(
            url=url,
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_point(
        self,
        latitude: float,
        longitude: float,
    ) -> SnowPoint:
        """Get data for given lon and lat.

        Args:
            latitude: latitude
            longitude: longitude

        Returns:
            point data model
        """
        url = self._base_url + f"geotype/point/lon/{longitude}/lat/{latitude}/data.json"
        data, headers, status = self._get_data(url)
        data_table = self._format_data_point(data)
        data["geometry"]["coordinates"] = [
            [data["geometry"]["coordinates"][0]],
            [data["geometry"]["coordinates"][1]],
        ]  # TODO: consider to remove one list (depedency in smhi module)
        return self._point_data_model(
            longitude=longitude,
            latitude=latitude,
            url=url,
            created_time=data["createdTime"],
            reference_time=data["referenceTime"],
            geometry=data["geometry"],
            level_unit=SNOW_LEVELS_UNIT,
            status=status,
            headers=headers,
            df=data_table,
        )

    def get_multipoint(
        self,
        times: Union[str, datetime],
        parameter: str,
        geo: bool = True,
        downsample: int = 2,
    ) -> SnowMultiPoint:
        """Get multipoint data.

        Args:
            times: valid time
            parameter: parameter
            geo: fetch geography data
            downsample: downsample

        Returns:
            multipoint data model

        Raises:
            ValueError
        """
        times = format_datetime(times)
        if self._check_valid_time(times) is False:
            raise ValueError(f"Invalid time {times}.")

        url = self._build_multipoint_url(times, parameter, geo, downsample)
        data, headers, status = self._get_data(url)
        data_table = self._format_data_multipoint(data, parameter)

        return self._multipoint_data_model(
            parameter=parameter,
            parameter_meaning=self._parameter_descriptions[parameter],
            geo=geo,
            downsample=downsample,
            url=url,
            created_time=data["createdTime"],
            reference_time=data["referenceTime"],
            times=data["timeSeries"][0]["time"],
            status=status,
            headers=headers,
            df=data_table,
        )

    def _check_downsample(self, downsample: int) -> int:
        """Check that downsample parameter is within valid bounds.

        Args:
            downsample: downsample factor

        Returns:
            bounded downsample factor
        """
        if downsample < 1:
            logger.warning("Downsample set too low, will use downsample=1.")
            return 1
        elif downsample > 20:
            logger.warning("Downsample set too high, will use downsample=20.")
            return 20
        else:
            return downsample

    def _get_data(self, url) -> tuple[dict[str, Any], CaseInsensitiveDict[str], bool]:
        """Get requested data.

        Args:
            url: url to get from

        Returns:
            data of response
            headers of response
            status of response
        """
        response = get_request(url)

        return json.loads(response.content), response.headers, response.status_code

    def _format_data_point(self, data: dict) -> pd.DataFrame:
        """Format data for point request.

        Args:
            data: data in dictionary

        Returns:
            data_table: pandas DataFrame
        """
        records = []
        for item in data["timeSeries"]:
            time = item["time"]
            for key, value in item["data"].items():
                records.append({"times": time, "name": key, "value": value})

        df_exploded = pd.DataFrame(records)
        df_exploded["times"] = df_exploded["times"].apply(
            lambda x: arrow.get(x).datetime
        )

        data_table = df_exploded.pivot_table(
            index="times", columns="name", values="value", aggfunc="first"
        )

        return data_table

    def _format_data_multipoint(self, data: dict, param: str) -> Optional[pd.DataFrame]:
        """Format data for multipoint request.

        Args:
            data: data in dictionary
            param: parameter to extract

        Returns:
            data_table: pandas DataFrame
        """
        formatted_data = {"value": data["timeSeries"][0]["data"][param]}
        if "geometry" in data:
            formatted_data["lat"] = [x[1] for x in data["geometry"]["coordinates"]]
            formatted_data["lon"] = [x[0] for x in data["geometry"]["coordinates"]]

        return pd.DataFrame(formatted_data)

    def _build_multipoint_url(
        self,
        times: Union[str, datetime],
        parameter: str,
        geo: bool,
        downsample: int,
    ) -> str:
        """Build multipoint url.

        Args:
            times: valid time
            parameter: parameter
            geo: geo
            downsample downsample

        Returns:
            valid multipoint url
        """
        times = format_datetime(times)
        downsample = self._check_downsample(downsample)
        geo_url = "true" if geo is True else "false"

        return (
            self._base_url
            + "geotype/multipoint/"
            + f"time/{times}/parameter/{parameter}/"
            + f"data.json?with-geo={geo_url}&downsample={downsample}"
        )

    def _check_valid_time(self, test_time: Union[str, datetime]) -> bool:
        """Check if time is valid, that is within the forecast horizon.

        This might be overly restrictive but avoids an extra API call for each get_multipoint.

        Args:
            test_time: time to check

        Returns
            true if valid and false if not valid
        """
        times = format_datetime(test_time)
        return -1 < (arrow.get(times) - arrow.now("Z").shift(hours=-1)).days < 10
