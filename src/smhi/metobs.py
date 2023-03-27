"""SMHI Metobs client."""
import io
import json
import logging
import requests
import pandas as pd
from typing import Union, Optional, Any, Dict
from requests.structures import CaseInsensitiveDict
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
        self.version: Optional[Union[str, int]] = None
        self.versions = Versions()
        self.parameters: Optional[Parameters] = None
        self.stations: Optional[Stations] = None
        self.periods: Optional[Periods] = None
        self.data: Optional[Data] = None

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
        self.parameters = Parameters(self.versions)

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
            self.stations = Stations(self.parameters, parameter=parameter)
        else:
            self.stations = Stations(self.parameters, parameter_title=parameter_title)

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
            self.periods = Periods(self.stations, station)
        else:
            self.periods = Periods(self.stations, stationset=stationset)

    def get_data(
        self, period: str = "corrected-archive"
    ) -> tuple[Optional[pd.DataFrame], Optional[tuple[dict]]]:
        """Get SMHI Metobs API (version 1) data from given period.

        Args:
            period: period

        Returns:
            data table
            data header dict
        """
        if self.periods is None:
            logging.info("No periods found, call get_periods first.")
            return None, None

        self.data = Data(self.periods, period)

        return self.data.data, self.data.data_header

    def get_data_from_selection(
        self,
        parameter: int,
        station: int,
        period: str,
    ) -> tuple[Optional[pd.DataFrame], Optional[tuple[dict]]]:
        """Get data from explicit parameters.

        Get data from explicit parameter, station and period,
        without inspecting each level. Note, no version parameters.

        Args:
            parameter: parameter to get
            station: station to get
            period: period to get

        Returns:
            data table
            data header dict
        """
        self.get_parameters()
        self.get_stations(parameter)
        self.get_periods(station)
        data, data_header = self.get_data(period)
        return data, data_header

    def get_data_stationset(
        self,
        parameter: int,
        stationset: str,
        period: str,
    ) -> tuple[Optional[pd.DataFrame], Optional[tuple[dict]]]:
        """Get data from stationset.

        Get data from explicit parameters, stations set and period,
        without inspecting each level. Note, no version parameters.

        Args:
            parameter: parameter to get
            stationset: stationset to get
            period: period to get

        Returns:
            data table
        """
        self.get_parameters()
        self.get_stations(parameter)
        self.get_periods(None, stationset)
        data, data_header = self.get_data(period)
        return data, data_header

    def inspect(self, num_print: int = 10) -> None:
        """Inspect object state.

        Args:
            num_print: number of items to print
        """
        print("API version")
        print("Available versions: ", [x["key"] for x in self.versions.data])
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


class BaseLevel:
    """Base Metobs level version 1 class."""

    def __init__(self) -> None:
        """Initialise base class."""
        self.headers: Optional[CaseInsensitiveDict] = None
        self.key: Optional[str] = None
        self.updated: Optional[str] = None
        self.title: Optional[str] = None
        self.summary: Optional[str] = None
        self.link: Optional[str] = None
        self.data_type: Optional[str] = None
        self.raw_data_header: Optional[str] = None
        self.data_header: Any = None
        self.raw_data: Any = None
        self.data: Any = None

    @property
    def show(self) -> Any:
        """Show property."""
        return self.data

    def _get_and_parse_request(self, url: str) -> Dict[Any, Any]:
        """Get and parse API request. Only JSON supported.

        Args:
            url: url to get from

        Returns:
            jsonified content
        """
        response = requests.get(url, timeout=200)
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
        self.data_type = TYPE_MAP[data_type]
        try:
            requested_data = [x for x in data if x[key] == str(parameter)][0]["link"]
            url = [x["href"] for x in requested_data if x["type"] == self.data_type][0]
            return url
        except IndexError:
            raise IndexError("Can't find data for parameters: {p}".format(p=parameter))
        except KeyError:
            raise KeyError("Can't find key: {key}".format(key=key))


class Versions(BaseLevel):
    """Get versions of Metobs API."""

    def __init__(
        self,
        data_type: str = "json",
    ) -> None:
        """Get versions.

        For now, only supports `json` and version 1.

        Args:
            data_type: data_type of request

        Raises:
            TypeError: data_type not supported
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        content = self._get_and_parse_request(METOBS_URL)
        self.data = tuple(content["version"])


class Parameters(BaseLevel):
    """Get parameters for version 1 of Metobs API."""

    def __init__(
        self,
        versions_object: Optional[Versions] = None,
        version: Union[str, int] = "1.0",
        data_type: str = "json",
    ) -> None:
        """Get parameters from version.

        Args:
            versions_object: versions object
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

        if versions_object is None:
            versions_object = Versions()

        self.versions_object = versions_object
        self.selected_version = "1.0" if version == 1 else version
        url = self._get_url(versions_object.data, "key", version, data_type)
        content = self._get_and_parse_request(url)
        self.resource = sorted(content["resource"], key=lambda x: int(x["key"]))
        self.data = tuple((x["key"], x["title"], x["summary"]) for x in self.resource)


class Stations(BaseLevel):
    """Get stations from parameter for version 1 of Metobs API."""

    def __init__(
        self,
        parameters_in_version: Parameters,
        parameter: Optional[int] = None,
        parameter_title: Optional[str] = None,
        data_type: str = "json",
    ) -> None:
        """Get stations from parameters.

        Args:
            parameters_in_version: parameters object
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

        self.parameters_in_version = parameters_in_version
        if parameter:
            self.selected_parameter = parameter
            url = self._get_url(
                parameters_in_version.resource, "key", parameter, data_type
            )
        if parameter_title:
            self.selected_parameter = parameter_title
            url = self._get_url(
                parameters_in_version.resource, "title", parameter_title, data_type
            )

        content = self._get_and_parse_request(url)
        self.valuetype = content["valueType"]
        self.stationset = content["stationSet"]
        self.stations = sorted(content["station"], key=lambda x: int(x["id"]))
        self.data = tuple((x["id"], x["name"]) for i, x in enumerate(self.stations))


class Periods(BaseLevel):
    """Get periods from station for version 1 of Metobs API.

    Note that stationset_title is not supported
    """

    def __init__(
        self,
        stations_in_parameter: Stations,
        station: Optional[int] = None,
        station_name: Optional[str] = None,
        stationset: Optional[str] = None,
        data_type: str = "json",
    ) -> None:
        """Get periods from station.

        Args:
            stations_in_parameter: stations object
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

        self.stations_in_parameter = stations_in_parameter
        if station:
            self.selected_station = station
            url = self._get_url(
                stations_in_parameter.stations, "key", station, data_type
            )
        if station_name:
            self.selected_station = station_name
            url = self._get_url(
                stations_in_parameter.stations, "title", station_name, data_type
            )
        if stationset:
            self.selected_station = stationset
            url = self._get_url(
                stations_in_parameter.stations, "key", stationset, data_type
            )

        content = self._get_and_parse_request(url)
        self.owner = content["owner"]
        self.ownercategory = content["ownerCategory"]
        self.measuringstations = content["measuringStations"]
        self.active = content["active"]
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.position = content["position"]
        self.periods = sorted(content["period"], key=lambda x: x["key"])
        self.data = tuple(x["key"] for x in self.periods)


class Data(BaseLevel):
    """Get data from period for version 1 of Metobs API."""

    def __init__(
        self,
        periods_in_station: Periods,
        period: str = "corrected-archive",
        data_type: str = "json",
    ) -> None:
        """Get data from period.

        Args:
            periods_in_station: periods object
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

        self.periods_in_station = periods_in_station
        self.selected_period = period
        url = self._get_url(periods_in_station.periods, "key", period, data_type)
        content = self._get_and_parse_request(url)
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.raw_data = content["data"]
        self._get_data()

    def _get_data(self, type: str = "text/plain") -> None:
        """Get the selected data file.

        Args:
            type: type of request
        """
        for item in self.raw_data:
            for link in item["link"]:
                if link["type"] != type:
                    continue

                content = requests.get(link["href"]).content.decode("utf-8")
                raw_data_header, raw_data = self._separate_header_data(content)
                self._parse_header(raw_data_header)
                self._parse_data(raw_data)
                return

    def _separate_header_data(self, content: str) -> tuple:
        """Separate header and data into two strings.

        Args:
            content: raw data string
        """
        data_starting_point = content.find("Datum")
        self.raw_data_header = content[:data_starting_point]
        self.raw_data = content[data_starting_point:-1]

        return self.raw_data_header, self.raw_data

    def _parse_header(self, raw_data_header: str) -> None:
        """Parse header string.

        Args:
            raw_data_header: raw data header as a string
        """
        data_headers = []
        for header in raw_data_header.split("\n\n")[:-1]:
            try:
                data_headers.append(
                    pd.read_csv(
                        io.StringIO(header),
                        sep=";",
                        on_bad_lines="skip",
                    ).to_dict("records")[0]
                )
            except pd.errors.EmptyDataError:
                logging.warning("No columns to parse.")

        self.data_header = {k: v for d in data_headers for k, v in d.items()}

    def _parse_data(self, raw_data: str) -> None:
        """Parse string data.

        Args:
            raw_data: utf-8 decoded response

        Raises:
            NotImplementedError
        """
        self.data = pd.read_csv(
            io.StringIO(raw_data),
            sep=";",
            on_bad_lines="skip",
            usecols=[0, 1, 2],
        )

        try:
            self.data.set_index(
                pd.to_datetime(self.data["Datum"] + " " + self.data["Tid (UTC)"]),
                inplace=True,
            )
            self.data.drop(["Datum", "Tid (UTC)"], axis=1, inplace=True)
        except TypeError:
            raise TypeError("Can't parse date of empty data.")
