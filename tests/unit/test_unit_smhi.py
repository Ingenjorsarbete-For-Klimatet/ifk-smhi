"""SMHI unit tests."""
from unittest.mock import patch
from smhi.smhi import SMHI
import pytest
import pandas as pd


class TestUnitSMHI:
    """Unit tests for SMHI class."""

    @patch("smhi.smhi.Metobs")
    def test_unit_smhi_init(self, mock_requests_metobs):
        """Unit test for SMHI init method.

        Args:
            mock_requests_metobs: mock requests metobs object
        """
        client = SMHI()

        assert client.type == "application/json"
        mock_requests_metobs.assert_called_once()
        mock_requests_metobs.return_value.get_parameters.assert_called_once()

    @patch("smhi.smhi.Metobs")
    def test_unit_smhi_parameters(self, mock_Metobs):
        """Unit test for SMHI parameters method.

        Args:
            mock_Metobs: mock Metobs object
        """
        client = SMHI()
        assert client.parameters == mock_Metobs.return_value.parameters.data

    @pytest.mark.parametrize(
        "parameter,Metobs_parameters",
        [(None, None), (1, [(2, 0), (3, 0)]), (2, [(2, 0)])],
    )
    @patch("smhi.smhi.Metobs")
    @patch("smhi.smhi.logging.info")
    def test_unit_smhi_get_stations(
        self, mock_logging_info, mock_Metobs, parameter, Metobs_parameters
    ):
        """Unit test for SMHI get_stations method.

        Args:
            mock_logging_info: mock logging info object
            mock_Metobs: mock Metobs object
            parameter: parameter (int)
            Metobs_parameters: Metobs return parameters
        """
        mock_Metobs.return_value.parameters = Metobs_parameters
        client = SMHI()
        if Metobs_parameters is None:
            client.get_stations(parameter)
            mock_logging_info.assert_called_once()
            return

        stations = client.get_stations(parameter)
        assert stations == mock_Metobs.return_value.stations.data

    @pytest.mark.parametrize(
        "title,Metobs_stations",
        [
            (None, None),
            (
                "Göteborg",
                pd.DataFrame({"stations": "Göteborg", "data": [(2, 0), (3, 0)]}),
            ),
        ],
    )
    @patch("smhi.smhi.Metobs")
    @patch("smhi.smhi.logging.info")
    def test_unit_smhi_get_stations_from_title(
        self, mock_logging_info, mock_Metobs, title, Metobs_stations
    ):
        """Unit test for SMHI get_stations_from_title method.

        Args:
            title: title of station
        """
        mock_Metobs.return_value.stations = Metobs_stations
        client = SMHI()
        if Metobs_stations is None:
            client.get_stations_from_title(title)
            mock_logging_info.assert_called_once()
            return

        data = client.get_stations_from_title(title)
        assert (data == mock_Metobs.return_value.stations.data).all()

    @pytest.mark.parametrize(
        "parameter,latitude,longitude,dist,Metobs_stations",
        [
            (None, None, None, None, None),
            (
                1,
                15,
                72,
                0,
                pd.DataFrame(
                    {
                        "stations": [
                            pd.DataFrame(
                                {
                                    "id": [1],
                                    "name": ["Göteborg"],
                                    "latitude": [57.708870],
                                    "longitude": [11.974560],
                                }
                            )
                        ],
                        "data": [(2, 0)],
                    }
                ),
            ),
        ],
    )
    @patch("smhi.smhi.distance.distance")
    @patch("smhi.smhi.Metobs")
    @patch("smhi.smhi.logging.info")
    def test_find_stations_from_gps(
        self,
        mock_logging_info,
        mock_Metobs,
        mock_distance,
        parameter,
        latitude,
        longitude,
        dist,
        Metobs_stations,
    ):
        """Unit test for SMHI find_stations_from_gps method.

        Args:
            mock_logging_info: mock logging info object
            mock_Metobs: mock Metobs object
            mock_distance: mock distance object
            parameter: parameter (int)
            latitude: latitude (int)
            longitude: longitude (int)
            dist: Distance radius in which to look for stations
            Metobs_stations: Metobs stations
        """
        mock_Metobs.return_value.stations = Metobs_stations
        client = SMHI()

        if parameter is None:
            client.find_stations_from_gps(parameter, latitude, longitude)
            mock_logging_info.assert_called_once()
            return
        else:
            client.find_stations_from_gps(parameter, latitude, longitude, dist)
            mock_distance.assert_called()
            assert len(client.nearby_stations[0]) > 0

    @pytest.mark.parametrize(
        "parameter,city,dist,Metobs_stations",
        [
            (None, None, None, None),
            (
                1,
                "Göteborg",
                0,
                pd.DataFrame(
                    {
                        "stations": [
                            pd.DataFrame(
                                {
                                    "id": [1],
                                    "name": ["Göteborg"],
                                    "latitude": [57.708870],
                                    "longitude": [11.974560],
                                }
                            )
                        ],
                        "data": [(2, 0)],
                    }
                ),
            ),
        ],
    )
    @patch("smhi.smhi.distance.distance")
    @patch("smhi.smhi.Nominatim")
    @patch("smhi.smhi.Metobs")
    def test_find_stations_by_city(
        self,
        mock_Metobs,
        mock_Nominatim,
        mock_distance,
        parameter,
        city,
        dist,
        Metobs_stations,
    ):
        """Unit test for SMHI find_stations_by_city method.

        Args:
            mock_Metobs: mock Metobs object
            mock_Nominatim: mock Nominatim object
            mock_distance: mock distance object
            parameter: parameter (int)
            city: city name
            dist: Distance radius in which to look for stations
            Metobs_stations: Metobs stations
        """
        mock_Metobs.return_value.stations = Metobs_stations
        client = SMHI()
        client.find_stations_by_city(parameter, city, dist)
        mock_Nominatim.assert_called_once()
