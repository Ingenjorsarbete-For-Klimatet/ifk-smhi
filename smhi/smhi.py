"""
Read SMHI data.
"""
import json
import math
import requests
from typing import Union
from geopy import distance
from collections import defaultdict


BASE_URL = "https://opendata-download-metobs.smhi.se/api.json"
TYPE_MAP = defaultdict(lambda: "application/json", json="application/json")


class SMHIClient:
    """
    SMHI data class.
    """

    def __init__(self, type: str = "json"):
        """
        Initialise the class with a data type format.

        Args:
            type: type of request
        """
        self.type = TYPE_MAP[type]
        response = requests.get(BASE_URL)
        self.headers = response.headers
        self.content = json.loads(response.content)
        self.available_versions = self.content["version"]

        self.version = None
        self.parameter = None
        self.station = None
        self.period = None
        self.data = None
        self.table = None

    def fetch_parameters(self, version: Union[str, int] = "latest"):
        """
        Fetch SMHI API parameters from version.

        Args:
            version: selected API version
        """
        self.version = version
        self.parameter = SMHIParameter(self.type, self.available_versions, version)

    def fetch_stations(self, parameter: str = None, parameter_title: str = None):
        """
        Fetch SMHI API stations from given parameter.

        Args:
            parameter: id of data
            parameter_title: exact title of data
        """
        if parameter is None and parameter_title is None:
            raise Exception("Both arguments None.")

        if self.parameter is None:
            raise Exception("Fetch parameters first.")

        if parameter_title is None:
            self.station = SMHIStation(
                self.type, self.parameter.resource, parameter=parameter
            )

        if parameter is None:
            self.station = SMHIStation(
                self.type, self.parameter.resource, parameter_title=parameter_title
            )

    def fetch_periods(self, station: str = None, station_set: str = None):
        """
        Fetch SMHI API periods from given station.

        Args:
            station: id of data
            station_set: exact title of data
        """
        if station is None and station_set is None:
            raise Exception("Both arguments None.")

        if self.station is None:
            raise Exception("Fetch stations first.")

        if station_set is None:
            self.period = SMHIPeriod(self.type, self.station.station, station=station)

        if station is None:
            self.period = SMHIPeriod(
                self.type, self.station.station, station_set=station_set
            )

    def fetch_data(self, period: str = "corrected-archive"):
        """
        Fetch SMHI API data from given period.

        Args:
            period: period
        """
        self.data = SMHIData(self.type, self.period.period, period)
        self.table = self.data.fetch()

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

        if self.parameter is not None:
            print("API parameter")
            print("Available parameters ({0} first): ".format(num_print))
            print(self.parameter.data[:num_print])
            print(
                "See all ({0}) parameters with ´client.parameter.data".format(
                    len(self.parameter.data)
                )
            )
            if self.station is not None:
                print("Selected parameter: ", self.station.selected_parameter)
            print()

        if self.station is not None:
            print("API station")
            print("Available stations ({0} first): ".format(num_print))
            print(self.station.data[:num_print])
            print(
                "See all ({0}) stations with ´client.station.data".format(
                    len(self.station.data)
                )
            )
            if self.period is not None:
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

        if self.period is not None:
            print("API period")
            print("Available periods: ")
            print(self.period.data)
            if self.data is not None:
                print("Selected period: ", self.data.selected_period)
            print()

    def get_explicit_data(
        self,
        version: str,
        parameter: int,
        station: int,
        station_set: str,
        select_period: str,
    ):
        """
        Get data from explicit selection.

        Args:
            version: API version
            parameter: API parameter
            station: station
            station_set: station_set
            select_period: period to download
        """
        pass


class SMHIParameter:
    """
    Fetch parameter for given version.
    """

    def __init__(
        self,
        type: str = "application/json",
        data: list = None,
        version: Union[str, int] = "latest",
    ):
        """
        Fetch parameter from version.

        Args:
            type: type of request
            data: available API versions
            version: selected API version
        """
        self.selected_version = version
        requested_version = [x for x in data if x["key"] == version][0]
        url = [x["href"] for x in requested_version["link"] if x["type"] == type][0]
        response = requests.get(url)
        content = json.loads(response.content)

        self.headers = response.headers
        self.key = content["key"]
        self.updated = content["updated"]
        self.title = content["title"]
        self.summary = content["summary"]
        self.link = content["link"]
        self.resource = sorted(content["resource"], key=lambda x: int(x["key"]))
        self.data = tuple((x["key"], x["title"]) for x in self.resource)


class SMHIStation:
    """
    Fetch stations from parameter.
    """

    def __init__(
        self,
        type: str = "application/json",
        data: list = None,
        parameter: str = None,
        parameter_title: str = None,
    ):
        """
        Fetch stations from parameter.

        Args:
            type: type of request
            data: available API parameters
            parameter: data to read
            parameter_title: exact title of data
        """
        self.selected_parameter = parameter
        if parameter_title is not None:
            requested_parameter = [x for x in data if x["title"] == parameter_title][0]
        else:
            requested_parameter = [x for x in data if x["key"] == str(parameter)][0]
        url = [x["href"] for x in requested_parameter["link"] if x["type"] == type][0]
        response = requests.get(url)
        content = json.loads(response.content)

        self.headers = response.headers
        self.key = content["key"]
        self.updated = content["updated"]
        self.title = content["title"]
        self.summary = content["summary"]
        self.valuetype = content["valueType"]
        self.link = content["link"]
        self.stationset = content["stationSet"]
        self.station = sorted(content["station"], key=lambda x: int(x["id"]))
        self.data = tuple((i, x["id"], x["name"]) for i, x in enumerate(self.station))


class SMHIPeriod:
    """
    Fetch periods from station.
    """

    def __init__(
        self,
        type: str = "application/json",
        data: list = None,
        station: int = None,
        station_name: str = None,
    ):
        """
        Fetch periods from station.

        Args:
            type: type of request
            data: available API stations
            station: station id, not key
            station_name: station name
        """
        self.selected_station = station
        if station_name is not None:
            requested_station = [x for x in data if x["title"] == station_name][0]
        else:
            requested_station = [x for x in data if x["id"] == station][0]
        url = [x["href"] for x in requested_station["link"] if x["type"] == type][0]
        response = requests.get(url)
        content = json.loads(response.content)

        self.headers = response.headers
        self.key = content["key"]
        self.updated = content["updated"]
        self.title = content["title"]
        self.owner = content["owner"]
        self.ownercategory = content["ownerCategory"]
        self.measuringstations = content["measuringStations"]
        self.active = content["active"]
        self.summary = content["summary"]
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.position = content["position"]
        self.link = content["link"]
        self.period = sorted(content["period"], key=lambda x: x["key"])
        self.data = [x["key"] for x in self.period]


class SMHIData:
    """
    Fetch data from period.
    """

    def __init__(
        self,
        type: str = "application/json",
        data: list = None,
        period: str = "corrected-archive",
    ):
        """
        Fetch data from period.

        Args:
            type: type of request
            data: available API periods
            period: select period from: latest-hour, latest-day, latest-months or corrected-archive
        """
        self.selected_period = period
        requested_period = [x for x in data if x["key"] == period][0]
        url = [x["href"] for x in requested_period["link"] if x["type"] == type][0]
        response = requests.get(url)
        content = json.loads(response.content)

        self.headers = response.headers

        self.key = content["key"]
        self.updated = content["updated"]
        self.title = content["title"]
        self.summary = content["summary"]
        self.time_from = content["from"]
        self.time_to = content["to"]
        self.link = content["link"]
        self.data = content["data"]

    def fetch(self, type: str = "text/plain"):
        """
        Fetch the selected data file.

        Args:
            type: type of request
        """
        for item in self.data:
            print(item)
            for link in item["link"]:
                print(link)
                if link["type"] != type:
                    continue

                response = requests.get(link["href"])
                return response.content


class SMHI:
    """
    SMHI class with high-level functions.
    """

    def __init__(self, type: str = "json", version: Union[str, int] = "latest"):
        self.type = TYPE_MAP[type]
        self.client = SMHIClient(type)
        self.client.fetch_parameters(version)

    @property
    def parameters(self):
        return self.client.parameter.data

    def get_stations(self, parameter: str = None):
        self.client.fetch_stations(parameter)
        return self.client.station.data

    def get_stations_from_title(self, parameter: str = None):
        self.client.fetch_stations(None, parameter)
        return self.client.station.data

    def find_stations_from_gps(
        self, parameter: int, dist: float, latitude: float, longitude: float
    ):
        user_position = (latitude, longitude)
        self.get_stations(parameter)
        self.d = []

        for station in self.client.station.station:
            station_position = (station["latitude"], station["longitude"])
            station_distance = distance.distance(user_position, station_position)

            if station_distance <= dist:
                self.d.append(distance.distance(user_position, station_position))
