"""
SMHI unit tests.
"""

from unittest.mock import patch
from smhi.smhi import SMHI


class TestUnitSMHI:
    """
    Unit tests for SMHI class.
    """

    @patch("smhi.smhi.requests.get")
    @patch("smhi.smhi.json.loads")
    def test_unit_smhi_init(self, mock_requests_get, mock_json_loads):
        """
        Unit test for SMHI init method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
        """
        smhi = SMHI()

        assert smhi.type == "application/json"
        mock_requests_get.assert_called_once()
        mock_json_loads.assert_called_once()
