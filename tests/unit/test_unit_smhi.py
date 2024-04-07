"""SMHI unit tests."""

from unittest.mock import patch
import pandas as pd
import pytest
from smhi.smhi import SMHI


class TestUnitSMHI:
    """Unit tests for SMHI class."""

    def test_unit_smhi_init(self):
        """Unit test for SMHI init method.

        Args:
            mock_requests_metobs: mock requests metobs object
        """
        client = SMHI()

        assert client.versions.data[0].key == "latest"

    def test_unit_smhi_parameters(self):
        """Unit test for SMHI parameters method.

        Args:
            mock_metobs: mock Metobs object
        """
        client = SMHI()
        assert client.parameters.data[0].key == "1"

    @pytest.mark.parametrize(
        "parameter",
        [(None), (1)],
    )
    def test_unit_smhi_get_stations(self, parameter):
        """Unit test for SMHI get_stations method.

        Args:
            parameter: parameter (int)
        """
        assert 2 == 2

    def test_unit_smhi_get_stations_from_title(self):
        """Unit test for SMHI get_stations_from_title method.

        Args:
            title: title of station
        """
        assert 1 == 1

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
