"""SMHI unit tests."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from smhi.smhi import SMHI


class MockMetobsStationLink:
    """Support class to mock MetObs StationLink object."""

    def __init__(self, id: int, name: str, lat: float, lon: float):
        """Initiate parameters."""
        self.id = id
        self.name = name
        self.latitude = lat
        self.longitude = lon


class MockParameterModel:
    """Support class to mock Metobs Parameter object."""

    def __init__(self, station: MockMetobsStationLink):
        """Initiate station."""
        self.station = station


class MockStationModel:
    """Support class to mock Metobs Station object."""

    def __init__(self, data="str"):
        """Initiate data"""
        self.data = data


@pytest.fixture
def setup_iterate_over_time():
    """Iterate over time fixture."""
    df = pd.DataFrame(
        {
            "date": [
                "2024-04-21 10:00",
                "2024-04-21 11:00",
                "2024-04-21 12:00",
                "2024-04-22 12:00",
            ],
            "Temperatur": [1, 1, 1, 12],
        }
    )
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    nearby_df = pd.DataFrame(
        {"date": ["2024-04-22 10:00", "2024-04-22 11:00"], "Temperatur": [8, 9]}
    )
    nearby_df["date"] = pd.to_datetime(nearby_df["date"])
    nearby_df = nearby_df.set_index("date")

    missing_df = df[df.index.to_series().diff() > df.index.to_series().diff().median()]

    return df, nearby_df, missing_df


class TestUnitSMHI:
    """Unit tests for SMHI class."""

    @patch("smhi.metobs.Parameters.__new__", return_value="test")
    def test_unit_smhi_init(self, mock_parameters):
        """Unit test for SMHI init method.

        Args:
            mock_parameters
        """
        client = SMHI()

        assert client.parameters == "test"

    @pytest.mark.parametrize("parameter", [(None), (1)])
    @patch("smhi.metobs.Stations.__new__", return_value=MockStationModel("Test"))
    def test_unit_smhi_get_stations(self, mock_station_data, parameter):
        """Unit test for SMHI get_stations method.

        Args:
            mock_station_data,
            parameter: parameter (int)
        """
        client = SMHI()
        assert client.get_stations(parameter) == "Test"

    @pytest.mark.parametrize("parameter_title", [(None), ("Snöfall")])
    @patch("smhi.metobs.Stations.__new__", return_value=MockStationModel("Test"))
    def test_unit_smhi_get_stations_from_title(
        self, mock_station_data, parameter_title
    ):
        """Unit test for SMHI get_stations_from_title method.

        Args:
            mock_station_data,
            parameter_title: title of parameter
        """
        client = SMHI()
        assert client.get_stations_from_title(parameter_title) == "Test"

    @pytest.mark.parametrize(
        "parameter, station, distance", [(8, 180960, None), (8, 180960, 50)]
    )
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("smhi.smhi.SMHI._interpolate", return_value="test")
    def test_unit_get_data(
        self,
        mock_interpolate,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        parameter,
        station,
        distance,
    ):
        """Unit test for SMHI method get_data

        Args:
            mock_interpolate,
            mock_data_data,
            mock_period_data,
            mock_station_data,
            parameter,
            station,
            distance,
        """
        client = SMHI()
        data = client.get_data(parameter, station, distance)
        assert data == "test"

    @pytest.mark.parametrize(
        "parameter, city, distance", [(8, "Bengtsfors", None), (8, "Bengtsfors", 50)]
    )
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("smhi.smhi.SMHI._find_stations_by_city")
    @patch("smhi.smhi.SMHI._interpolate", return_value="test")
    def test_unit_get_data_by_city(
        self,
        mock_interpolate,
        mock_find_stations_by_city,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        parameter,
        city,
        distance,
    ):
        """Unit test for SMHI _get_data_by_city method.

        args:
            mock_interpolate,
            mock_find_stations_by_city,
            mock_data_data,
            mock_period_data,
            mock_station_data,
            parameter,
            city,
            distance
        """
        client = SMHI()
        data = client.get_data_by_city(parameter, city, distance)
        assert data == "test"

    distanceresponse = MagicMock()
    distanceresponse.km = 0

    @pytest.mark.parametrize(
        "latitude, longitude, dist, expected_result",
        [(59, 17, 0, 1), (59.5, 17.75, 30, 1)],
    )
    def test_find_stations_from_gps(self, latitude, longitude, dist, expected_result):
        """Unit test for SMHI find_stations_from_gps method.

        Args:
            latitude,
            longitude,
            dist
            expected_result
        """
        station1 = MockMetobsStationLink(1, "Akalla", 59.5, 17.8)
        station2 = MockMetobsStationLink(2, "name", 57, 16)
        station3 = MockMetobsStationLink(3, "name", 58, 17)
        stations = MockParameterModel([station1, station2, station3])

        client = SMHI()
        nearby_town = client._find_stations_from_gps(
            stations, latitude, longitude, dist
        )
        assert nearby_town[0][0] == expected_result

    @pytest.mark.parametrize(
        "parameter, city, distance", [(8, "Bengtsfors", None), (8, "Bengtsfors", 50)]
    )
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("geopy.geocoders.Nominatim.__new__")
    @patch("smhi.smhi.SMHI._find_stations_from_gps")
    def test_find_stations_by_city(
        self,
        mock_find_from_gps,
        mock_nominatim,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        parameter,
        city,
        distance,
    ):
        """Unit test for SMHI _find_stations_by_city method.

        Args:
            mock_find_from_gps,
            mock_nominatim,
            mock_data_data,
            mock_period_data,
            mock_station_data,
            parameter,
            city,
            distance
        """
        client = SMHI()
        _ = client._find_stations_by_city(parameter, city, distance)
        mock_nominatim.assert_called_once()
        mock_find_from_gps.assert_called_once()

    @pytest.mark.parametrize("distance", [(0), (50)])
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("smhi.smhi.SMHI._iterate_over_time")
    @patch("smhi.smhi.SMHI._find_missing_data")
    @patch("smhi.smhi.SMHI._find_stations_from_gps")
    def test_interpolate(
        self,
        mock_find_from_gps,
        mock_find_missing_data,
        mock_iterate_over_time,
        mock_data_data,
        mock_period_data,
        mock_station_data,
        distance,
    ):
        """Unit test for SMHI _interpolate method.

        Args:
            mock_find_from_gps,
            mock_find_missing_data,
            mock_iterate_over_time,
            mock_data_data,
            mock_period_data,
            mock_station_data,
            distance
        """
        client = SMHI()
        data = client._interpolate(
            distance, mock_station_data, mock_period_data, mock_data_data
        )
        if distance <= 0:
            assert data == mock_data_data
        else:
            mock_find_from_gps.assert_called_once()

    def test_iterate_over_time(self, setup_iterate_over_time):
        """Unit test for SMHI _iterate_over_time method."""
        df, nearby_df, missing_df = setup_iterate_over_time
        client = SMHI()

        data = client._iterate_over_time(df, nearby_df, missing_df)
        assert data.tail(2).iloc[0]["Temperatur"] == nearby_df.iloc[0]["Temperatur"]

    def test_find_missing_data(self):
        """Unit test for SMHI _find_missing_data method."""
        df = pd.DataFrame(
            {
                "date": [
                    "2024-04-21 10:00",
                    "2024-04-21 11:00",
                    "2024-04-21 12:00",
                    "2024-04-22 12:00",
                ],
                "Temperatur": [1, 1, 1, 12],
            }
        )
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        client = SMHI()

        missingdata = client._find_missing_data(df)
        assert missingdata.iloc[0]["Temperatur"] == df.iloc[-1]["Temperatur"]
