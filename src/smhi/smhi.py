"""Read SMHI data."""
from geopy import distance
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
        self.client.fetch_parameters(version)

    @property
    def parameters(self):
        """Get available parameters.

        Returns:
            parameters
        """
        return self.client.parameter.data

    def get_stations(self, parameter: str = None):
        """Get stations from parameter.

        Args:
            parameter: station parameter

        Returns:
            stations
        """
        self.client.fetch_stations(parameter)
        return self.client.station.data

    def get_stations_from_title(self, title: str = None):
        """Get stations from title.

        Args:
            title: station title

        Returns:
            stations
        """
        self.client.fetch_stations(None, title)
        return self.client.station.data

    def find_stations_from_gps(
        self, parameter: int, dist: float, latitude: float, longitude: float
    ) -> None:
        """Find stations for parameter from gps location.

        Args:
            parameter: station parameter
            dist: distance from gps location
            latitude: latitude
            longitude: longitude
        """
        user_position = (latitude, longitude)
        self.get_stations(parameter)
        self.d = []

        all_stations = self.client.station.station
        self.d = [
            s
            for s in all_stations
            if distance.distance(user_position, (s["latitude"], s["longitude"])) <= dist
        ]
