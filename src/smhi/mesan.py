"""SMHI Mesan API module."""
import json
import arrow
import requests
import pandas as pd
from functools import wraps
from typing import Any, Callable, Union, Optional
from requests.structures import CaseInsensitiveDict
from smhi.constants import MESAN_URL, MESAN_LEVELS_UNIT


def get_data(key: Optional[str] = None) -> Callable:
    """Get data from url wrapper.

    Args:
        key: key to index returned dict

    Returns:
        function get_data_inner
    """

    def get_data_inner(func: Callable) -> Callable:
        """Get data from url inner.

        Args:
            function func

        Returns:
            function inner
        """

        @wraps(func)
        def inner(self, *args: Any) -> Optional[Union[list, pd.DataFrame]]:
            url = func(self, *args)
            data, header, status = self._get_data(url)
            self.status = status
            self.header = header

            if key == "approvedTime" or key == "validTime":
                return data[key]
            elif key == "coordinates":
                return data[key]
            elif key == "parameter":
                return data[key]
            elif key == "point":
                return self._format_data_point(data)
            else:
                return self._format_data_multipoint(data)

        return inner

    return get_data_inner


class Mesan:
    """SMHI Mesan module."""

    def __init__(self) -> None:
        """Initialise Mesan."""
        self._category: str = "mesan1g"
        self._version: int = 2

        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.status: Optional[bool] = None
        self.header: Optional[CaseInsensitiveDict[str]] = None
        self.base_url: str = MESAN_URL.format(
            category=self._category, version=self._version
        )
        self.url: Optional[str] = None

    @property
    @get_data("approvedTime")
    def approved_time(self) -> str:
        """Get approved time.

        Returns:
            approved times
        """
        return self.base_url + "approvedtime.json"

    @property
    @get_data("validTime")
    def valid_time(self) -> str:
        """Get valid time.

        Returns:
            valid times
        """
        return self.base_url + "validtime.json"

    @property
    @get_data("coordinates")
    def geo_polygon(self) -> str:
        """Get geographic area polygon.

        Returns:
            polygon data
        """
        return self.base_url + "geotype/polygon.json"

    @get_data("coordinates")
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

        return self.base_url + multipoint_url

    @property
    @get_data("parameter")
    def parameters(self) -> str:
        """Get parameters.

        Returns:
            available parameters
        """
        return self.base_url + "parameter.json"

    @get_data("point")
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
        return (
            self.base_url
            + "geotype/point/lon/{longitude}/lat/{latitude}/data.json".format(
                longitude=longitude, latitude=latitude
            )
        )

    @get_data("multipoint")
    def get_multipoint(
        self,
        validtime: str,
        parameter: str,
        leveltype: str,
        level: int,
        downsample: int = 2,
    ) -> str:
        """Get multipoint data.

        Args:
            validtime: valid time
            parameter: parameter
            leveltype: level type
            level: level
            downsample: downsample

        Returns:
            data
        """
        validtime = arrow.get(validtime).format("YYYYMMDDThhmmss") + "Z"
        return (
            self.base_url
            + "geotype/multipoint/"
            + "validtime/{YYMMDDThhmmssZ}/parameter/{p}/leveltype/".format(
                YYMMDDThhmmssZ=validtime,
                p=parameter,
            )
            + "{lt}/level/{l}/data.json?with-geo=false&downsample={downsample}".format(
                lt=leveltype,
                l=level,
                downsample=downsample,
            )
        )

    def _get_data(
        self, url
    ) -> tuple[Optional[dict[str, Any]], CaseInsensitiveDict[str], bool]:
        """Get requested data.

        Args:
            url: url to get from

        Returns:
            data of response
            header of response
            status of response
        """
        response = requests.get(url)
        status = response.ok
        header = response.headers

        if status:
            return json.loads(response.content), header, status
        else:
            return None, header, status

    def _format_data_point(self, data: dict) -> Optional[pd.DataFrame]:
        """Format data for point request.

        Args:
            key: key in dictionary holding data
            data: data in dictionary

        Returns:
            data_table: pandas DataFrame
        """
        data_table = None

        if "geometry" in data:
            data0 = pd.DataFrame(data["timeSeries"]).explode("parameters")
            data0 = pd.concat(
                [
                    data0.drop("parameters", axis=1),
                    data0["parameters"].apply(pd.Series).explode("values"),
                ],
                axis=1,
            )
            data0["validTime"] = data0["validTime"].apply(
                lambda x: arrow.get(x).datetime
            )

            data2 = data0.pivot_table(
                index="validTime",
                columns=["levelType"],
                values="level",
                aggfunc="first",
            )
            data2.columns = pd.MultiIndex.from_arrays(
                [data2.columns, [MESAN_LEVELS_UNIT] * len(data2.columns)]
            )
            data2.columns.names = ["levelType", "unit"]

            data1 = data0.pivot_table(
                index="validTime",
                columns=["name", "unit"],
                values="values",
                aggfunc="first",
            )

            data_table = data1.join(data2)

        return data_table

    def _format_data_multipoint(self, data: dict) -> Optional[pd.DataFrame]:
        """Format data for multipoint request.

        Args:
            key: key in dictionary holding data
            data: data in dictionary

        Returns:
            data_table: pandas DataFrame
        """
        data_table = None

        if "approvedTime" in data:
            data0 = pd.DataFrame(data["timeSeries"]).explode("parameters")
            data0["approvedTime"] = data["approvedTime"]
            data0["referenceTime"] = data["referenceTime"]
            for date in ["validTime", "approvedTime", "referenceTime"]:
                data0[date] = data0[date].apply(lambda x: arrow.get(x).datetime)
            data0 = pd.concat(
                [
                    data0.drop("parameters", axis=1),
                    data0["parameters"].apply(pd.Series).explode("values"),
                ],
                axis=1,
            )
            data0["values"] = data0["values"].apply(pd.to_numeric)
            data_table = data0.reset_index(drop=True)

        return data_table
