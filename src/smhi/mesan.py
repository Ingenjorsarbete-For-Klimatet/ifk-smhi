"""SMHI Mesan API module."""

import json
import logging
from typing import Any, Dict, Optional

import arrow
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
from smhi.constants import (
    MESAN_LEVELS_UNIT,
    MESAN_PARAMETER_DESCRIPTIONS,
    MESAN_URL,
    STATUS_OK,
)
from smhi.models.mesan import (
    MesanApprovedTime,
    MesanMultiPointData,
    MesanParameters,
    MesanPointData,
    MesanPolygon,
    MesanValidTime,
)
from smhi.models.metfcts import (
    MetfctsApprovedTime,
    MetfctsMultiPointData,
    MetfctsParameters,
    MetfctsPointData,
    MetfctsPolygon,
    MetfctsValidTime,
)

logger = logging.getLogger(__name__)


class Mesan:
    """SMHI Mesan module."""

    __parameters_model = MesanParameters
    __approved_time_model = MesanApprovedTime
    __valid_time_model = MesanValidTime
    __polygon_model = MesanPolygon
    __point_data_model = MesanPointData
    __multipoint_data_model = MesanMultiPointData

    def __init__(self) -> None:
        """Initialise Mesan."""
        self._category: str = "mesan2g"
        self._version: int = 1
        self._base_url: str = MESAN_URL.format(
            category=self._category, version=self._version
        )
        self._parameters = self.__parameters_model(*self._get_parameters())
        self._parameter_descriptions = MESAN_PARAMETER_DESCRIPTIONS

    @property
    def parameter_descriptions(self) -> Dict[str, str]:
        """Get parameter descriptions from object state.

        Returns:
            mesan parameter model
        """
        return self._parameter_descriptions

    @property
    def parameters(self) -> MesanParameters | MetfctsParameters:
        """Get parameters from object state.

        Returns:
            mesan parameter model
        """
        return self._parameters.parameter

    def _get_parameters(self) -> MesanParameters:
        """Get parameters from SMHI.

        Returns:
            mesan parameter model
        """
        return self._get_data(self._base_url + "parameter.json")

    @property
    def approved_time(self) -> MesanApprovedTime | MetfctsApprovedTime:
        """Get approved time.

        Returns:
            approved times
        """
        data, headers, status = self._get_data(self._base_url + "approvedtime.json")

        return self.__approved_time_model(
            status=status,
            headers=headers,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
        )

    @property
    def valid_time(self) -> MesanValidTime | MetfctsValidTime:
        """Get valid time.

        Returns:
            mesan valid time
        """
        data, headers, status = self._get_data(self._base_url + "validtime.json")

        return self.__valid_time_model(
            status=status, headers=headers, valid_time=data["validTime"]
        )

    @property
    def geo_polygon(self) -> MesanPolygon | MetfctsPolygon:
        """Get geographic area polygon.

        Returns:
            mesan polygon model
        """
        data, headers, status = self._get_data(self._base_url + "geotype/polygon.json")

        return self.__polygon_model(
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_geo_multipoint(self, downsample: int = 2) -> MesanPolygon | MetfctsPolygon:
        """Get geographic area multipoint.

        Args:
            downsample: downsample parameter

        Returns:
            multipoint data
        """
        downsample_url = self._check_downsample(downsample)
        multipoint_url = f"geotype/multipoint.json?{downsample_url}"
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
    ) -> MesanPointData | MetfctsPointData:
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
    ) -> MesanMultiPointData | MetfctsMultiPointData:
        """Get multipoint data.

        Args:
            validtime: valid time
            parameter: parameter
            leveltype: level type
            level: level
            downsample: downsample
            geo: fetch geography data

        Returns:
            data
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

    def _check_downsample(self, downsample: int) -> str:
        if downsample < 1:
            logger.warning("Downsample set too low, will use downsample=1.")
            return ""
        elif downsample > 20:
            logger.warning("Downsample set too high, will use downsample=20.")
            return "downsample=20"
        else:
            return "downsample={downsample}".format(downsample=downsample)

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
        response = requests.get(url)
        status = response.status_code
        headers = response.headers

        if status == STATUS_OK:
            return json.loads(response.content), headers, status
        else:
            logger.warning(f"Request {url} failed.")
            return None, headers, status

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
                index="name",
                values=["level_type", "level", "unit"],
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
        if "geometry" in data:
            df = pd.DataFrame(
                {
                    "lat": [x[1] for x in data["geometry"]["coordinates"]],
                    "lon": [x[0] for x in data["geometry"]["coordinates"]],
                    "value": data["timeSeries"][0]["parameters"][0]["values"],
                }
            )
        else:
            df = pd.DataFrame(
                {
                    "value": data["timeSeries"][0]["parameters"][0]["values"],
                }
            )

        return df

    def _build_point_url(self, longitude, latitude):
        return (
            self._base_url
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=longitude, latitude=latitude
            )
        )

    def _build_multipoint_url(
        self, validtime, parameter, leveltype, level, geo, downsample
    ):
        validtime = arrow.get(validtime).format("YYYYMMDDThhmmss") + "Z"
        downsample_url = self._check_downsample(downsample)

        return (
            self._base_url
            + "geotype/multipoint/"
            + "validtime/{YYMMDDThhmmssZ}/parameter/{p}/leveltype/".format(
                YYMMDDThhmmssZ=validtime,
                p=parameter,
            )
            + "{lt}/level/{l}/data.json?with-geo={geo}&{downsample_url}".format(
                lt=leveltype,
                l=level,
                geo="true" if geo is True else "false",
                downsample_url=downsample_url,
            )
        )
