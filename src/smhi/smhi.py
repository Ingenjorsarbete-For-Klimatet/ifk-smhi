"""Read SMHI data."""
import logging
from geopy import distance
from typing import Optional
from smhi.metobs import Metobs
from smhi.constants import TYPE_MAP


class SMHI:
    """SMHI class with high-level functions."""

    def __init__(self, type: str = "json", version: str = "1.0") -> None:
        """Initialise SMHI class.

        Args:
            type: API type
            version: API version
        """
        self.type = TYPE_MAP[type]
        self.client = Metobs(type)
        self.client.get_parameters()

    @property
    def parameters(self):
        """Get available parameters.

        Returns:
            parameters
        """
        return self.client.parameters.data

    def get_stations(self, parameter: Optional[int] = None):
        """Get stations from parameter.

        Args:
            parameter: station parameter

        Returns:
            stations
        """
        if self.client.parameters is None:
            logging.info("No parameters available.")
            return None

        self.client.get_stations(parameter)
        return self.client.stations.data

    def get_stations_from_title(self, title: Optional[str] = None):
        """Get stations from title.

        Args:
            title: station title

        Returns:
            stations
        """
        if self.client.stations is None:
            logging.info("No stations available.")
            return None

        self.client.get_stations(None, title)
        return self.client.stations.data

    def find_stations_from_gps(
        self, parameter: int, latitude: float, longitude: float, dist: float = 0
    ) -> None:
        """Find stations for parameter from gps location.

        Args:
            parameter: station parameter
            latitude: latitude
            longitude: longitude
            dist: distance from gps location. If zero (default), chooses closest.

        """
        if self.client.stations is None:
            logging.info("No stations available.")
            return None

        user_position = (latitude, longitude)
        self.get_stations(parameter)
        self.nearby_stations = []
        all_stations = self.client.stations.stations
        if dist == 0:
            stations = [
                (s['id'], s['name'], distance.distance(
                    user_position, (s["latitude"], s["longitude"])).km)
                for s in all_stations
            ]
            self.nearby_stations = min(stations, key=lambda x: x[2])

        else:
            self.nearby_stations = [
                (s['id'], s['name'], distance.distance(
                    user_position, (s["latitude"], s["longitude"])).km)
                for s in all_stations
                if distance.distance(user_position, (s["latitude"], s["longitude"])) <= dist
            ]
            self.nearby_stations = sorted(self.nearby_stations, key=lambda x: x[2])
