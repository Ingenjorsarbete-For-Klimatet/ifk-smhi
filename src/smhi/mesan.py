"""SMHI Mesan API module."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union

import arrow
import numpy as np
import pandas as pd
from requests.structures import CaseInsensitiveDict

from smhi.constants import (
    MESAN_LEVELS_UNIT,
    MESAN_PARAMETER_CATEGORIES,
    MESAN_PARAMETER_DESCRIPTIONS,
    MESAN_PRECIPITATION_FROZEN_PART_NO_PRECIPITATION,
    MESAN_URL,
)
from smhi.models.mesan_model import (
    MesanCreatedTime,
    MesanGeoMultiPoint,
    MesanGeoPolygon,
    MesanMultiPoint,
    MesanParameter,
    MesanPoint,
    MesanValidTime,
)
from smhi.models.variable_model import (
    ApprovedTime,
    GeoMultiPoint,
    GeoPolygon,
    MultiPoint,
    Parameter,
    Point,
    ValidTime,
)
from smhi.utils import format_datetime, get_request

logger = logging.getLogger(__name__)


class Mesan:
    """SMHI Mesan module."""

    __parameters_model: Parameter = MesanParameter
    __created_time_model: ApprovedTime = MesanCreatedTime
    __times_model: ValidTime = MesanValidTime
    __geo_polygon_model: GeoPolygon = MesanGeoPolygon
    __geo_multipoint_model: GeoMultiPoint = MesanGeoMultiPoint
    __point_data_model: Point = MesanPoint
    __multipoint_data_model: MultiPoint = MesanMultiPoint

    _category: str = "mesan2g"
    _version: int = 3
    _base_url: str = MESAN_URL
    _parameter_descriptions: Dict[str, str] = MESAN_PARAMETER_DESCRIPTIONS
    _parameter_categories: Dict[str, Dict[int, str]] = MESAN_PARAMETER_CATEGORIES

    def __init__(self) -> None:
        """Initialise Mesan."""
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
    def parameter_categories(self) -> Dict[str, Dict[int, str]]:
        """Get category value descriptions per parameter from object state.

        Only parameters with categorical values have an entry.

        Returns:
            mapping of parameter name to category value descriptions
        """
        return self._parameter_categories

    @property
    def parameters(self) -> Parameter:
        """Get parameters from object state.

        Returns:
            parameter model
        """
        return self._parameters

    def _get_parameters(self) -> Parameter:
        """Get parameters from SMHI.

        Returns:
            parameter model
        """
        url = self._base_url + "parameter.json"
        data, headers, status = self._get_data(url)

        return self.__parameters_model(
            url=url, status=status, headers=headers, parameter=data["parameter"]
        )

    @property
    def created_time(self) -> ApprovedTime:
        """Get created time.

        Returns:
            created time model
        """
        url = self._base_url + "createdtime.json"
        data, headers, status = self._get_data(url)

        return self.__created_time_model(
            url=url,
            status=status,
            headers=headers,
            created_time=data["createdTime"],
            reference_time=data["referenceTime"],
        )

    @property
    def times(self) -> ValidTime:
        """Get valid time.

        Returns:
            valid time model
        """
        url = self._base_url + "times.json"
        data, headers, status = self._get_data(url)

        return self.__times_model(
            url=url, status=status, headers=headers, times=data["time"]
        )

    @property
    def geo_polygon(self) -> GeoPolygon:
        """Get geographic area polygon.

        Returns:
            polygon model
        """
        url = self._base_url + "geotype/polygon.json"
        data, headers, status = self._get_data(url)

        return self.__geo_polygon_model(
            url=url,
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_geo_multipoint(self, downsample: int = 2) -> GeoMultiPoint:
        """Get geographic area multipoint.

        Args:
            downsample: downsample parameter

        Returns:
            multipoint polygon model
        """
        downsample = self._check_downsample(downsample)
        url = self._base_url + f"geotype/multipoint.json?downsample={downsample}"
        data, headers, status = self._get_data(url)

        return self.__geo_multipoint_model(
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
    ) -> Point:
        """Get data for given lon, lat and parameter.

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
        return self.__point_data_model(
            longitude=longitude,
            latitude=latitude,
            url=url,
            created_time=data["createdTime"],
            reference_time=data["referenceTime"],
            geometry=data["geometry"],
            level_unit=MESAN_LEVELS_UNIT,
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
    ) -> MultiPoint:
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
        if self._check_times(times) is False:
            raise ValueError(f"Invalid time {times}.")

        url = self._build_multipoint_url(times, parameter, geo, downsample)
        data, headers, status = self._get_data(url)
        data_table = self._format_data_multipoint(data, parameter)

        return self.__multipoint_data_model(
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
        # Convert timeSeries list to DataFrame
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

        return self._mask_missing_data_point(data_table)

    def _format_data_multipoint(self, data: dict, param: str) -> Optional[pd.DataFrame]:
        """Format data for multipoint request.

        Args:
            data: data in dictionary
            param: parameter to extract

        Returns:
            data_table: pandas DataFrame
        """
        missing_value = self._get_missing_values().get(param)
        values = data["timeSeries"][0]["data"][param]
        masked_values = [
            np.nan if self._is_missing_value(param, value, missing_value) else value
            for value in values
        ]
        formatted_data = {"value": masked_values}
        if "geometry" in data:
            formatted_data["lat"] = [x[1] for x in data["geometry"]["coordinates"]]
            formatted_data["lon"] = [x[0] for x in data["geometry"]["coordinates"]]

        return pd.DataFrame(formatted_data)

    def _get_missing_values(self) -> Dict[str, int]:
        """Get missing value sentinel for each parameter.

        Returns:
            mapping of parameter name to its missing value
        """
        return {p.name: p.missing_value for p in self._parameters.parameter}

    def _is_missing_value(
        self, param: str, value: Any, missing_value: Optional[int]
    ) -> bool:
        """Check if a value is a missing value sentinel.

        The MESAN2g API sets precipitation_frozen_part to -9 when there
        is no precipitation, per the SMHI parameter documentation.

        Args:
            param: parameter name
            value: value to check
            missing_value: missing value sentinel of the parameter

        Returns:
            true if the value is a missing value sentinel
        """
        if missing_value is not None and value == missing_value:
            return True

        return (
            param == "precipitation_frozen_part"
            and value == MESAN_PRECIPITATION_FROZEN_PART_NO_PRECIPITATION
        )

    def _mask_missing_data_point(self, data_table: pd.DataFrame) -> pd.DataFrame:
        """Mask missing value sentinels in a point data table.

        Args:
            data_table: pandas DataFrame of point data

        Returns:
            data_table: pandas DataFrame with missing values as NaN
        """
        for name, missing_value in self._get_missing_values().items():
            if name in data_table.columns:
                data_table[name] = data_table[name].replace(missing_value, np.nan)

        if "precipitation_frozen_part" in data_table.columns:
            data_table["precipitation_frozen_part"] = data_table[
                "precipitation_frozen_part"
            ].replace(MESAN_PRECIPITATION_FROZEN_PART_NO_PRECIPITATION, np.nan)

        return data_table

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

    def _check_times(self, test_time: Union[str, datetime]) -> bool:
        """Check if time is valid, that is within a day window.

        This might be overly restrictive but avoids an extra API call for each get_multipoint.

        Args:
            test_time: time to check

        Returns
            true if valid and false if not valid
        """
        times = format_datetime(test_time)
        return -1 < (arrow.now("Z").shift(hours=-1) - arrow.get(times)).days < 1
