"""SMHI Mesan API module."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Union

import arrow
import pandas as pd
from requests.structures import CaseInsensitiveDict
from smhi.constants import (
    MESAN_LEVELS_UNIT,
    MESAN_PARAMETER_DESCRIPTIONS,
    MESAN_URL,
)
from smhi.models.mesan_model import (
    MesanApprovedTime,
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
    __approved_time_model: ApprovedTime = MesanApprovedTime
    __valid_time_model: ValidTime = MesanValidTime
    __geo_polygon_model: GeoPolygon = MesanGeoPolygon
    __geo_multipoint_model: GeoMultiPoint = MesanGeoMultiPoint
    __point_data_model: Point = MesanPoint
    __multipoint_data_model: MultiPoint = MesanMultiPoint

    _category: str = "mesan2g"
    _version: int = 1
    _base_url: str = MESAN_URL
    _parameter_descriptions: Dict[str, str] = MESAN_PARAMETER_DESCRIPTIONS

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
    def approved_time(self) -> ApprovedTime:
        """Get approved time.

        Returns:
            approved time model
        """
        url = self._base_url + "approvedtime.json"
        data, headers, status = self._get_data(url)

        return self.__approved_time_model(
            url=url,
            status=status,
            headers=headers,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
        )

    @property
    def valid_time(self) -> ValidTime:
        """Get valid time.

        Returns:
            valid time model
        """
        url = self._base_url + "validtime.json"
        data, headers, status = self._get_data(url)

        return self.__valid_time_model(
            url=url, status=status, headers=headers, valid_time=data["validTime"]
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
        data_table, info_table = self._format_data_point(data)

        return self.__point_data_model(
            longitude=longitude,
            latitude=latitude,
            url=url,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
            geometry=data["geometry"],
            level_unit=MESAN_LEVELS_UNIT,
            status=status,
            headers=headers,
            df=data_table,
            df_info=info_table,
        )

    def get_multipoint(
        self,
        valid_time: Union[str, datetime],
        parameter: str,
        level_type: str,
        level: int,
        geo: bool = True,
        downsample: int = 2,
    ) -> MultiPoint:
        """Get multipoint data.

        Args:
            valid_time: valid time
            parameter: parameter
            level_type: level type
            level: level
            geo: fetch geography data
            downsample: downsample

        Returns:
            multipoint data model

        Raises:
            ValueError
        """
        valid_time = format_datetime(valid_time)
        if self._check_valid_time(valid_time) is False:
            raise ValueError(f"Invalid time {valid_time}.")

        url = self._build_multipoint_url(
            valid_time, parameter, level_type, level, geo, downsample
        )
        data, headers, status = self._get_data(url)
        data_table = self._format_data_multipoint(data)

        return self.__multipoint_data_model(
            parameter=parameter,
            parameter_meaning=self._parameter_descriptions[parameter],
            geo=geo,
            downsample=downsample,
            url=url,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
            valid_time=data["timeSeries"][0]["validTime"],
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

    def _format_data_point(self, data: dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Format data for point request.

        Args:
            data: data in dictionary

        Returns:
            data_table: pandas DataFrame
        """
        df = pd.DataFrame(data["timeSeries"]).explode("parameters")
        df_exploded = pd.concat(
            [
                df.drop("parameters", axis=1),
                df["parameters"].apply(pd.Series).explode("values"),
            ],
            axis=1,
        )
        df_exploded["validTime"] = df_exploded["validTime"].apply(
            lambda x: arrow.get(x).datetime
        )
        df_exploded = df_exploded.rename(
            columns={
                "values": "value",
                "validTime": "valid_time",
                "levelType": "level_type",
            }
        )

        data_table = df_exploded.pivot_table(
            index="valid_time", columns="name", values="value", aggfunc="first"
        )
        # https://github.com/pandas-dev/pandas-stubs/issues/885
        info_table = df_exploded.pivot_table(
            index="name",
            values=["level_type", "level", "unit"],  # type: ignore
            aggfunc="first",
        )

        return data_table, info_table

    def _format_data_multipoint(self, data: dict) -> Optional[pd.DataFrame]:
        """Format data for multipoint request.

        Args:
            key: key in dictionary holding data
            data: data in dictionary

        Returns:
            data_table: pandas DataFrame
        """
        formatted_data = {"value": data["timeSeries"][0]["parameters"][0]["values"]}
        if "geometry" in data:
            formatted_data["lat"] = [x[1] for x in data["geometry"]["coordinates"]]
            formatted_data["lon"] = [x[0] for x in data["geometry"]["coordinates"]]

        return pd.DataFrame(formatted_data)

    def _build_multipoint_url(
        self,
        valid_time: Union[str, datetime],
        parameter: str,
        level_type: str,
        level: int,
        geo: bool,
        downsample: int,
    ) -> str:
        """Build multipoint url.

        Args:
            valid_time: valid time
            parameter: parameter
            level_type: level type
            level: level
            geo: geo
            downsample downsample

        Returns:
            valid multipoint url
        """
        valid_time = format_datetime(valid_time)
        downsample = self._check_downsample(downsample)
        geo_url = "true" if geo is True else "false"

        return (
            self._base_url
            + "geotype/multipoint/"
            + f"validtime/{valid_time}/parameter/{parameter}/leveltype/"
            + f"{level_type}/level/{level}/data.json?with-geo={geo_url}&downsample={downsample}"
        )

    def _check_valid_time(self, test_time: Union[str, datetime]) -> bool:
        """Check if time is valid, that is within a day window.

        This might be overly restrictive but avoids an extra API call for each get_multipoint.

        Args:
            test_time: time to check

        Returns
            true if valid and false if not valid
        """
        valid_time = format_datetime(test_time)
        return -1 < (arrow.now("Z").shift(hours=-1) - arrow.get(valid_time)).days < 1
