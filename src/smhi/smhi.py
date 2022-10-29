"""
Read SMHI data.
"""
from typing import Union
from geopy import distance
from smhi.metobs import MetObs
from smhi.constants import TYPE_MAP


class SMHI:
    """
    SMHI class with high-level functions.
    """

    def __init__(self, type: str = "json", version: str = "1.0"):
        self.type = TYPE_MAP[type]
        self.client = MetObs(type)
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

        all_stations = self.client.station.station
        self.d = [
            s
            for s in all_stations
            if distance.distance(user_position, (s["latitude"], s["longitude"])) <= dist
        ]
