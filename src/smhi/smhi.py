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
        """Initialise SMHI class.

        Raises:
            ValueError
        """
        self.parameters = Parameters()

        if self.parameters is None:
            raise ValueError("No parameters available.")

    def get_stations(self, parameter: Optional[int] = None) -> List[MetobsLinksModel]:
        """Get stations from parameter.

        Args:
            parameter: station parameter

        Returns:
            stations
        """
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
        return Stations(self.parameters, parameter_title=title).data

    def _find_stations_from_gps(
        self,
        station_response: Stations,
        latitude: float,
        longitude: float,
        dist: float = 0,
    ) -> List[Tuple[int, str, float]]:
        """Find stations for parameter from gps location.

        Args:
            parameter: station parameter
            latitude: latitude
            longitude: longitude
            dist: distance from gps location. If zero (default), chooses closest

        Returns:
            nearby stations
        """
        user_pos = (latitude, longitude)
        all_stations = station_response.station
        nearby_stations = [
            (s.id, s.name, distance.distance(user_pos, (s.latitude, s.longitude)).km)
            for s in all_stations
        ]

        if dist == 0:
            return min(nearby_stations, key=lambda x: x[2])

        nearby_stations = [x for x in nearby_stations if x[2] <= dist]

        return sorted(nearby_stations, key=lambda x: x[2])

    def _find_stations_by_city(
        self, station_response: Stations, city: str, dist: float = 0
    ) -> List[Tuple[int, str, float]]:
        """Find stations for parameter from city name.

        Args:
            parameter: station parameter
            dist: distance from city in km
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
            distance: station distance in km

        Returns:
            data
        """
        stations = Stations(Parameters(), parameter)
        periods = Periods(stations, station)
        data = Data(periods)

        return self._interpolate(distance, stations, periods, data)

    def get_data_by_city(
        self,
        parameter: int,
        city: str,
        distance: int = 0,
    ) -> Tuple[Any, Any]:
        """Get data from station.

        Args:
            parameter: data parameter
            city: user provided city
            distance: station distance in km

        Returns:
            data
        """
        stations = Stations(Parameters(), parameter)
        station = self._find_stations_by_city(stations, city, distance)[0]
        periods = Periods(stations, station[0])
        data = Data(periods)

        return self._interpolate(distance, stations, periods, data)

    def _interpolate(
        self, distance: float, stations: Stations, periods: Periods, data: Data
    ) -> Data:
        """Interpolate data from several stations based on allowed distance."""
        if distance > 0:
            lat, lon = (periods.position[0].latitude, periods.position[0].longitude)
            df = data.df
            df_index = df.index.to_series()

            condition = df_index.diff() > df_index.diff().median()
            holes_to_fill = df[condition]

            all_nearby_stations = self._find_stations_from_gps(
                stations, lat, lon, distance
            )

            for nearby_station in all_nearby_stations[1:]:
                nearby_data = Data(Periods(stations, nearby_station[0]))
                df = self._iterate_time(df, nearby_data.df, holes_to_fill)

                holes_to_fill = df[condition]

        data.df = df.sort_index()

        return data

    def _iterate_time(
        self, df: pd.DataFrame, nearby_df: pd.DataFrame, holes_to_fill: pd.DataFrame
    ) -> pd.DataFrame:
        """Iterate over time."""
        for time, _ in holes_to_fill.iterrows():
            earliertime = df[df.index < time].index.max()
            condition = (nearby_df.index > earliertime) & (nearby_df.index < time)

            if len(nearby_df[condition]) > 0:
                df = pd.concat([df, nearby_df], axis=0, join="outer")

        return df
