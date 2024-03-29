"""SMHI Mesan API module."""

import json
from functools import wraps
from typing import Any, Callable, Optional, Union

import arrow
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
from smhi.constants import MESAN_LEVELS_UNIT, MESAN_URL, STATUS_OK

from smhi.models.mesan import (
    MesanParameters,
    MesanApprovedTime,
    MesanValidTime,
    MesanPolygon,
    MesanPointData,
    MesanMultiPointData,
)


class Mesan:
    """SMHI Mesan module."""

    def __init__(self) -> None:
        """Initialise Mesan."""
        self._category: str = "mesan2g"
        self._version: int = 1
        self._base_url: str = MESAN_URL.format(
            category=self._category, version=self._version
        )
        self._parameters = self._get_parameters()

    @property
    def parameters(self) -> MesanParameters:
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
        data, headers, status = self._get_data(self._base_url + "parameter.json")

        return MesanParameters(
            status=status, headers=headers, parameter=data["parameter"]
        )

    @property
    def approved_time(self) -> MesanApprovedTime:
        """Get approved time.

        Returns:
            approved times
        """
        data, headers, status = self._get_data(self._base_url + "approvedtime.json")

        return MesanApprovedTime(
            status=status,
            headers=headers,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
        )

    @property
    def valid_time(self) -> MesanValidTime:
        """Get valid time.

        Returns:
            mesan valid time
        """
        data, headers, status = self._get_data(self._base_url + "validtime.json")

        return MesanValidTime(
            status=status, headers=headers, valid_time=data["validTime"]
        )

    @property
    def geo_polygon(self) -> MesanPolygon:
        """Get geographic area polygon.

        Returns:
            mesan polygon model
        """
        data, headers, status = self._get_data(self._base_url + "geotype/polygon.json")

        return MesanPolygon(
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_geo_multipoint(self, downsample: int = 2) -> str:
        """Get geographic area multipoint.

        Args:
            downsample: downsample parameter

        Returns:
            multipoint data
        """
        if downsample < 1:
            multipoint_url = "geotype/multipoint.json"
        elif downsample > 20:
            multipoint_url = "geotype/multipoint.json?downsample=20"
        else:
            multipoint_url = "geotype/multipoint.json?downsample={downsample}".format(
                downsample=downsample
            )

        data, headers, status = self._get_data(self._base_url + multipoint_url)

        return MesanPolygon(
            status=status,
            headers=headers,
            type=data["type"],
            coordinates=data["coordinates"],
        )

    def get_point(
        self,
        latitude: float,
        longitude: float,
    ) -> str:
        """Get data for given lon, lat and parameter.

        Args:
            latitude: latitude
            longitude: longitude

        Returns:
            data
        """
        data, headers, status = self._get_data(
            self._base_url
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=longitude, latitude=latitude
            )
        )

        dataframes = self._format_data_point(data)

        return MesanPointData(
            status=status,
            headers=headers,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
            geometry=data["geometry"],
            valid_time=data["timeSeries"][0]["validTime"],
            level_unit=MESAN_LEVELS_UNIT,
            df=dataframes,
        )

    def get_multipoint(
        self,
        validtime: str,
        parameter: str,
        leveltype: str,
        level: int,
        downsample: int = 2,
        geo: bool = True,
    ) -> str:
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
        validtime = arrow.get(validtime).format("YYYYMMDDThhmmss") + "Z"

        data, headers, status = self._get_data(
            self._base_url
            + "geotype/multipoint/"
            + "validtime/{YYMMDDThhmmssZ}/parameter/{p}/leveltype/".format(
                YYMMDDThhmmssZ=validtime,
                p=parameter,
            )
            + "{lt}/level/{l}/data.json?with-geo={geo}&downsample={downsample}".format(
                lt=leveltype,
                l=level,
                geo={"true" if geo is True else "false"},
                downsample=downsample,
            )
        )

        dataframe = self._format_data_multipoint(data)

        return MesanMultiPointData(
            status=status,
            headers=headers,
            approved_time=data["approvedTime"],
            reference_time=data["referenceTime"],
            valid_time=data["timeSeries"][0]["validTime"],
            df=dataframe,
        )

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
            return None, headers, status

    def _format_data_point(self, data: dict) -> Optional[pd.DataFrame]:
        """Format data for point request.

        Args:
            data: data in dictionary

        Returns:
            data_table: pandas DataFrame
        """
        data_table = None

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
            data_table = df_exploded.pivot_table(
                index="validTime",
                columns=["name", "levelType", "level", "unit"],
                values="values",
                aggfunc="first",
            )

        return data_table

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
