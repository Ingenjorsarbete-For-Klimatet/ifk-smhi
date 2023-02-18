"""Read SMHI data."""
import logging
import pandas as pd
from geopy.geocoders import Nominatim
from geopy import distance
from typing import Optional, Any, List, Tuple
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
        if parameter is None:
            logging.info("Parameter needed.")
            return None

        user_position = (latitude, longitude)
        self.get_stations(parameter)
        self.nearby_stations: List[Tuple[Any, Any, Any]]
        all_stations = self.client.stations.stations
        if dist == 0:
            stations = [
                (
                    s["id"],
                    s["name"],
                    distance.distance(
                        user_position, (s["latitude"], s["longitude"])
                    ).km,
                )
                for s in all_stations
            ]
            self.nearby_stations = min(stations, key=lambda x: x[2])

        else:
            self.nearby_stations = [
                (
                    s["id"],
                    s["name"],
                    distance.distance(
                        user_position, (s["latitude"], s["longitude"])
                    ).km,
                )
                for s in all_stations
                if distance.distance(user_position, (s["latitude"], s["longitude"]))
                <= dist
            ]
            self.nearby_stations = sorted(self.nearby_stations, key=lambda x: x[2])

    def find_stations_by_city(self, parameter: int, city: str, dist: float = 0) -> None:
        """Find stations for parameter from city name.

        Args:
            parameter: station parameter
            dist: distance from city
            city: name of city
        """
        geolocator = Nominatim(user_agent="ifk-smhi")
        loc = geolocator.geocode(city)
        self.find_stations_from_gps(
            parameter=parameter,
            dist=dist,
            latitude=loc.latitude,
            longitude=loc.longitude,
        )

    def get_data(
        self,
        parameter: int,
        station: int,
        period: str = "corrected-archive",
        interpolate: int = 0,
    ) -> Tuple[Any, Any]:
        """Get data from station.

        Args:
            parameter: data parameter
            station: station id
            period: period to get
        """
        data, header = self.client.get_data_from_selection(
            parameter=parameter, station=station, period=period
        )
        if interpolate > 0:
            # Find the station latitude and longitude information from Metobs
            stat = next(
                item for item in self.client.stations.stations if item["id"] == station
            )
            latitude = stat["latitude"]
            longitude = stat["longitude"]

            holes_to_fill = data[
                data.index.to_series().diff() > data.index.to_series().diff().median()
            ]
            # Find stations within a given radius - set in "interpolate".
            self.find_stations_from_gps(
                parameter=parameter,
                latitude=latitude,
                longitude=longitude,
                dist=interpolate,
            )

            # Iterate over nearby stations, starting with the closest
            for nearby_station in self.nearby_stations[1:]:
                _, tmpdata = self.get_data(parameter, nearby_station[0])
                for time, _ in holes_to_fill.iterrows():
                    earliertime = data[data.index < time].index.max()

                    if (
                        len(
                            tmpdata[
                                (tmpdata.index > earliertime) & (tmpdata.index < time)
                            ]
                        )
                        > 0
                    ):
                        data = pd.concat([data, tmpdata], axis=0, join="outer")

                # Re-check how many holes remain
                holes_to_fill = data[
                    data.index.to_series().diff()
                    > data.index.to_series().diff().median()
                ]
        data = data.sort_index()
        return data, header
