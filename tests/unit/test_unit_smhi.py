"""SMHI unit tests."""
from unittest.mock import patch
from smhi.smhi import SMHI


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
