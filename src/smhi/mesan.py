"""SMHI Mesan API module."""
import json
import arrow
import requests
import pandas as pd
from functools import wraps
from smhi.constants import MESAN_URL
from typing import Any, Callable, Optional
from requests.structures import CaseInsensitiveDict


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
        def inner(self, *args: Any) -> pd.DataFrame:
            url = func(self, *args)
            data, header, status = self._get_data(url)
            self.status = status
            self.header = header

            if key == "approvedTime" or key == "validTime":
                return self._format_time(key, data)
            elif key == "coordinates":
                return self._format_coordinate(key, data)
            elif key == "parameter":
                return self._format_parameters(key, data)
            else:
                return self._format_data(key, data)

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

    @get_data()
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

    @get_data()
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

    def _format_time(self, key: str, data: dict) -> list:
        """Format valid and approved time.

        Args:
            key: key in dictionary holding data
            data: data in dictionary

        Returns:
            data list
        """
        return data[key]

    def _format_coordinate(self, key, data):
        """Format polygon and multipoint.

        Args:
            key: key in dictionary holding data
            data: data in dictionary

        Returns:
            data list
        """
        if data["type"] == "Polygon":
            return data[key]

        if data["type"] == "MultiPoint":
            return data[key]

    def _format_parameters(self, key, data):
        """Format parameters.

        Args:
            key: key in dictionary holding data
            data: data in dictionary

        Returns:
            data list
        """
        return data[key]

    def _format_data(self, key, data) -> pd.DataFrame:
        """Format data.

        Args:
            key: key in dictionary holding data
            data: data in dictionary

        Returns:
            data: pandas DataFrame
        """
        if "geometry" in data:
            # df = pd.DataFrame.from_records(data["timeSeries"])
            # for a in range(len(df)):
            #     df["validTime"][a] = dt.datetime.strptime(
            #         df["validTime"][a], "%Y-%m-%dT%H:%M:%SZ"
            #     )

            # for s in range(len(df["parameters"][6])):
            #     tmplist = []
            #     parname = df["parameters"][6][s]["name"]
            #     name = parname + " [" + df["parameters"][6][s]["unit"] + "]"
            #     for t in range(len(df)):
            #         names = [
            #             df["parameters"][t][u]["name"]
            #             for u in range(len(df["parameters"][t]))
            #         ]
            #         if parname in names:
            #             pos = names.index(parname)
            #             tmplist.append(df["parameters"][t][pos]["values"][0])
            #         else:
            #             tmplist.append("NaN")

            #     df[name] = tmplist

            # df.drop("parameters", axis=1, inplace=True)
            # df.set_index("validTime", inplace=True)
            data_temporary = pd.DataFrame(data["timeSeries"]).explode("parameters")
            data = pd.concat(
                [
                    data_temporary.drop("parameters", axis=1),
                    data_temporary["parameters"].apply(pd.Series).explode("values"),
                ],
                axis=1,
            )
            data["validTime"] = data["validTime"].apply(lambda x: arrow.get(x).datetime)
            data = data.pivot_table(
                index="validTime",
                columns=["name", "unit"],
                values=["values"],
                aggfunc="first",
            )
            return data
        else:
            return data
