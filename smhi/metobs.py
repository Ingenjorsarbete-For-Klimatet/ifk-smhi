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
        Initialise the SMHI MetObs class with a data type format used to get data.
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

    def get_parameters(self, version: Union[str, int] = "1.0"):
        """
        Get SMHI MetObs API parameters from version. Only supports `version = 1.0`.

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

    def get_stations(self, parameter: str = None, parameter_title: str = None):
        """
        Get SMHI MetObs API (version 1) stations from given parameter.

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

    def get_periods(self, station: str = None, stationset: str = None):
        """
        Get SMHI MetObs API (version 1) periods from given station.

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

    def get_data(self, period: str = "corrected-archive"):
        """
        Get SMHI MetObs API (version 1) data from given period.

        Args:
            period: period
        """
        self.data = MetObsDataV1(self.period.period, period)
        self.table_raw = self.data.get()
        self.table = pd.read_csv(io.StringIO(self.table_raw), on_bad_lines="skip")

    def get_data_from_selection(
        self,
        parameter: int,
        station: int,
        period: str,
    ):
        """
        Get data from explicit parameter selection and station,
        without inspecting each level. Note, no version parameter.

        Args:
            parameter: API parameter
            station: station
            period: period to download
        """
        self.get_parameters()
        self.get_stations(parameter)
        self.get_periods(station)
        self.get_data(period)

    def get_data_stationset(
        self,
        parameter: int,
        stationset: int,
        period: str,
    ):
        """
        Get data from explicit parameter selection and station set,
        without inspecting each level. Note, no version parameter.

        Args:
            parameter: API parameter
            stationset: station
            period: period to download
        """
        self.get_parameters()
        self.get_stations(parameter)
        self.get_periods(None, stationset)
        self.get_data(period)

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
        parameter: Union[str, int],
        data_type: str = "json",
    ):
        """
        Get the url to get data from. Defaults to type json.

        Args:
            data: data list
            key: key to look in
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
            raise IndexError("Can't find data for parameter: {p}".format(p=parameter))
        except KeyError:
            raise KeyError("Can't find key: {key}".format(key=key))


class MetObsParameterV1(MetObsLevelV1):
    """
    Get parameter for version 1 of MetObs API.
    """

    def __init__(
        self,
        data: list = None,
        version: Union[str, int] = "1.0",
        data_type: str = "json",
    ):
        """
        Get parameter from version.

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


class MetObsStationV1(MetObsLevelV1):
    """
    Get stations from parameter for version 1 of MetObs API.
    """

    def __init__(
        self,
        data: list,
        parameter: str = None,
        parameter_title: str = None,
        data_type: str = "json",
    ):
        """
        Get stations from parameter.

        Args:
            data: available API parameters
            parameter: data to read
            parameter_title: exact title of data
            data_type: data_type of request

        Raises:
            TypeError
            NotImplementedError
        """
        super().__init__()

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
        self.station = sorted(content["station"], key=lambda x: int(x["id"]))
        self.data = tuple((x["id"], x["name"]) for i, x in enumerate(self.station))


class MetObsPeriodV1(MetObsLevelV1):
    """
    Get periods from station for version 1 of MetObs API.
    Note that stationset_title is not supported
    """

    def __init__(
        self,
        data: list,
        station: int = None,
        station_name: str = None,
        stationset: str = None,
        data_type: str = "json",
    ):
        """
        Get periods from station.

        Args:
            data: available API stations
            station: station key to get
            station_name: station name to get
            stationset: station set to get
            data_type: data_type of request

        Raises:
            TypeError
            NotImplementedError
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if [station, station_name, stationset].count(None) == 3:
            raise NotImplementedError("No station selected.")

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
        self.period = sorted(content["period"], key=lambda x: x["key"])
        self.data = [x["key"] for x in self.period]


class MetObsDataV1(MetObsLevelV1):
    """
    Get data from period for version 1 of MetObs API.
    """

    def __init__(
        self,
        data: list,
        period: str = "corrected-archive",
        data_type: str = "json",
    ):
        """
        Get data from period.

        Args:
            data: available API periods
            period: select period from:
                    latest-hour, latest-day, latest-months or corrected-archive
            data_type: data_type of request

        Raises:
            TypeError
            NotImplementedError
        """
        super().__init__()

        if data_type != "json":
            raise TypeError("Only json supported.")

        if period not in METOBS_AVAILABLE_PERIODS:
            raise NotImplementedError(
                "Select a supported period: }"
                + ", ".join([p for p in METOBS_AVAILABLE_PERIODS])
            )

        self.selected_period = period
        url = self._get_url(data, "key", period, data_type)
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
