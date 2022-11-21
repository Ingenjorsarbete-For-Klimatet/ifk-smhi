"""SMHI Metobs client."""
import io
import json
import logging
import requests
import pandas as pd
from typing import Union, Optional, Any
from smhi.constants import METOBS_URL, TYPE_MAP, METOBS_AVAILABLE_PERIODS


class Metobs:
    """SMHI Metobs class."""

    def __init__(self, data_type: str = "json") -> None:
        """Initialise the SMHI Metobs class with a data type format used to get data.

        For now, only supports `json` and version 1.

        Args:
            data_type: type of request
        """
        if data_type != "json":
            raise NotImplementedError(
                "API for type {0} is not supported for now. Use json".format(data_type)
            )

        self.data_type = TYPE_MAP[data_type]
        response = requests.get(METOBS_URL)
        self.headers = response.headers
        self.content = json.loads(response.content)
        self.available_versions = self.content["version"]

        self.version: Optional[Union[str, int]] = None
        self.parameters: Optional[MetobsParametersV1] = None
        self.stations: Optional[MetobsStationsV1] = None
        self.periods: Optional[MetobsPeriodsV1] = None
        self.data: Optional[MetobsDataV1] = None
        self.table_raw: Optional[str] = None

    def get_parameters(self, version: Union[str, int] = "1.0"):
        """Get SMHI Metobs API parameters from version. Only supports `version = 1.0`.

        Args:
            version: selected API version
        """
        if version == 1:
            version = "1.0"

        if version != "1.0":
            raise NotImplementedError(
                "Version {} not supported. Only supports version = 1.0.".format(version)
            )

        self.version = version
        self.parameters = MetobsParametersV1(self.available_versions)

    def get_stations(
        self, parameter: Optional[int] = None, parameter_title: Optional[str] = None
    ):
        """Get SMHI Metobs API (version 1) stations from given parameter.

        Args:
            parameter: integer id of parameter
            parameter_title: exact title of parameter
        """
        if self.parameters is None:
            logging.info("No parameters found, call get_parameters first.")
            return

        if parameter is None and parameter_title is None:
            raise NotImplementedError("Both arguments None.")

        if parameter:
            self.stations = MetobsStationsV1(
                self.parameters.resource, parameter=parameter
            )
        else:
            self.stations = MetobsStationsV1(
                self.parameters.resource, parameter_title=parameter_title
            )

    def get_periods(
        self, station: Optional[int] = None, stationset: Optional[str] = None
    ):
        """Get SMHI Metobs API (version 1) periods from given stations or stationset.

        Args:
            station: integer id of station
            stationset: exact title of station
        """
        if self.stations is None:
            logging.info("No stations found, call get_stations first.")
            return

        if station is None and stationset is None:
            raise NotImplementedError("Both arguments None.")

        if station:
            self.periods = MetobsPeriodsV1(self.stations.stations, station)
        else:
            self.periods = MetobsPeriodsV1(
                self.stations.stations, stationset=stationset
            )

    def get_data(self, period: str = "corrected-archive") -> tuple[Any, Any]:
        """Get SMHI Metobs API (version 1) data from given period.

        Args:
            period: period

        Returns:
            data headers
            data table
        """
        if self.periods is None:
            logging.info("No periods found, call get_periods first.")
            return None, None

        self.data = MetobsDataV1(self.periods.periods, period)
        self.table_raw = self.data.get()
        data_starting_point = self.table_raw.find("Datum")
        header = self.table_raw[0:data_starting_point]
        table = pd.read_csv(
            io.StringIO(self.table_raw[data_starting_point:-1]),
            sep=";",
            on_bad_lines="skip",
            usecols=[0, 1, 2],
        )
        return header, table

    def get_data_from_selection(
        self,
        parameter: int,
        station: int,
        period: str,
    ):
        """Get data from explicit parameters.

        Get data from explicit parameter, station and period,
        without inspecting each level. Note, no version parameters.

        Args:
            parameter: parameter to get
            station: station to get
            period: period to get

        Returns:
            data headers
            data table
        """
        self.get_parameters()
        self.get_stations(parameter)
        self.get_periods(station)
        header, table = self.get_data(period)
        return header, table

    def get_data_stationset(
        self,
        parameter: int,
        stationset: str,
        period: str,
    ):
        """Get data from stationset.

        Get data from explicit parameters, stations set and period,
        without inspecting each level. Note, no version parameters.

        Args:
            parameter: parameter to get
            stationset: stationset to get
            period: period to get

        Returns:
            data headers
            data table
        """
        self.get_parameters()
        self.get_stations(parameter)
        self.get_periods(None, stationset)
        header, table = self.get_data(period)
        return header, table

    def inspect(self, num_print: int = 10) -> None:
        """Inspect object state.

        Args:
            num_print: number of items to print
        """
        print("API version")
        print("Available versions: ", [x["key"] for x in self.available_versions])
        print("Selected version: ", self.version)
        print()

        if self.parameters:
            print("API parameters")
            print("Available parameters ({0} first): ".format(num_print))
            print(self.parameters.data[:num_print])
            print(
                "See all ({0}) parameters with client.parameters.data".format(
                    len(self.parameters.data)
                )
            )
            if self.stations:
                print("Selected parameters: ", self.stations.selected_parameter)
            print()

        if self.stations:
            print("API stations")
            print("Available stations ({0} first): ".format(num_print))
            print(self.stations.data[:num_print])
            print(
                "See all ({0}) stations with client.stations.data".format(
                    len(self.stations.data)
                )
            )
            if self.periods:
                print(
                    "Selected stations: {0} {1}".format(
                        self.periods.selected_station,
                        [
                            x[1]
                            for x in self.stations.data
                            if x[0] == self.periods.selected_station
                        ][0],
                    )
                )
            print()

        if self.periods:
            print("API periods")
            print("Available periods: ")
            print(self.periods.data)
            if self.data:
                print("Selected periods: ", self.data.selected_period)
            print()


class MetobsLevelV1:
    """Base Metobs level version 1 class."""

    def __init__(self):
        """Initialise base class."""
        self.headers = None
        self.key = None
        self.updated = None
        self.title = None
        self.summary = None
        self.link = None
        self.data_type = None

    def _get_and_parse_request(self, url: str):
        """Get and parse API request. Only JSON supported.

        Args:
            url: url to get from

        Returns:
            jsonified content
        """
        response = requests.get(url)
        content = json.loads(response.content)

        self.headers = response.headers
        self.key = content["key"]
        self.updated = content["updated"]
        self.title = content["title"]
        self.summary = content["summary"]
        self.link = content["link"]

        return content

    def _get_url(
        self,
        data: list[Any],
        key: str,
        parameter: Union[str, int],
        data_type: str = "json",
    ) -> str:
        """Get the url to get data from. Defaults to type json.

        Args:
            data: data list
            key: key to look up
            parameter: parameter to look for
            data_type: data type of requested url

        Returns:
            url

        Raises:
            IndexError
        """
        self.data_type = data_type = TYPE_MAP[data_type]
        try:
            requested_data = [x for x in data if x[key] == str(parameter)][0]["link"]
            url = [x["href"] for x in requested_data if x["type"] == self.data_type][0]
            return url
        except IndexError:
            raise IndexError("Can't find data for parameters: {p}".format(p=parameter))
        except KeyError:
            raise KeyError("Can't find key: {key}".format(key=key))


class MetobsParametersV1(MetobsLevelV1):
    """Get parameters for version 1 of Metobs API."""

    def __init__(
        self,
        data: list[Any],
        version: Union[str, int] = "1.0",
        data_type: str = "json",
    ) -> None:
        """Get parameters from version.

        Args:
            data: available API versions
            version: selected version
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: version not implemented
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if version != 1 and version != "1.0":
            raise NotImplementedError("Only supports version 1.0.")

        self.selected_version = "1.0" if version == 1 else version
        url = self._get_url(data, "key", version, data_type)
        content = self._get_and_parse_request(url)
        self.resource = sorted(content["resource"], key=lambda x: int(x["key"]))
        self.data = tuple((x["key"], x["title"]) for x in self.resource)


class MetobsStationsV1(MetobsLevelV1):
    """Get stations from parameter for version 1 of Metobs API."""

    def __init__(
        self,
        data: list[Any],
        parameter: Optional[int] = None,
        parameter_title: Optional[str] = None,
        data_type: str = "json",
    ) -> None:
        """Get stations from parameters.

        Args:
            data: available API parameters
            parameter: integer parameter key to get
            parameter_title: exact parameter title to get
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: parameter not implemented
        """
        super().__init__()
        self.selected_parameter: Optional[Union[int, str]] = None

        if data_type != "json":
            raise TypeError("Only json supported.")

        if parameter is None and parameter_title is None:
            raise NotImplementedError("No parameter selected.")

        if parameter and parameter_title:
            raise NotImplementedError("Can't decide which input to select.")

        if parameter:
            self.selected_parameter = parameter
            url = self._get_url(data, "key", parameter, data_type)
        if parameter_title:
            self.selected_parameter = parameter_title
            url = self._get_url(data, "title", parameter_title, data_type)

        content = self._get_and_parse_request(url)
        self.valuetype = content["valueType"]
        self.stationset = content["stationSet"]
        self.stations = sorted(content["station"], key=lambda x: int(x["id"]))
        self.data = tuple((x["id"], x["name"]) for i, x in enumerate(self.stations))


class MetobsPeriodsV1(MetobsLevelV1):
    """Get periods from station for version 1 of Metobs API.

    Note that stationset_title is not supported
    """

    def __init__(
        self,
        data: list[Any],
        station: Optional[int] = None,
        station_name: Optional[str] = None,
        stationset: Optional[str] = None,
        data_type: str = "json",
    ) -> None:
        """Get periods from station.

        Args:
            data: available API stations
            station: integer station key to get
            station_name: exact station name to get
            stationset: station set to get
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: station not implemented
        """
        super().__init__()
        self.selected_station: Optional[Union[int, str]] = None

        if data_type != "json":
            raise TypeError("Only json supported.")

        if [station, station_name, stationset].count(None) == 3:
            raise NotImplementedError("No stations selected.")

        if [bool(x) for x in [station, station_name, stationset]].count(True) > 1:
            raise NotImplementedError("Can't decide which input to select.")

        if station:
            self.selected_station = station
            url = self._get_url(data, "key", station, data_type)
        if station_name:
            self.selected_station = station_name
            url = self._get_url(data, "title", station_name, data_type)
        if stationset:
            self.selected_station = stationset
            url = self._get_url(data, "key", stationset, data_type)

        content = self._get_and_parse_request(url)
        self.owner = content["owner"]
        self.ownercategory = content["ownerCategory"]
        self.measuringstations = content["measuringStations"]
        self.active = content["active"]
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.position = content["position"]
        self.periods = sorted(content["period"], key=lambda x: x["key"])
        self.data = [x["key"] for x in self.periods]


class MetobsDataV1(MetobsLevelV1):
    """Get data from period for version 1 of Metobs API."""

    def __init__(
        self,
        data: list[Any],
        period: str = "corrected-archive",
        data_type: str = "json",
    ) -> None:
        """Get data from period.

        Args:
            data: available API periods
            period: select period from:
                    latest-hour, latest-day, latest-months or corrected-archive
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
            NotImplementedError: period not implemented
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if period not in METOBS_AVAILABLE_PERIODS:
            raise NotImplementedError(
                "Select a supported periods: }"
                + ", ".join([p for p in METOBS_AVAILABLE_PERIODS])
            )

        self.selected_period = period
        url = self._get_url(data, "key", period, data_type)
        content = self._get_and_parse_request(url)
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.data = content["data"]

    def get(self, type: str = "text/plain") -> str:
        """Get the selected data file.

        Args:
            type: type of request

        Returns:
            utf-8 decoded response

        Raises:
            UnicodeEncodeError
        """
        for item in self.data:
            for link in item["link"]:
                if link["type"] != type:
                    continue

                response = requests.get(link["href"])

                break
            break

        try:
            return response.content.decode("utf-8")
        except UnicodeError:
            raise UnicodeError("Can't decode response.")
