"""SMHI unit tests."""
from unittest.mock import patch
from smhi.smhi import SMHI
import pytest


class TestUnitSMHI:
    """Unit tests for SMHI class."""

    @patch("smhi.smhi.Metobs")
    def test_unit_smhi_init(self, mock_requests_metobs):
        """Unit test for SMHI init method.

        Args:
            mock_requests_metobs: mock Metobs object
        """
        client = SMHI()

        assert client.type == "application/json"
        mock_requests_metobs.assert_called_once()
        mock_requests_metobs.return_value.get_parameters.assert_called_once()

    @patch("smhi.smhi.Metobs")
    def test_unit_smhi_parameters(self, mock_Metobs):
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
        mock_Metobs.return_value.parameters = Metobs_parameters
        client = SMHI()
        if Metobs_parameters is None:
            client.get_stations(parameter)
            mock_logging_info.assert_called_once()
            return

        stations = client.get_stations(parameter)
        assert stations == mock_Metobs.return_value.stations.data
