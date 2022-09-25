"""
Read SMHI data.
"""
import json
import requests
from typing import Union
from collections import defaultdict


TYPE_MAP = defaultdict(lambda: "application/json", json="application/json")


class SMHI:
    """
    SMHI data class.
    """

    def __init__(self, type: str = "json"):
        """
        Initialise the class with a data type format.

        Args:
            type: type of data to fetch
        """
        self.type = TYPE_MAP[type]
        self.base_url = "https://opendata-download-metobs.smhi.se/api.json"

        response = requests.get(self.base_url)
        self.base = json.loads(response.content)
        self.versions = [x["key"] for x in self.base["version"]]

        self.selected_version = None
        self.selected_parameter = None
        self.selected_station_set = None
        self.selected_station = None
        self.selected_period = None
        self.selected_data_url = None
        self.selected_data = None

    def inspect(self, num_print: int = 10):
        """
        Inspect object state.

        Args:
            num_print: number of items to print
        """
        print("API base")
        print(self.base)
        print()

        print("API version")
        print("Available versions: ", self.versions)
        print("Selected version: ", self.selected_version)
        print()

        print("API parameter")
        print("Available parameters ({0} first): ".format(num_print))
        print(self.parameters_key[:num_print])
        print("See all parameters with ´client.parameters_key´")
        print("Selected parameter: ", self.selected_parameter)
        print()

        print("API station")
        print("Available stations ({0} first): ".format(num_print))
        print(self.stations_key[:num_print])
        print("See all stations with ´client.stations_key")
        print(
            "Selected station: {0} {1}".format(
                self.selected_station,
                [x[2] for x in self.stations_key if x[1] == self.selected_station][0],
            )
        )
        print()

        print("API period")
        print("Available periods: ")
        print(self.periods_key)
        print("Selected period: ", self.selected_period)
        print()

    def select_version(self, version: Union[str, int] = "latest"):
        """
        Select version of SMHI API to read.

        Args:
            version: selected API version
        """
        self.selected_version = version
        requested_version = [x for x in self.base["version"] if x["key"] == version][0]
        url = [x["href"] for x in requested_version["link"] if x["type"] == self.type][
            0
        ]

        response = requests.get(url)
        self.parameters = sorted(
            json.loads(response.content)["resource"], key=lambda x: x["key"]
        )
        self.parameters_key = tuple((x["key"], x["title"]) for x in self.parameters)

    def select_parameter(self, parameter: str, parameter_title: str = None):
        """
        Select the data to read, also called parameter.

        Args:
            parameter: data to read
            parameter_title: exact title of data
        """
        self.selected_parameter = parameter
        if parameter_title is not None:
            requested_parameter = [
                x for x in self.parameters if x["title"] == parameter_title
            ][0]
        else:
            requested_parameter = [
                x for x in self.parameters if x["key"] == str(parameter)
            ][0]
        url = [
            x["href"] for x in requested_parameter["link"] if x["type"] == self.type
        ][0]

        response = requests.get(url)
        response_content = json.loads(response.content)
        self.station_sets = response_content["stationSet"]
        self.stations = sorted(response_content["station"], key=lambda x: x["id"])

        self.stations_key = tuple(
            (i, x["id"], x["name"]) for i, x in enumerate(self.stations)
        )

    def select_station(self, station: int, station_name: str = None):
        """
        Selection station.

        Args:
            station: station id, not key
            station_name: station name
        """
        self.selected_station = station
        if self.stations is None:
            raise Exception("Station is empty, try station set.")

        if station_name is not None:
            requested_station = [
                x for x in self.stations if x["title"] == station_name
            ][0]
        else:
            requested_station = [x for x in self.stations if x["id"] == station][0]
        url = [x["href"] for x in requested_station["link"] if x["type"] == self.type][
            0
        ]

        response = requests.get(url)
        self.periods = sorted(
            json.loads(response.content)["period"], key=lambda x: x["key"]
        )

        self.periods_key = [x["key"] for x in self.periods]

    def select_station_set(self, station_set: int):
        if self.station_set is None:
            raise Exception("Station set is empty, try station.")

    def select_period(self, period: str = "corrected-archive"):
        """
        Select period of data.

        Args:
            period: select period from: latest-hour, latest-day, latest-months or corrected-archive
        """
        self.selected_period = period
        requested_period = [x for x in self.periods if x["key"] == period][0]
        url = [x["href"] for x in requested_period["link"] if x["type"] == self.type][0]

        response = requests.get(url)
        self.data_urls = json.loads(response.content)["data"]

    def get_data(self, data_type: str = "text/plain"):
        """
        Get the selected data

        Args:
            data_type:
        """
        self.data = []
        for x in self.data_urls:
            for y in x["link"]:
                if type(y) is not list:
                    y = [y]

                url = [z for z in y if z["type"] == data_type][0]["href"]
                self.data.append(requests.get(url).content)

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

    def find_from_coordinates(self, radius: int = 1):
        """
        Find all data near coordinates.

        Args:
            radius: radius from coordinates, inclusive
        """
        pass
