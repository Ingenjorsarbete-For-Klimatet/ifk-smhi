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
        self.versions = json.loads(response.content)["version"]

    def select_version(self, version: Union[str, int] = "latest"):
        """
        Select version of SMHI API to read.

        Args:
            version: selected API version
        """
        requested_version = [x for x in self.versions if x["key"] == version][0]
        url = [x["href"] for x in requested_version["link"] if x["type"] == self.type][
            0
        ]

        response = self.session.get(url)
        self.parameters = json.loads(response.content)["resource"]
        self.parameters_key = tuple((x["key"], x["title"]) for x in self.parameters)

    def select_parameter(self, parameter: str, parameter_title: str = None):
        """
        Select the data to read, also called parameter.

        Args:
            parameter: data to read
            parameter_title: exact title of data
        """
        if parameter_title is not None:
            requested_version = [
                x for x in self.parameters if x["title"] == parameter_title
            ][0]
        else:
            requested_version = [
                x for x in self.parameters if x["key"] == str(parameter)
            ][0]
        url = [x["href"] for x in requested_version["link"] if x["type"] == self.type][
            0
        ]

        response = self.session.get(url)
        response_content = json.loads(response.content)
        self.station_sets = response_content["stationSet"]
        self.stations = response_content["station"]

    def select_station(self, station: int, station_name: str = None):
        """
        Selection station.

        Args:
            station: station id, not key
            station_name: station name
        """
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

        response = self.session.get(url)
        self.period = json.loads(response.content)["period"]

    def select_station_set(self, station_set: int):
        if self.station_set is None:
            raise Exception("Station set is empty, try station.")

    def select_period(self, period: str = "corrected-archive"):
        """
        Select period of data.

        Args:
            period: select period from: latest-hour, latest-day, latest-months or corrected-archive
        """
        requested_period = [x for x in self.period if x["key"] == period][0]
        url = [x["href"] for x in requested_period["link"] if x["type"] == self.type][0]

        response = self.session.get(url)
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
                self.data.append(self.session.get(url).content)

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
