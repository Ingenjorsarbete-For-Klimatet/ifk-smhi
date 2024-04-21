"""SMHI unit tests."""

from unittest.mock import MagicMock, patch
import pytest
from smhi.smhi import SMHI
import pandas as pd


class TestUnitSMHI:
    """Unit tests for SMHI class."""

    @patch("smhi.metobs.Parameters.__new__")
    def test_unit_smhi_init(self, mock_parameters):
        """Unit test for SMHI init method.

        Args:
            mock_requests_metobs: mock requests metobs object
        """
        client = SMHI()

        assert client.parameters

    @pytest.mark.parametrize("parameter", [(None), (1)])
    @patch("smhi.metobs.Stations.__new__")
    def test_unit_smhi_get_stations(self, mock_station_data, parameter):
        """Unit test for SMHI get_stations method.

        Args:
            parameter: parameter (int)
        """
        client = SMHI()
        assert client.get_stations(parameter)

    @pytest.mark.parametrize("parameter_title", [(None), ("Snöfall")])
    @patch("smhi.metobs.Stations.__new__")
    def test_unit_smhi_get_stations_from_title(
        self, mock_station_data, parameter_title
    ):
        """Unit test for SMHI get_stations_from_title method.

        Args:
            title: title of station
        """
        client = SMHI()
        assert client.get_stations_from_title(parameter_title)

    @pytest.mark.parametrize(
        "parameter, station, distance", [(8, 180960, None), (8, 180960, 50)]
    )
    @patch("smhi.metobs.Stations.__new__")
    @patch("smhi.metobs.Periods.__new__")
    @patch("smhi.metobs.Data.__new__")
    @patch("smhi.smhi.SMHI._interpolate")
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
        mock_interpolate.return_value = "test"
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
    @patch("smhi.smhi.SMHI._interpolate")
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
        mock_interpolate.return_value = "test"
        client = SMHI()
        data = client.get_data_by_city(parameter, city, distance)
        assert data == "test"

    @pytest.mark.parametrize(
        "latitude, longitude,dist",
        [
            (
                59,
                17,
                None,
            ),
            (
                59.4,
                17,
                30,
            ),
        ],
    )
    @patch("geopy.distance")
    def test_find_stations_from_gps(self, mock_distance, latitude, longitude, dist):
        """Unit test for SMHI find_stations_from_gps method.

        Args:
        """
        stations = MagicMock()
        stations.station.id.return_value = 1
        stations.station.name.return_value = "Akalla"
        stations.station.latitude.return_value = 59.5
        stations.station.longitude.return_value = 17.8
        mock_distance.distance.return_value = 0
        client = SMHI()
        nearby_town = client._find_stations_from_gps(
            stations, latitude, longitude, dist
        )
        assert nearby_town[0][0] in stations.station.id

    def test_find_stations_by_city(
        self,
    ):
        """Unit test for SMHI find_stations_by_city method.

        Args:
        """
        assert True
