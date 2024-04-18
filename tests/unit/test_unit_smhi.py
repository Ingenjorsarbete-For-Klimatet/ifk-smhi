"""SMHI unit tests."""

from unittest.mock import patch

import pytest
from smhi.smhi import SMHI


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

    def test_find_stations_from_gps(
        self,
    ):
        """Unit test for SMHI find_stations_from_gps method.

        Args:
        """
        assert True

    def test_find_stations_by_city(
        self,
    ):
        """Unit test for SMHI find_stations_by_city method.

        Args:
        """
        assert True
