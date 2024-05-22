"""Read SMHI data."""

import logging
import time
from typing import Any, List, Optional, Tuple

import pandas as pd
from geopy import distance
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from smhi.metobs import Data, Parameters, Periods, Stations
from smhi.models.metobs_model import MetobsLinks

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

    def get_stations(self, parameter: Optional[int] = None) -> List[MetobsLinks]:
        """Get stations from parameter.

        Args:
            parameter: station parameter

        Returns:
            stations
        """
        return Stations(self.parameters, parameter).data

    def get_stations_from_title(self, title: Optional[str] = None) -> List[MetobsLinks]:
        """Get stations from title.

        Args:
            title: station title

        Returns:
            stations
        """
        return Stations(self.parameters, parameter_title=title).data

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
            distance: station distance in km (for interpolation)

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
        station = self._find_stations_by_city(stations, city, distance)[0][0]
        periods = Periods(stations, station)
        data = Data(periods)

        return self._interpolate(distance, stations, periods, data)

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
        if not dist:
            dist = 0

        user_pos = (latitude, longitude)
        all_stations = station_response.station
        nearby_stations = [
            (s.id, s.name, distance.distance(user_pos, (s.latitude, s.longitude)).km)
            for s in all_stations
        ]

        if dist == 0:
            return [min(nearby_stations, key=lambda x: x[2])]

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
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        loc = geocode(city)

        return self._find_stations_from_gps(
            station_response, latitude=loc.latitude, longitude=loc.longitude, dist=dist
        )

    def _interpolate(
        self, distance: float, stations: Stations, periods: Periods, data: Data
    ) -> Data:
        """Interpolate data from several stations based on allowed distance."""
        if not distance:
            return data

        if distance <= 0:
            return data

        lat, lon = (periods.position[0].latitude, periods.position[0].longitude)
        missing_df = self._find_missing_data(data.df)
        all_nearby_stations = self._find_stations_from_gps(stations, lat, lon, distance)

        for nearby_station in all_nearby_stations[1:]:
            time.sleep(1)
            nearby_data = Data(Periods(stations, nearby_station[0]))
            data.df = self._iterate_over_time(data.df, nearby_data.df, missing_df)
            missing_df = self._find_missing_data(data.df)

        data.df = data.df.sort_index()

        return data

    def _iterate_over_time(
        self, df: pd.DataFrame, nearby_df: pd.DataFrame, missing_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Iterate over time."""
        for tajm, _ in missing_df.iterrows():
            earliertime = df[df.index < tajm].index.max()
            condition = (nearby_df.index > earliertime) & (nearby_df.index < tajm)

            if len(nearby_df[condition]) > 0:
                df = pd.concat([df, nearby_df], axis=0, join="outer")

        return df

    def _find_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Find missing data."""
        return df[df.index.to_series().diff() > df.index.to_series().diff().median()]
