"""
SMHI Meteorological Observations client.
"""
import io
import json
import requests
import pandas as pd
from typing import Union
from smhi.constants import METOBS_URL, TYPE_MAP, METOBS_AVAILABLE_PERIODS


class Metobs:
    """
    SMHI data class.
    """

    def __init__(self, data_type: str = "json"):
        """
        Initialise the SMHI Metobs class with a data type format used to get data.
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

        self.version = None
        self.parameters = None
        self.stations = None
        self.periods = None
        self.data = None
        self.table_raw = None

    def get_parameters(self, version: Union[str, int] = "1.0"):
        """
        Get SMHI Metobs API parameters from version. Only supports `version = 1.0`.

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

    def get_stations(self, parameters: str = None, parameters_title: str = None):
        """
        Get SMHI Metobs API (version 1) stations from given parameters.

        Args:
            parameters: id of data
            parameters_title: exact title of data
        """
        if parameters is None and parameters_title is None:
            raise NotImplementedError("Both arguments None.")

        if parameters:
            self.stations = MetobsStationsV1(
                self.parameters.resource, parameters=parameters
            )
        else:
            self.stations = MetobsStationsV1(
                self.parameters.resource, parameters_title=parameters_title
            )

    def get_periods(self, stations: str = None, stationset: str = None):
        """
        Get SMHI Metobs API (version 1) periods from given stations.

        Args:
            stations: id of data
            stationset: exact title of data
        """
        if stations is None and stationset is None:
            raise NotImplementedError("Both arguments None.")

        if stations:
            self.periods = MetobsPeriodsV1(self.stations.stations, stations)
        else:
            self.periods = MetobsPeriodsV1(
                self.stations.stations, stationset=stationset
            )

    def get_data(self, periods: str = "corrected-archive"):
        """
        Get SMHI Metobs API (version 1) data from given periods.

        Args:
            periods: periods
        """
        self.data = MetobsDataV1(self.periods.periods, periods)
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
        parameters: int,
        stations: int,
        periods: str,
    ):
        """
        Get data from explicit parameters selection and stations,
        without inspecting each level. Note, no version parameters.

        Args:
            parameters: API parameters
            stations: stations
            periods: periods to download
        """
        self.get_parameters()
        self.get_stations(parameters)
        self.get_periods(stations)
        header, table = self.get_data(periods)
        return header, table

    def get_data_stationset(
        self,
        parameters: int,
        stationset: int,
        periods: str,
    ):
        """
        Get data from explicit parameters selection and stations set,
        without inspecting each level. Note, no version parameters.

        Args:
            parameters: API parameters
            stationset: stations
            periods: periods to download
        """
        self.get_parameters()
        self.get_stations(parameters)
        self.get_periods(None, stationset)
        header, table = self.get_data(periods)
        return header, table

    def inspect(self, num_print: int = 10):
        """
        Inspect object state.

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
                print("Selected parameters: ", self.stations.selected_parameters)
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
                            x[2]
                            for x in self.stations.data
                            if x[1] == self.periods.selected_station
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
    """
    Base Metobs level version 1 class.
    """

    def __init__(self):
        """
        Initialise base class.
        """
        self.headers = None
        self.key = None
        self.updated = None
        self.title = None
        self.summary = None
        self.link = None
        self.data_type = None

    def _get_and_parse_request(self, url: str):
        """
        Get and parse API request. Only JSON supported.

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
        data: list,
        key: str,
        parameters: Union[str, int],
        data_type: str = "json",
    ):
        """
        Get the url to get data from. Defaults to type json.

        Args:
            data: data list
            key: key to look in
            parameters: parameters to look for
            data_type: data type of requested url

        Returns:
            url

        Raises:
            IndexError
        """
        self.data_type = data_type = TYPE_MAP[data_type]
        try:
            requested_data = [x for x in data if x[key] == str(parameters)][0]["link"]
            url = [x["href"] for x in requested_data if x["type"] == self.data_type][0]
            return url
        except IndexError:
            raise IndexError("Can't find data for parameters: {p}".format(p=parameters))
        except KeyError:
            raise KeyError("Can't find key: {key}".format(key=key))


class MetobsParametersV1(MetobsLevelV1):
    """
    Get parameters for version 1 of Metobs API.
    """

    def __init__(
        self,
        data: list = None,
        version: Union[str, int] = "1.0",
        data_type: str = "json",
    ):
        """
        Get parameters from version.

        Args:
            data: available API versions
            version: selected API version
            data_type: data_type of request

        Raises:
            TypeError
            NotImplementedError
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
    """
    Get stations from parameters for version 1 of Metobs API.
    """

    def __init__(
        self,
        data: list,
        parameters: str = None,
        parameters_title: str = None,
        data_type: str = "json",
    ):
        """
        Get stations from parameters.

        Args:
            data: available API parameters
            parameters: data to read
            parameters_title: exact title of data
            data_type: data_type of request

        Raises:
            TypeError
            NotImplementedError
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if parameters is None and parameters_title is None:
            raise NotImplementedError("No parameters selected.")

        if parameters and parameters_title:
            raise NotImplementedError("Can't decide which input to select.")

        if parameters:
            self.selected_parameters = parameters
            url = self._get_url(data, "key", parameters, data_type)
        if parameters_title:
            self.selected_parameters = parameters_title
            url = self._get_url(data, "title", parameters_title, data_type)

        content = self._get_and_parse_request(url)
        self.valuetype = content["valueType"]
        self.stationset = content["stationSet"]
        self.stations = sorted(content["station"], key=lambda x: int(x["id"]))
        self.data = tuple((x["id"], x["name"]) for i, x in enumerate(self.stations))


class MetobsPeriodsV1(MetobsLevelV1):
    """
    Get periods from stations for version 1 of Metobs API.
    Note that stationset_title is not supported
    """

    def __init__(
        self,
        data: list,
        stations: int = None,
        station_name: str = None,
        stationset: str = None,
        data_type: str = "json",
    ):
        """
        Get periods from stations.

        Args:
            data: available API stations
            stations: stations key to get
            station_name: stations name to get
            stationset: stations set to get
            data_type: data_type of request

        Raises:
            TypeError
            NotImplementedError
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if [stations, station_name, stationset].count(None) == 3:
            raise NotImplementedError("No stations selected.")

        if [bool(x) for x in [stations, station_name, stationset]].count(True) > 1:
            raise NotImplementedError("Can't decide which input to select.")

        if stations:
            self.selected_station = stations
            url = self._get_url(data, "key", stations, data_type)
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
    """
    Get data from periods for version 1 of Metobs API.
    """

    def __init__(
        self,
        data: list,
        periods: str = "corrected-archive",
        data_type: str = "json",
    ):
        """
        Get data from periods.

        Args:
            data: available API periods
            periods: select periods from:
                    latest-hour, latest-day, latest-months or corrected-archive
            data_type: data_type of request

        Raises:
            TypeError
            NotImplementedError
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if periods not in METOBS_AVAILABLE_PERIODS:
            raise NotImplementedError(
                "Select a supported periods: }"
                + ", ".join([p for p in METOBS_AVAILABLE_PERIODS])
            )

        self.selected_period = periods
        url = self._get_url(data, "key", periods, data_type)
        content = self._get_and_parse_request(url)
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.data = content["data"]

    def get(self, type: str = "text/plain"):
        """
        Get the selected data file.

        Args:
            type: type of request

        Returns:
            utf-8 decoded response
        """
        for item in self.data:
            for link in item["link"]:
                if link["type"] != type:
                    continue

                response = requests.get(link["href"])
                return response.content.decode("utf-8")
