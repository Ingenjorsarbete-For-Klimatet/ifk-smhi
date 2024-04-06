"""Read SMHI data."""

import logging
from typing import Any, List, Optional, Tuple

import pandas as pd
from geopy import distance
from geopy.geocoders import Nominatim
from smhi.metobs import Data, Parameters, Periods, Stations, Versions


class SMHI:
    """SMHI class with high-level functions."""

    def __init__(self, type: str = "json", version: str = "1.0") -> None:
        """Initialise SMHI class.

        Args:
            type: API type
            version: API version
        """
        self.versions = Versions()
        self.parameters = Parameters(self.versions)

    def get_stations(self, parameter: Optional[int] = None):
        """Get stations from parameter.

        Args:
            parameter: station parameter

        Returns:
            stations
        """
        if self.parameters is None:
            logging.info("No parameters available.")
            return None

        self.stations = Stations(self.parameters, parameter)
        return self.stations.data

    def get_stations_from_title(self, title: Optional[str] = None):
        """Get stations from title.

        Args:
            title: station title

        Returns:
            stations
        """
        if self.stations is None:
            logging.info("No stations available.")
            return None

        self.stations = Stations(self.parameters, title)
        return self.stations.data

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
        self.stations = Stations(self.parameters, parameter)
        self.nearby_stations: List[Tuple[Any, Any, Any]]
        all_stations = self.stations.stations
        if dist == 0:
            stations = [
                (
                    s.id,
                    s.name,
                    distance.distance(user_position, (s.latitude, s.longitude)).km,
                )
                for s in all_stations
            ]
            self.nearby_stations = min(stations, key=lambda x: x[2])

        else:
            self.nearby_stations = [
                (
                    s.id,
                    s.name,
                    distance.distance(user_position, (s.latitude, s.longitude)).km,
                )
                for s in all_stations
                if distance.distance(user_position, (s.latitude, s.longitude)) <= dist
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
        self.stations = Stations(Parameters(Versions()), parameter)
        self.periods = Periods(self.stations, station)
        data = Data(self.periods)
        if interpolate > 0:
            # Find the station latitude and longitude information from Metobs
            # should be replaced by a self.periods.position[0].latitude
            stat = next(item for item in self.stations.station if item.id == station)
            latitude = stat.latitude
            longitude = stat.longitude

            holes_to_fill = data.df[
                data.df.index.to_series().diff()
                > data.df.index.to_series().diff().median()
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
                tmpdata = Data(Periods(self.stations, station))
                for time, _ in holes_to_fill.iterrows():
                    earliertime = data.df[data.df.index < time].index.max()

                    if (
                        len(
                            tmpdata.df[
                                (tmpdata.df.index > earliertime)
                                & (tmpdata.df.index < time)
                            ]
                        )
                        > 0
                    ):
                        data.df = pd.concat([data.df, tmpdata.df], axis=0, join="outer")

                # Re-check how many holes remain
                holes_to_fill = data.df[
                    data.df.index.to_series().diff()
                    > data.df.index.to_series().diff().median()
                ]
        data.df = data.df.sort_index()
        return data
