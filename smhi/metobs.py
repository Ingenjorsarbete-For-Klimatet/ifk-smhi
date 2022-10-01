"""
SMHI Meteorological Observations client.
"""
import io
import json
import requests
import pandas as pd
from typing import Union
from smhi.constants import METOBS_URL, TYPE_MAP, METOBS_AVAILABLE_PERIODS


class MetObs:
    """
    SMHI data class.
    """

    def __init__(self, data_type: str = "json"):
        """
        Initialise the SMHI MetObs class with a data type format used to fetch data.
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
        self.parameter = None
        self.station = None
        self.period = None
        self.data = None
        self.table_raw = None
        self.table = None

    def fetch_parameters(self, version: Union[str, int] = "1.0"):
        """
        Fetch SMHI MetObs API parameters from version. Only supports `version = 1.0`.

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
        self.parameter = MetObsParameterV1(self.available_versions)

    def fetch_stations(self, parameter: str = None, parameter_title: str = None):
        """
        Fetch SMHI MetObs API (version 1) stations from given parameter.

        Args:
            parameter: id of data
            parameter_title: exact title of data
        """
        if parameter is None and parameter_title is None:
            raise NotImplementedError("Both arguments None.")

        if parameter:
            self.station = MetObsStationV1(self.parameter.resource, parameter=parameter)
        else:
            self.station = MetObsStationV1(
                self.parameter.resource, parameter_title=parameter_title
            )

    def fetch_periods(self, station: str = None, stationset: str = None):
        """
        Fetch SMHI MetObs API (version 1) periods from given station.

        Args:
            station: id of data
            stationset: exact title of data
        """
        if station is None and stationset is None:
            raise NotImplementedError("Both arguments None.")

        if station:
            self.period = MetObsPeriodV1(self.station.station, station)
        else:
            self.period = MetObsPeriodV1(self.station.station, stationset=stationset)

    def fetch_data(self, period: str = "corrected-archive"):
        """
        Fetch SMHI MetObs API (version 1) data from given period.

        Args:
            period: period
        """
        self.data = MetObsDataV1(self.period.period, period)
        self.table_raw = self.data.fetch()
        self.table = pd.read_csv(io.StringIO(self.table_raw), on_bad_lines="skip")

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

        if self.parameter:
            print("API parameter")
            print("Available parameters ({0} first): ".format(num_print))
            print(self.parameter.data[:num_print])
            print(
                "See all ({0}) parameters with ´client.parameter.data".format(
                    len(self.parameter.data)
                )
            )
            if self.station:
                print("Selected parameter: ", self.station.selected_parameter)
            print()

        if self.station:
            print("API station")
            print("Available stations ({0} first): ".format(num_print))
            print(self.station.data[:num_print])
            print(
                "See all ({0}) stations with ´client.station.data".format(
                    len(self.station.data)
                )
            )
            if self.period:
                print(
                    "Selected station: {0} {1}".format(
                        self.period.selected_station,
                        [
                            x[2]
                            for x in self.station.data
                            if x[1] == self.period.selected_station
                        ][0],
                    )
                )
            print()

        if self.period:
            print("API period")
            print("Available periods: ")
            print(self.period.data)
            if self.data:
                print("Selected period: ", self.data.selected_period)
            print()

    def get_data(
        self,
        parameter: int,
        station: int,
        period: str,
    ):
        """
        Get data from explicit parameter selection and station, without inspecting each level.
        Note, no version parameter.

        Args:
            parameter: API parameter
            station: station
            period: period to download
        """
        self.fetch_parameters()
        self.fetch_stations(parameter)
        self.fetch_periods(station)
        self.fetch_data(period)

    def get_data_stationset(
        self,
        parameter: int,
        stationset: int,
        period: str,
    ):
        """
        Get data from explicit parameter selection and station set, without inspecting each level.
        Note, no version parameter.

        Args:
            parameter: API parameter
            stationset: station
            period: period to download
        """
        self.fetch_parameters()
        self.fetch_stations(parameter)
        self.fetch_periods(None, stationset)
        self.fetch_data(period)


class MetObsLevelV1:
    """
    Base MetObs level version 1 class.
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

    def _fetch_and_parse_request(
        self, data: list, data_type: str, p1: str, p2: str = None, p3: str = None
    ):
        """
        Fetch and parse API request. Only JSON supported.

        Args:
            data: list of data to fetch from
            data_type: type of data to fetch
            p1: parameter 1
            p2: parameter 2
            p3: parameter 3

        Returns:
            jsonified content
        """
        p1 = p3 if p3 else p1
        if p2:
            requested_data = [x for x in data if x["title"] == p2][0]
        else:
            requested_data = [x for x in data if x["key"] == str(p1)][0]
        url = [x["href"] for x in requested_data["link"] if x["type"] == data_type][0]

        response = requests.get(url)
        content = json.loads(response.content)

        self.headers = response.headers
        self.key = content["key"]
        self.updated = content["updated"]
        self.title = content["title"]
        self.summary = content["summary"]
        self.link = content["link"]

        return content


class MetObsParameterV1(MetObsLevelV1):
    """
    Fetch parameter for version 1 of MetObs API.
    """

    def __init__(
        self,
        data: list = None,
        version: Union[str, int] = "1.0",
        data_type: str = "application/json",
    ):
        """
        Fetch parameter from version.

        Args:
            data: available API versions
            version: selected API version
            data_type: data_type of request
        """
        super().__init__()

        if version != 1 and version != "1.0":
            raise NotImplementedError("Only supports version 1.0.")

        if data_type != TYPE_MAP["json"]:
            raise TypeError("Only json supported.")

        self.selected_version = "1.0" if version == 1 else version
        content = self._fetch_and_parse_request(data, data_type, version)
        self.resource = sorted(content["resource"], key=lambda x: int(x["key"]))
        self.data = tuple((x["key"], x["title"]) for x in self.resource)


class MetObsStationV1(MetObsLevelV1):
    """
    Fetch stations from parameter for version 1 of MetObs API.
    """

    def __init__(
        self,
        data: list,
        parameter: str = None,
        parameter_title: str = None,
        data_type: str = "application/json",
    ):
        """
        Fetch stations from parameter.

        Args:
            data: available API parameters
            parameter: data to read
            parameter_title: exact title of data
            data_type: data_type of request
        """
        super().__init__()

        if data_type != TYPE_MAP["json"]:
            raise TypeError("Only json supported.")

        if parameter is None and parameter_title is None:
            raise NotImplementedError("No parameter selected.")

        if parameter and parameter_title:
            raise NotImplementedError("Can't decide which input to select.")

        self.selected_parameter = (
            parameter if parameter_title is None else parameter_title
        )
        content = self._fetch_and_parse_request(
            data, data_type, parameter, parameter_title
        )
        self.valuetype = content["valueType"]
        self.stationset = content["stationSet"]
        self.station = sorted(content["station"], key=lambda x: int(x["id"]))
        self.data = tuple((i, x["id"], x["name"]) for i, x in enumerate(self.station))


class MetObsPeriodV1(MetObsLevelV1):
    """
    Fetch periods from station for version 1 of MetObs API.
    Note that stationset_title is not supported
    """

    def __init__(
        self,
        data: list,
        station: int = None,
        station_name: str = None,
        stationset: str = None,
        data_type: str = "application/json",
    ):
        """
        Fetch periods from station.

        Args:
            data: available API stations
            station: station key to fetch
            station_name: station name to fetch
            stationset: station set to fetch
            data_type: data_type of request
        """
        super().__init__()

        if data_type != TYPE_MAP["json"]:
            raise TypeError("Only json supported.")

        if station is None and station_name is None and stationset is None:
            raise NotImplementedError("No station selected.")

        if [bool(x) for x in [station, station_name, stationset]].count(True) > 1:
            raise NotImplementedError("Can't decide which input to select.")

        selected_station = station_name if station_name else stationset
        self.selected_station = station if station else selected_station
        content = self._fetch_and_parse_request(
            data, data_type, station, station_name, stationset
        )
        self.owner = content["owner"]
        self.ownercategory = content["ownerCategory"]
        self.measuringstations = content["measuringStations"]
        self.active = content["active"]
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.position = content["position"]
        self.period = sorted(content["period"], key=lambda x: x["key"])
        self.data = [x["key"] for x in self.period]


class MetObsDataV1(MetObsLevelV1):
    """
    Fetch data from period for version 1 of MetObs API.
    """

    def __init__(
        self,
        data: list,
        period: str = "corrected-archive",
        data_type: str = "application/json",
    ):
        """
        Fetch data from period.

        Args:
            data: available API periods
            period: select period from: latest-hour, latest-day, latest-months or corrected-archive
            data_type: data_type of request
        """
        super().__init__()

        if data_type != TYPE_MAP["json"]:
            raise TypeError("Only json supported.")

        if period not in METOBS_AVAILABLE_PERIODS:
            raise NotImplementedError(
                "Select a supported period: }"
                + ", ".join([p for p in METOBS_AVAILABLE_PERIODS])
            )

        self.selected_period = period
        content = self._fetch_and_parse_request(data, data_type, period)
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.data = content["data"]

    def fetch(self, type: str = "text/plain"):
        """
        Fetch the selected data file.

        Args:
            type: type of request
        """
        for item in self.data:
            for link in item["link"]:
                if link["type"] != type:
                    continue

                response = requests.get(link["href"])
                return response.content.decode("utf-8")
