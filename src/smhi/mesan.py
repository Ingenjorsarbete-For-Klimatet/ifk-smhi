"""SMHI Mesan API module."""

import json
import logging
from typing import Any, Dict, Optional

import arrow
import pandas as pd
from requests.structures import CaseInsensitiveDict
from smhi.constants import (
    MESAN_LEVELS_UNIT,
    MESAN_PARAMETER_DESCRIPTIONS,
    MESAN_URL,
)
from smhi.models.mesan import (
    MesanApprovedTime,
    MesanMultiPointData,
    MesanParameters,
    MesanPointData,
    MesanPolygon,
    MesanValidTime,
)
from smhi.models.variable import (
    ApprovedTime,
    MultiPointData,
    Parameters,
    PointData,
    Polygon,
    ValidTime,
)
from smhi.utils import get_request

logger = logging.getLogger(__name__)


class Mesan:
    """SMHI Mesan module."""

    __parameters_model: Parameters = MesanParameters
    __approved_time_model: ApprovedTime = MesanApprovedTime
    __valid_time_model: ValidTime = MesanValidTime
    __polygon_model: Polygon = MesanPolygon
    __point_data_model: PointData = MesanPointData
    __multipoint_data_model: MultiPointData = MesanMultiPointData

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
    def parameters(self) -> Parameters:
        """Get parameters from object state.

        Returns:
            parameter model
        """
        return self._parameters.parameter

    def _get_parameters(self) -> Parameters:
        """Get parameters from SMHI.

        Returns:
            parameter model
        """
        data, headers, status = self._get_data(self._base_url + "parameter.json")
        return self.__parameters_model(
            status=status, headers=headers, parameter=data["parameter"]
        )

    @property
    def approved_time(self) -> ApprovedTime:
        """Get approved time.

        Returns:
            approved time model
        """
        data, headers, status = self._get_data(self._base_url + "approvedtime.json")

        return self.__approved_time_model(
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
        data, headers, status = self._get_data(self._base_url + "validtime.json")

        return self.__valid_time_model(
            status=status, headers=headers, valid_time=data["validTime"]
        )

    @property
    def geo_polygon(self) -> Polygon:
        """Get geographic area polygon.

        Returns:
            polygon model
        """
        data, headers, status = self._get_data(self._base_url + "geotype/polygon.json")

        return self.__polygon_model(
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_geo_multipoint(self, downsample: int = 2) -> Polygon:
        """Get geographic area multipoint.

        Args:
            downsample: downsample parameter

        Returns:
            multipoint polygon model
        """
        downsample = self._check_downsample(downsample)
        multipoint_url = f"geotype/multipoint.json?downsample={downsample}"
        data, headers, status = self._get_data(self._base_url + multipoint_url)

        return self.__polygon_model(
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_point(
        self,
        latitude: float,
        longitude: float,
    ) -> PointData:
        """Get data for given lon, lat and parameter.

        Args:
            latitude: latitude
            longitude: longitude

        Returns:
            point data model
        """
        url = self._build_point_url(longitude, latitude)
        data, headers, status = self._get_data(url)
        data_table, info_table = self._format_data_point(data)

        return self.__point_data_model(
            status=status,
            headers=headers,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
            geometry=data["geometry"],
            level_unit=MESAN_LEVELS_UNIT,
            df=data_table,
            df_info=info_table,
        )

    def get_multipoint(
        self,
        validtime: str,
        parameter: str,
        leveltype: str,
        level: int,
        downsample: int = 2,
        geo: bool = True,
    ) -> MultiPointData:
        """Get multipoint data.

        Args:
            validtime: valid time
            parameter: parameter
            leveltype: level type
            level: level
            downsample: downsample
            geo: fetch geography data

        Returns:
            multipoint data model
        """
        url = self._build_multipoint_url(
            validtime, parameter, leveltype, level, geo, downsample
        )
        data, headers, status = self._get_data(url)
        data_table = self._format_data_multipoint(data)

        return self.__multipoint_data_model(
            status=status,
            headers=headers,
            parameter=parameter,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
            valid_time=data["timeSeries"][0]["validTime"],
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

    def _get_data(
        self, url
    ) -> tuple[Optional[dict[str, Any]], CaseInsensitiveDict[str], bool]:
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

    def _format_data_point(self, data: dict) -> Optional[pd.DataFrame]:
        """Format data for point request.

        Args:
            data: data in dictionary

        Returns:
            data_table: pandas DataFrame
        """
        data_table = None
        info_table = None

        if "geometry" in data:
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
            info_table = df_exploded.pivot_table(
                index="name", values=["level_type", "level", "unit"], aggfunc="first"
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
        formatted_data = {"values": data["timeSeries"][0]["parameters"][0]["values"]}
        if "geometry" in data:
            formatted_data["lat"] = [x[1] for x in data["geometry"]["coordinates"]]
            formatted_data["lon"] = [x[0] for x in data["geometry"]["coordinates"]]

        return pd.DataFrame(formatted_data)

    def _build_point_url(self, lon: float, lat: float) -> str:
        """Build point url.

        Args:
            lon: longitude
            lat: latitude

        Returns:
            valid point url
        """
        return self._base_url + f"geotype/point/lon/{lon}/lat/{lat}/data.json"

    def _build_multipoint_url(
        self,
        validtime: str,
        parameter: str,
        leveltype: str,
        level: str,
        geo: bool,
        downsample: int,
    ) -> str:
        """Build multipoint url.

        Args:
            validtime:
            parameter:
            leveltype:
            level:
            geo:
            downsample:

        Returns:
            valid multipoint url
        """
        validtime = arrow.get(validtime).format("YYYYMMDDThhmmss") + "Z"
        downsample = self._check_downsample(downsample)
        geo_url = "true" if geo is True else "false"

        return (
            self._base_url
            + "geotype/multipoint/"
            + f"validtime/{validtime}/parameter/{parameter}/leveltype/"
            + f"{leveltype}/level/{level}/data.json?with-geo={geo_url}&downsample={downsample}"
        )
