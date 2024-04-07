"""Read SMHI data."""

import logging
from typing import Any, List, Optional, Tuple

import pandas as pd
from geopy import distance
from geopy.geocoders import Nominatim
from smhi.metobs import Data, Parameters, Periods, Stations
from smhi.models.metobs_model import MetobsLinksModel

logger = logging.getLogger(__name__)


class SMHI:
    """SMHI class with high-level functions."""

    def __init__(self) -> None:
        """Initialise SMHI class."""
        self.parameters = Parameters()

    def get_stations(self, parameter: Optional[int] = None) -> List[MetobsLinksModel]:
        """Get stations from parameter.

        Args:
            parameter: station parameter

        Returns:
            stations
        """
        if self.parameters is None:
            logger.info("No parameters available.")
            return None

        return Stations(self.parameters, parameter).data

    def get_stations_from_title(
        self, title: Optional[str] = None
    ) -> List[MetobsLinksModel]:
        """Get stations from title.

        Args:
            title: station title

        Returns:
            stations
        """
        if self.stations is None:
            logging.info("No stations available.")
            return None

        return Stations(self.parameters, title).data

    def _find_stations_from_gps(
        self,
        station_response: Stations,
        latitude: float,
        longitude: float,
        dist: float = 0,
    ) -> List[Tuple[Any, Any, Any]]:
        """Find stations for parameter from gps location.

        Args:
            parameter: station parameter
            latitude: latitude
            longitude: longitude
            dist: distance from gps location. If zero (default), chooses closest.

        Returns:
            nearby stations
        """
        user_position = (latitude, longitude)
        all_stations = station_response.station
        if dist == 0:
            stations = [
                (
                    s.id,
                    s.name,
                    distance.distance(user_position, (s.latitude, s.longitude)).km,
                )
                for s in all_stations
            ]
            nearby_stations = min(stations, key=lambda x: x[2])

        else:
            nearby_stations = [
                (
                    s.id,
                    s.name,
                    distance.distance(user_position, (s.latitude, s.longitude)).km,
                )
                for s in all_stations
                if distance.distance(user_position, (s.latitude, s.longitude)) <= dist
            ]
            nearby_stations = sorted(nearby_stations, key=lambda x: x[2])

        return nearby_stations

    def _find_stations_by_city(
        self, station_response: Stations, city: str, dist: float = 0
    ) -> List[Tuple[Any, Any, Any]]:
        """Find stations for parameter from city name.

        Args:
            parameter: station parameter
            dist: distance from city
            city: name of city

        Returns:
            nearby stations
        """
        geolocator = Nominatim(user_agent="ifk-smhi")
        loc = geolocator.geocode(city)
        return self._find_stations_from_gps(
            station_response,
            latitude=loc.latitude,
            longitude=loc.longitude,
            dist=dist,
        )

    def get_data(
        self,
        parameter: int,
        station: int,
        distance: int = 0,
    ) -> Tuple[Any, Any]:
        """Get data from station.

        Args:
            parameter: data parameter
            station: station id
            distance: station distance

        Returns:
            data
        """
        stations = Stations(Parameters(), parameter)
        periods = Periods(stations, station)
        data = Data(periods)

        if distance > 0:
            # Find the station latitude and longitude information from Metobs
            # should be replaced by a self.periods.position[0].latitude
            latitude = periods.position[0].latitude
            longitude = periods.position[0].longitude

            holes_to_fill = data.df[
                data.df.index.to_series().diff()
                > data.df.index.to_series().diff().median()
            ]

            # Find stations within a given radius - set in "distance".
            nearby_stations = self._find_stations_from_gps(
                stations, latitude, longitude, distance
            )

            # Iterate over nearby stations, starting with the closest
            for nearby_station in nearby_stations[1:]:
                tmpdata = Data(Periods(stations, nearby_station[0]))
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
