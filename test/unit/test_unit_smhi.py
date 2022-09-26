"""
SMHI unit tests.
"""

from unittest.mock import patch
from smhi.metobs import MetObs


class TestUnitMetObs:
    """
    Unit tests for SMHI class.
    """

    @patch("smhi.MetObs.requests.get")
    @patch("smhi.MetObs.json.loads")
    def test_unit_smhi_init(self, mock_requests_get, mock_json_loads):
        """
        Unit test for MetObs init method.

        Args:
            mock_requests_get: mock requests get method
            mock_json_loads: mock json loads method
        """
        client = MetObs()

        assert client.type == "application/json"
        mock_requests_get.assert_called_once()
        mock_json_loads.assert_called_once()
